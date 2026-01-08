import time
from fastapi import HTTPException, Request,Depends
from app.core.redis import redis_client
from app.core.config import settings
from app.core.redis import redis_client

DEFAULT_RATE_LIMIT = settings.rate_limit_per_minute  # req/hour
WINDOW = 3600

def _config_key(api_key: str) -> str:
    return f"apikey_rl:{api_key}"


def set_api_rate_limit(api_key: str, limit_per_hour: int):
    redis_client.set(_config_key(api_key), limit_per_hour)


def get_api_rate_limit(api_key: str) -> int:
    limit = redis_client.get(_config_key(api_key))
    return int(limit) if limit else DEFAULT_RATE_LIMIT


import time
from fastapi import HTTPException
from app.core.redis import redis_client

def rate_limit_hourly(api_key: str, endpoint: str):
    limit = get_api_rate_limit(api_key)

    now = int(time.time())
    window = now // WINDOW

    redis_key = f"ratelimit:{api_key}:{endpoint}:{window}"
    count = redis_client.incr(redis_key)
    if count == 1:
        redis_client.expire(redis_key, WINDOW)

    if count > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded ({limit} req/hour)",
        )
    
