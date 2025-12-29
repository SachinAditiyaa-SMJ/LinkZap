from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app import db
from app.api import urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to Database..")
    await db.init_db_engine()
    await db.create_tables()

    yield

    logger.info("Shutting Down Application..")
    await db.engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(urls.router)
