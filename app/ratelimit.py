import os
import time
from upstash_redis import Redis
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

REQUESTS_PER_MINUTE = 10

def check_rate_limit(api_key: str):
    now = int(time.time() * 1000)  # milliseconds
    window_start = now - 60000     # 60 seconds ago in ms
    key = f"ratelimit:{api_key}"

    redis.zadd(key, {str(now): now})
    redis.zremrangebyscore(key, 0, window_start)
    count = redis.zcard(key)
    redis.expire(key, 60)

    if count > REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {REQUESTS_PER_MINUTE} requests per minute."
        )