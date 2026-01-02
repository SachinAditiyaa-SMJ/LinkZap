from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.urls import URL
from app.schemas.urls import URLCreate, URLResponse, URLUpdate, URLFilterParams
from app.services import db, redis
from app.utils.shortcode_generator import generate_shortcode

router = APIRouter(prefix="/urls")


@router.post("/shorten", response_model=URLResponse)
async def shorten_url(
    url: URLCreate,
    db: AsyncSession = Depends(db.get_session),
    redis_client: Redis = Depends(redis.get_redis),
):
    if url.short_code is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom short codes are not supported.",
        )
    
    shortcode: str = await generate_shortcode(redis_client, "url:counter")

    payload = url.model_dump(exclude_unset=True)
    payload["original_url"] = str(url.original_url)
    payload["short_code"] = shortcode

    url_instance: URL = await URL.create(db, **payload)
    
    # Cache the URL data in Redis using a hash
    hash_key = f"url:{shortcode}"
    cache_data = {
        "id": str(url_instance.id),
        "short_code": url_instance.short_code,
        "original_url": url_instance.original_url,
        "is_active": str(url_instance.is_active),
    }
    
    # Add expires_at if it exists
    if url_instance.expires_at:
        cache_data["expires_at"] = url_instance.expires_at.isoformat()
    
    # Store in Redis hash
    await redis_client.hset(hash_key, mapping=cache_data)
    
    return url_instance


@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db_session: AsyncSession = Depends(db.get_session),
    redis_client: Redis = Depends(redis.get_redis),
) -> RedirectResponse:
    """
    Resolve a shortcode to its original URL and perform an HTTP redirect.
    """
    # Check cache first
    hash_key = f"url:{short_code}"
    cached_data = await redis_client.hgetall(hash_key)
    
    if cached_data:
        # Found in cache
        is_active = cached_data.get("is_active", "True").lower() == "true"
        
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short URL not found.",
            )
        
        # Check expiry if set
        expires_at_str = cached_data.get("expires_at")
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if expires_at <= now:
                # Remove expired entry from cache
                await redis_client.delete(hash_key)
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="Short URL has expired.",
                )
        
        original_url = cached_data.get("original_url")
        if original_url:
            return RedirectResponse(
                url=original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )
    
    # Cache miss - query database
    url_obj = await URL.filter_by(db_session, short_code=short_code, is_active=True)

    # Not found or inactive
    if url_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found.",
        )

    # Check expiry, if set
    if url_obj.expires_at is not None:
        # Assume timezone-aware timestamps; fall back safely if naive
        now = datetime.now(timezone.utc)
        expires_at = (
            url_obj.expires_at
            if url_obj.expires_at.tzinfo
            else url_obj.expires_at.replace(tzinfo=timezone.utc)
        )
        if expires_at <= now:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Short URL has expired.",
            )
    
    # Cache the result for future requests
    hash_key = f"url:{short_code}"
    cache_data = {
        "id": str(url_obj.id),
        "short_code": url_obj.short_code,
        "original_url": url_obj.original_url,
        "is_active": str(url_obj.is_active),
    }
    
    if url_obj.expires_at:
        cache_data["expires_at"] = url_obj.expires_at.isoformat()
    
    await redis_client.hset(hash_key, mapping=cache_data)

    return RedirectResponse(
        url=url_obj.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


@router.get("/info/", response_model=List[URLResponse])
async def get_url_info(
    filter_params: Annotated[URLFilterParams, Query()],
    db_session: AsyncSession = Depends(db.get_session),
) -> URLResponse:
    """
    Get URL details by short code.
    """

    url_obj = await URL.filter_all(db_session, **filter_params.model_dump(exclude_unset=True, exclude_none=True))

    if url_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found.",
        )

    return url_obj



@router.put("/{id}", response_model=URLResponse)
async def update_url(
    id: int,
    url_update: URLUpdate,
    db_session: AsyncSession = Depends(db.get_session),
    redis_client: Redis = Depends(redis.get_redis),
) -> URLResponse:
    """
    Update URL details by id.
    """
    updates = url_update.model_dump(exclude_unset=True)

    # Convert HttpUrl to string if original_url is being updated
    if "original_url" in updates:
        updates["original_url"] = str(updates["original_url"])

    # Update the URL
    updated_url = await URL.update(db_session, id, updates)
    
    # Update cache
    hash_key = f"url:{updated_url.short_code}"
    cache_data = {
        "id": str(updated_url.id),
        "short_code": updated_url.short_code,
        "original_url": updated_url.original_url,
        "is_active": str(updated_url.is_active),
    }
    
    if updated_url.expires_at:
        cache_data["expires_at"] = updated_url.expires_at.isoformat()
    
    await redis_client.hset(hash_key, mapping=cache_data)
    
    # If expired, delete from cache
    if updated_url.expires_at:
        expires_at = (
            updated_url.expires_at
            if updated_url.expires_at.tzinfo
            else updated_url.expires_at.replace(tzinfo=timezone.utc)
        )
        now = datetime.now(timezone.utc)
        if expires_at <= now:
            await redis_client.delete(hash_key)

    return updated_url


