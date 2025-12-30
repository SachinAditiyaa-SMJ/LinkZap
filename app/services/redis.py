import os
from typing import Optional

import redis.asyncio as redis

redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """
    Initialize and configure the global Redis client for the application.

    This function should be called once during app startup. It sets up the
    global Redis connection using environment variables for host, port, and db.
    After establishing the connection, it initializes the URL counter in Redis.

    Returns:
        None
    """
    global redis_client
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        db=int(os.getenv("REDIS_DB")),
        decode_responses=True,
    )


async def get_redis() -> redis.Redis:
    """
    Retrieve the global Redis client instance.

    Raises:
        RuntimeError: If the Redis client has not been initialized.

    Returns:
        redis.Redis: The global Redis client instance.
    """
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client
