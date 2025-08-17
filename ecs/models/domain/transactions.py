import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Numeric, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecs.models.domain import Base

if TYPE_CHECKING:
    from ecs.models.domain.user import DBUser


class DBTransaction(Base):
    __tablename__ = "transactions"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Foreign key to users
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Transaction details
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BRL", nullable=False)
    
    # Transaction timestamp
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationship
    user: Mapped["DBUser"] = relationship("DBUser", back_populates="transactions")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index("ix_transactions_user_occurred", "user_id", "occurred_at"),
        Index("ix_transactions_occurred_at", "occurred_at"),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, timestamp={self.occurred_at}')>"
