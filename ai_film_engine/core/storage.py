from abc import ABC, abstractmethod
from pathlib import Path


class BaseStorage(ABC):
    @abstractmethod
    def read_bytes(self, path: str) -> bytes:
        pass

    @abstractmethod
    def write_bytes(self, path: str, data: bytes):
        pass


class LocalStorage(BaseStorage):
    def read_bytes(self, path: str) -> bytes:
        return Path(path).read_bytes()

    def write_bytes(self, path: str, data: bytes):
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)


class MockS3Storage(BaseStorage):
    def __init__(self):
        self.bucket: dict[str, bytes] = {}

    def read_bytes(self, path: str) -> bytes:
        if path not in self.bucket:
            raise FileNotFoundError(f"S3 object {path} not found")
        return self.bucket[path]

    def write_bytes(self, path: str, data: bytes):
        self.bucket[path] = data
