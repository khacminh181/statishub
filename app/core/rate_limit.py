# app/core/rate_limit.py

import time
from fastapi import HTTPException, Request,Depends
from app.core.redis import redis_client
from app.core.config import settings
from app.core.auth import verify_api_key



DEFAULT_LIMIT = settings.rate_limit_per_minute
DEFAULT_WINDOW = 3600


def rate_limit_hourly(
    api_key: str,
    endpoint: str,
    limit: int = DEFAULT_LIMIT,
    window: int = DEFAULT_WINDOW,
):
    now = int(time.time())
    window_key = now // window

    redis_key = f"ratelimit:{api_key}:{endpoint}:{window_key}"

    count = redis_client.incr(redis_key)

    if count == 1:
        redis_client.expire(redis_key, window)

    if count > limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded (60 requests/hour)",
        )
    

def hourly_rate_limit_dep(limit: int = 60):
    def _dep(
        request: Request,
        api_key=Depends(verify_api_key),
    ):
        rate_limit_hourly(
            api_key=api_key["api_key"],
            endpoint=request.url.path,
            limit=limit,
            window=3600,
        )
        return api_key

    return _dep
