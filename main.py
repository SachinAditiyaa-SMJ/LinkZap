from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.utils import shortcode_generator
from app.services import db
from app.services import redis
from app.api import urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to Database...")
    await db.init_db_engine()
    await db.create_tables()
    logger.info("Connecting to Database Successful")
    logger.info("Connecting to Redis...")
    await redis.init_redis()
    await shortcode_generator.init_counter( await redis.get_redis(), "url:counter")
    logger.info("Connecting to Redis Successful")

    yield

    logger.info("Shutting Down Application..")
    await db.engine.dispose()
    await redis.redis_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(urls.router)
