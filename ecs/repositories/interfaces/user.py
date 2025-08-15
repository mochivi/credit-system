from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from ecs.models.domain import User

class IUserRepository(ABC):
    """Base abstract class for the user repository"""
    
    @abstractmethod
    async def get_by_email(self, email: str, db: AsyncSession) -> User:
        ...
