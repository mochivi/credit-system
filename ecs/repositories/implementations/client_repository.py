from typing import override

import structlog
from structlog.contextvars import bind_contextvars
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ecs.repositories.interfaces import IClientRepository
from ecs.models.domain import Client
from ecs.repositories.exceptions import DatabaseError, NotFoundError

class ClientRepository(IClientRepository):

    @override
    async def get_by_client_id(self, client_id: str, db: AsyncSession) -> Client:
        logger = structlog.get_logger()
        logger.debug("Getting client from the database by client_id")
        
        try:
            result = await db.execute(
                select(Client).where(Client.client_id == client_id)
            )
            client: Client | None = result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {e}", original_error=e)
        
        if not client:
            raise NotFoundError("client", message="Client not found by client ID")

        bind_contextvars(id=client.id, client_id=client_id)
        logger.debug("Successfully retrieved client")
        return client