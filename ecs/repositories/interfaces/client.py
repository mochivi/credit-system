from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from ecs.models.domain import DBClient

class IClientRepository(ABC):
    """Base abstract class for the client repository"""

    @abstractmethod
    async def get_by_client_id(self, client_id: str, db:AsyncSession) -> DBClient:
        ...
