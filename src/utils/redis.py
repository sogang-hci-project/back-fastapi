import aioredis
from src.utils.common import throw_exception

redis = aioredis.from_url("redis://localhost")


class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


async def initialize():
    res = await redis.ping()
    if res == False:
        throw_exception("Redis initialization failed", 500)
