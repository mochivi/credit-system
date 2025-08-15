from time import timezone
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Numeric, Index, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecs.models.domain import Base

if TYPE_CHECKING:
    from .user import User


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

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
    
    # ML model risk assesment result
    risk_score: Mapped[float] = mapped_column(Numeric(precision=5, scale=4), nullable=False)  # 0.0000 to 1.0000
    
    # Decision outcome
    decision: Mapped[str] = mapped_column(String(20), nullable=False)  # approved, declined, ...
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="risk_assessments")
    credit_offer: Mapped["CreditOffer | None"] = relationship("CreditOffer", back_populates="risk_assessment")
    
    # Indexes
    __table_args__ = (
        Index("ix_risk_assessments_user_created", "user_id", "created_at"), # Quick search for user risk assessments
        Index("ix_risk_assessments_risk_score", "risk_score"), # Allows for efficient WHERE queries based on risk_score, data analysis could benefit from this
        Index("ix_risk_assessments_decision", "decision"), # Decision index allows for efficient grouping of orders by decision
    )

    def __repr__(self) -> str:
        return f"<RiskAssessment(id={self.id}, user_id={self.user_id}, risk_score={self.risk_score}, decision='{self.decision}')>"


class CreditOffer(Base):
    __tablename__ = "credit_offers"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    risk_assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risk_assessments.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Credit terms
    credit_type: Mapped[str] = mapped_column(String(50), nullable=False)  # short_term, long_term, revolving
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    apr: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # Annual percentage rate
    
    # Offer lifecycle
    status: Mapped[str] = mapped_column(String(20), default="proposed", nullable=False)  # proposed, accepted, rejected, expired
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="credit_offers")
    risk_assessment: Mapped["RiskAssessment"] = relationship("RiskAssessment", back_populates="credit_offer")
    
    # Indexes
    __table_args__ = (
        Index("ix_credit_offers_user_status", "user_id", "status"), # Quick search for user specific offers
        Index("ix_credit_offers_expires_at", "expires_at"), # Quick search for expiration, could be useful for sending notifications about offers close to expiration 
        Index("ix_credit_offers_created_at", "created_at"), # Quick search based on created date, fast ordering of offers chronologically, metric gathering for period of time etc.
    )

    def __repr__(self) -> str:
        return f"<CreditOffer(id={self.id}, user_id={self.user_id}, credit_limit={self.credit_limit}, status='{self.status}')>"


class CreditAccount(Base):
    __tablename__ = "credit_accounts"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Foreign key to users (one-to-one relationship)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    
    # Active credit terms
    active_limit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    apr: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    credit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Utilization
    current_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    available_credit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    
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
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="credit_account")
    
    # Indexes
    __table_args__ = (
        Index("ix_credit_accounts_user_id", "user_id"), # Fast lookup of a user’s account.
        Index("ix_credit_accounts_updated_at", "updated_at"), # Identify recently changed accounts for reconciliation/jobs.
    )

    def __repr__(self) -> str:
        return f"<CreditAccount(id={self.id}, user_id={self.user_id}, active_limit={self.active_limit}, current_balance={self.current_balance})>"
