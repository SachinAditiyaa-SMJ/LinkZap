from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from loguru import logger
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

    return updated_url


