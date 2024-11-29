import os
import asyncio
import redis.exceptions
import redis.asyncio as redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import signal
from .env import LOG

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

LOG.info(f"Database URL: {DATABASE_URL}")
LOG.info(f"Redis URL: {REDIS_URL}")

# Create an engine
DB_ENGINE = create_engine(
    DATABASE_URL,
    pool_size=20,  # Reasonable default, adjust based on your needs
    max_overflow=10,  # Allow 10 connections beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using
    pool_timeout=30,  # Wait up to 30 seconds for available connection
)
REDIS_POOL = None

Session = sessionmaker(bind=DB_ENGINE)


def db_health_check() -> bool:
    try:
        conn = DB_ENGINE.connect()
    except OperationalError as e:
        LOG.error(f"Database connection failed: {e}")
        return False
    else:
        conn.close()
        return True


async def redis_health_check() -> bool:
    try:
        async with get_redis_client() as redis_client:
            await redis_client.ping()
    except redis.exceptions.ConnectionError as e:
        LOG.error(f"Redis connection failed: {e}")
        return False
    else:
        return True


async def close_connection():
    DB_ENGINE.dispose()
    if REDIS_POOL is not None:
        await REDIS_POOL.aclose()
    LOG.info("Connections closed")


def init_redis_pool():
    global REDIS_POOL
    REDIS_POOL = redis.ConnectionPool.from_url(REDIS_URL)
    print("!!!", REDIS_POOL)


def get_redis_client() -> redis.Redis:
    if REDIS_POOL is not None:
        return redis.Redis(connection_pool=REDIS_POOL, decode_responses=True)
    else:
        return redis.Redis.from_url(REDIS_URL, decode_responses=True)


if __name__ == "__main__":

    async def main():
        try:
            result = await redis_health_check()
            print(result)
        finally:
            await close_connection()

    asyncio.run(main())
