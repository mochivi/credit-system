import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecs.models.domain import Base

if TYPE_CHECKING:
    from .emotion import EmotionalEvent
    from .transactions import Transaction
    from .credit import RiskAssessment, CreditOffer, CreditAccount


class User(Base):
    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Identity and contact
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    emotional_events: Mapped[list["EmotionalEvent"]] = relationship(
        "EmotionalEvent", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(
        "RiskAssessment", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    credit_offers: Mapped[list["CreditOffer"]] = relationship(
        "CreditOffer", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    credit_account: Mapped["CreditAccount | None"] = relationship(
        "CreditAccount", 
        back_populates="user",
        uselist=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
