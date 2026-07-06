import asyncio
import time
import uuid
from typing import Any

import httpx

from config.logging import logger
from config.settings import settings
from pixverse.auth import PixVerseAuth
from pixverse.exceptions import (
    PixVerseAPIError,
    PixVerseAuthError,
    PixVerseRateLimitError,
)


class PixVerseClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        retries: int | None = None,
    ):
        self.api_key = api_key or settings.pixverse.api_key
        self.base_url = base_url or settings.pixverse.base_url
        self.timeout = timeout or settings.pixverse.timeout
        self.retries = retries if retries is not None else settings.pixverse.retries

        self.auth = PixVerseAuth(self.api_key)

        # Connection pooling
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        self.http_client = httpx.AsyncClient(limits=limits, timeout=self.timeout)

    async def close(self):
        await self.http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        request_id = str(uuid.uuid4())
        headers = self.auth.get_headers(request_id)

        attempt = 0
        backoff = 1.0

        while True:
            attempt += 1
            start_time = time.perf_counter()
            error_msg = None
            status_code = None

            try:
                response = await self.http_client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params,
                )
                status_code = response.status_code
                duration = time.perf_counter() - start_time

                # Log success request
                logger.info(
                    "API request completed",
                    request_id=request_id,
                    endpoint=path,
                    duration=duration,
                    status=status_code,
                    attempt=attempt,
                )

                if response.status_code == 429:
                    raise PixVerseRateLimitError(
                        "Rate limit exceeded", 429, response.text, request_id
                    )
                elif response.status_code in (401, 403):
                    raise PixVerseAuthError(
                        "Authentication failure",
                        response.status_code,
                        response.text,
                        request_id,
                    )
                elif response.status_code >= 400:
                    raise PixVerseAPIError(
                        f"HTTP Error {response.status_code}",
                        response.status_code,
                        response.text,
                        request_id,
                    )

                return response.json()

            except (httpx.HTTPError, PixVerseRateLimitError) as e:
                duration = time.perf_counter() - start_time
                error_msg = str(e)

                logger.error(
                    "API request failed",
                    request_id=request_id,
                    endpoint=path,
                    duration=duration,
                    status=status_code,
                    attempt=attempt,
                    error=error_msg,
                )

                if attempt > self.retries:
                    if isinstance(e, PixVerseRateLimitError):
                        raise
                    raise PixVerseAPIError(
                        f"Request failed: {error_msg}",
                        status_code or 500,
                        request_id=request_id,
                    ) from e

                sleep_time = backoff * (2 ** (attempt - 1))
                logger.warn(
                    f"Retrying request in {sleep_time:.2f}s due to error: {error_msg}"
                )
                await asyncio.sleep(sleep_time)
