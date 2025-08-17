import uuid
from typing import Any, override, Sequence
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from ecs.repositories.exceptions import DatabaseError
from ecs.repositories.interfaces import ITransactionRepository
from ecs.models.domain import DBTransaction

class TransactionRepository(ITransactionRepository):

    @override
    async def get_recent_transactions(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        since: datetime | None = None,
        limit: int | None = None
    ) -> Sequence[DBTransaction]:
        logger = structlog.get_logger()
        logger.debug("Retrieving recent transactions", since=since.isoformat() if since else "ever")

        # Build query
        query = select(DBTransaction).where(DBTransaction.user_id == user_id)
        if since:
            query = query.where(DBTransaction.occurred_at > since)
        if limit:
            query = query.limit(limit)
        query = query.order_by(DBTransaction.occurred_at.desc())

        try:
            result = await db.execute(query)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {e}", original_error=e)

        # Extract Transaction objects from Row objects
        transactions = [row[0] for row in result.all()]
        if len(transactions) == 0:
            logger.warn(f"User has no transactions since {since.isoformat() if since else "ever"}")
            return []

        logger.debug(f"Retrieved transactions", count=len(transactions), since=since.isoformat() if since else "ever")
        return transactions