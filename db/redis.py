import json

import redis.asyncio as redis
from config.config_loader import db_settings

JTI_EXPIRY = 3600

redis_client = redis.Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=0
)


async def add_jti_to_blocklist(jti: str) -> None:
    await redis_client.set(
        name=jti,
        value=jti,
        ex=JTI_EXPIRY,
    )


async def token_in_blocklist(jti: str) -> bool:
    jti = await redis_client.get(name=jti)

    return jti is not None


# Cache keys
def user_key(username: str): return f"user:{username}"


def notes_key(username: str): return f"notes:{username}"


def labels_key(username: str): return f"labels:{username}"


# User cache operations
async def cache_user_data(username: str, user_data: dict):
    await redis_client.set(user_key(username), json.dumps(user_data,default=str))


async def get_cached_user(username: str):
    data = await redis_client.get(user_key(username))
    return json.loads(data) if data else None


# Notes cache
async def cache_user_notes(username: str, notes: list[dict]):
    await redis_client.set(notes_key(username), json.dumps(notes,default=str))


async def get_cached_notes(username: str):
    data = await redis_client.get(notes_key(username))
    return json.loads(data) if data else []


# Labels cache
async def cache_user_labels(username: str, labels: list[dict]):
    await redis_client.set(labels_key(username), json.dumps(labels,default=str))


async def get_cached_labels(username: str):
    data = await redis_client.get(labels_key(username))
    return json.loads(data) if data else []


# Clear all
async def clear_user_cache(username: str):
    await redis_client.delete(user_key(username), notes_key(username),
                              labels_key(username))
