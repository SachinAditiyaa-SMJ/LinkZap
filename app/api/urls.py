from fastapi import APIRouter, Depends
from app import db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.urls import URLCreate, URLResponse, URLUpdate


router = APIRouter(prefix="/urls")


@router.post("/")
async def get_urls(url: URLCreate, db: AsyncSession = Depends(db.get_session)):
    return {"id": 1, "short_code": "asn1234"}
