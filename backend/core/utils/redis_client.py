import redis
from core.config import settings

# Create Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

def get_redis_client():
    """Returns the Redis client instance."""
    return redis_client
