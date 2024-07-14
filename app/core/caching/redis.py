import redis.asyncio as redis

from core.config import get_config
from core.logger import logger

config = get_config()


class RedisClient:

    redis_client = None

    def __init__(self):
        """
        Creates the redis client
        """
        self.redis_client = redis.Redis(host=config.redis.host, port=config.redis.port, decode_responses=True)

    async def get_cache(self, key: str) -> str | None:
        """
        This method returns the value from the cache. If not available, returns None
        """
        try:
            value = await self.redis_client.get(key)
            return value
        except redis.ConnectionError as er:
            logger.info(f"Redis error - {er}")

    async def set_cache(self, key: str, value: str, expire: int = 300):
        """
        This method stores the value in cache with ttl 300 seconds
        """
        try:
            await self.redis_client.set(key, value, ex=expire)
        except redis.ConnectionError as er:
            logger.info(f"Redis error - {er}")

    async def unset_cache(self, key: str):
        """
        This method deletes the value from the cache
        """
        try:
            await self.redis_client.delete(key)
        except redis.ConnectionError as er:
            logger.info(f"Redis error - {er}")

