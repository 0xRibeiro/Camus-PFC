from redis.asyncio import Redis

from app.core.config import settings

# objeto cliente redis universal

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
