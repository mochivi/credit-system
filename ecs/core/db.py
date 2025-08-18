from typing import Any, AsyncGenerator, TypeAlias, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
import redis as redis_sync
from rq import Queue
from functools import lru_cache

from ecs.core.config import settings

# Database setup
engine: AsyncEngine = create_async_engine(settings.DB_URL)
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, 
    autoflush=False, 
    autocommit=False, 
    expire_on_commit=False
)

# Redis (async) connection pool for general async Redis usage
redis_pool: ConnectionPool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=20,
    retry_on_timeout=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    decode_responses=True,
)

async def get_async_db_session()  -> AsyncGenerator[AsyncSession, Any]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Not used, but can be used if there's a need to store anything on Redis
async def get_redis_client() -> AsyncGenerator[redis.Redis, Any]:
    """Get Redis client with connection pooling (async)."""
    client = redis.Redis(connection_pool=redis_pool)
    try:
        await client.ping()
        yield client
    except redis.ConnectionError as e:
        raise e
    finally:
        await client.close()

# RQ (sync) Queue setup — one Queue per process (singleton)
@lru_cache(maxsize=1)
def _get_rq_queue_singleton(queue_name: str = "ecs:offers") -> Queue:
    sync_pool = redis_sync.ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=20,
        socket_connect_timeout=5,
        socket_timeout=5,
        decode_responses=True,
    )
    sync_client = redis_sync.Redis(connection_pool=sync_pool)
    return Queue(name=queue_name, connection=sync_client)

def get_rq_queue() -> Queue:
    """FastAPI dependency: returns a process-wide RQ Queue instance."""
    return _get_rq_queue_singleton()

AsyncSessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_async_db_session)]
RedisDep: TypeAlias = Annotated[redis.Redis, Depends(get_redis_client)]
RQQueueDep: TypeAlias = Annotated[Queue, Depends(get_rq_queue)]