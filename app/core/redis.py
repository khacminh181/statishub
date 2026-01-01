import redis
import os

host = os.getenv("REDIS_HOST")
port = os.getenv("REDIS_PORT")
db = os.getenv("REDIS_DB")

redis_client = redis.Redis(
    host=host,
    port=port,
    db=db,
    decode_responses=True
)