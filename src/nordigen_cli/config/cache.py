import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


class CacheStrategy(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        pass

    @abstractmethod
    def invalidate(self, key: Optional[str] = None) -> None:
        """Invalidate single key or entire cache"""
        pass


class NoCache(CacheStrategy):
    """Strategy that doesn't cache anything"""

    def get(self, key: str) -> Optional[Any]:
        return None

    def set(self, key: str, value: Any) -> None:
        pass

    def invalidate(self, key: Optional[str] = None) -> None:
        pass


class InMemoryCache(CacheStrategy):
    """Simple dictionary-based cache"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def invalidate(self, key: Optional[str] = None) -> None:
        if key is None:
            self._cache.clear()
        else:
            self._cache.pop(key, None)


@dataclass
class CacheEntry:
    value: Any
    timestamp: float


class TTLCache(CacheStrategy):
    """Cache with time-based expiration"""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, CacheEntry] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry is None:
            return None

        if time.time() - entry.timestamp > self.ttl_seconds:
            self.invalidate(key)
            return None

        return entry.value

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = CacheEntry(value=value, timestamp=time.time())

    def invalidate(self, key: Optional[str] = None) -> None:
        if key is None:
            self._cache.clear()
        else:
            self._cache.pop(key, None)
