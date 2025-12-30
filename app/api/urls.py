from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.urls import URL
from app.schemas.urls import URLCreate, URLResponse
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
        
    # Create a Short code
    shortcode: str = await generate_shortcode(redis_client, "url:counter")

    payload = url.model_dump(exclude_unset=True)
    payload["original_url"] = str(url.original_url)
    payload["short_code"] = shortcode

    url_instance: URL = await URL.create(db, **payload)
    return url_instance


@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db_session: AsyncSession = Depends(db.get_session),
) -> RedirectResponse:
    """
    Resolve a shortcode to its original URL and perform an HTTP redirect.
    """
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

    return RedirectResponse(url=url_obj.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
