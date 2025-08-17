from typing import override

import structlog
from structlog.contextvars import bind_contextvars
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ecs.repositories.interfaces import IUserRepository
from ecs.models.domain import DBUser
from ecs.repositories.exceptions import DatabaseError, NotFoundError

class UserRepository(IUserRepository):

    @override
    async def get_by_email(self, email: str, db: AsyncSession) -> DBUser:
        logger = structlog.get_logger()
        logger.debug("Getting user from the database by email")
        
        try:
            result = await db.execute(
                select(DBUser).where(DBUser.email == email)
            )
            user: DBUser | None = result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {e}", original_error=e)
        
        if not user:
            raise NotFoundError("user", message="User not found by email")

        bind_contextvars(id=user.id)
        logger.debug("Successfully retrieved user by email")
        return user