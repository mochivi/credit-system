from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from ecs.models.domain import DBUser

class IUserRepository(ABC):
    """Base abstract class for the user repository"""
    
    @abstractmethod
    async def get_by_email(self, email: str, db: AsyncSession) -> "DBUser":
        ...
