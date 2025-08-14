from typing import Any, AsyncGenerator, TypeAlias, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

from ecs.core.config import settings

engine: AsyncEngine = create_async_engine(settings.DB_URL)
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)

async def get_async_db_session()  -> AsyncGenerator[AsyncSession, Any]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
async def init_db(session: AsyncSession) -> None:
    pass

AsyncSessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_async_db_session)]