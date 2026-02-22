from redis import Redis
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)

def cache_get(key: str):
    value = redis_client.get(key)
    return json.loads(value) if value else None

def cache_set(key, value, expire_seconds=10):
    redis_client.set(key, json.dumps(value), ex=expire_seconds)

def delete_pattern(pattern: str):
    keys = redis_client.keys(pattern)
    for k in keys:
        redis_client.delete(k)


redis_client = redis_client
redis_client.get_cache = cache_get
redis_client.set_cache = cache_set
redis_client.delete_pattern = delete_pattern