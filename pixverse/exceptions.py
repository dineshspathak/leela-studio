class PixVerseError(Exception):
    """Base exception for PixVerse SDK."""

    pass


class PixVerseAPIError(PixVerseError):
    """Exception raised for errors returned from PixVerse API."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: str = "",
        request_id: str = "",
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.request_id = request_id


class PixVerseRateLimitError(PixVerseAPIError):
    """Exception raised when PixVerse API returns 429 Rate Limit."""

    pass


class PixVerseAuthError(PixVerseAPIError):
    """Exception raised when authentication fails."""

    pass


class PixVerseTaskError(PixVerseError):
    """Exception raised when a video generation job fails or
    content moderation fails.
    """

    def __init__(self, message: str, video_id: str, status: int):
        super().__init__(message)
        self.video_id = video_id
        self.status = status


class PixVerseTimeoutError(PixVerseError):
    """Exception raised when a operation times out."""

    pass
