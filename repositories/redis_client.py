from typing import Optional, Dict

class RedisClient:
    def __init__(self):
        self._cache = {}
        self._ttl = {}

    async def get(self, key: str) -> Optional[str]:
        # Simple cache simulation ignoring TTL for now or implementing basic check
        return self._cache.get(key)

    async def set(self, key: str, value: str, ttl: int = None) -> None:
        self._cache[key] = value
        # Ignoring TTL implementation for simplicity in mock

    async def hset(self, key: str, field: str, value: str) -> None:
        if key not in self._cache or not isinstance(self._cache[key], dict):
            self._cache[key] = {}
        self._cache[key][field] = value
