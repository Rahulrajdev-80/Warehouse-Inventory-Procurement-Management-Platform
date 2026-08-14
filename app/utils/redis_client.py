import redis.asyncio as aioredis
import json
from typing import Optional, Any
from app.config import settings

class RedisManager:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def init(self):
        try:
            self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception:
            self.redis = None

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, expire: int = 300):
        if not self.redis:
            return
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except Exception:
            pass

    async def delete(self, key: str):
        if not self.redis:
            return
        try:
            await self.redis.delete(key)
        except Exception:
            pass

    async def publish(self, channel: str, message: dict):
        if not self.redis:
            return
        try:
            await self.redis.publish(channel, json.dumps(message))
        except Exception:
            pass

redis_client = RedisManager()
