import secrets

from redis.asyncio import Redis

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


async def init_counter(redis_client: Redis, counter_key: str) -> None:
    """
    Initialize the Redis URL counter with a random starting offset, if it doesn't already exist.

    This function ensures the counter does not start from a predictable value like 0 or 1
    by initializing it to a random value between 1,000,000,000 and 9,999,999,999.
    Should be called only once on app startup.

    Returns:
        None
    """
    exists = await redis_client.exists(counter_key)
    if not exists:
        # e.g. somewhere between 1B and 10B
        start = secrets.randbelow(9_000_000_000) + 1_000_000_000
        await redis_client.set(counter_key, start)


def _encode_base62(num: int, length: int = 7) -> str:
    """
    Encode an integer into a base62 string with a minimum specified length.

    Args:
        num (int): The integer to encode.
        length (int, optional): Minimum length of the encoded string; pads with leading zero-character if needed. Defaults to 7.

    Returns:
        str: The base62-encoded string representation of the number, left-padded to the desired length.
    """
    if num == 0:
        return BASE62_ALPHABET[0] * length

    chars = []
    while num > 0:
        num, rem = divmod(num, 62)
        chars.append(BASE62_ALPHABET[rem])
    encoded = "".join(reversed(chars))
    return encoded.zfill(length)


async def generate_shortcode(
    redis_client: Redis, incr_key: str, length: int = 7
) -> str:
    """
    Generate a unique shortcode by incrementing a Redis counter and encoding the value in base62.

    Args:
        length (int, optional): The desired length of the resulting shortcode. Defaults to 7.

    Returns:
        str: A base62-encoded string representation of the incremented counter.
    """
    value = await redis_client.incr(incr_key)
    return _encode_base62(value, length=length)
