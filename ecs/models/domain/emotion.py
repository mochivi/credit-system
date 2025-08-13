import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Float, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from .user import User


class EmotionalEvent(Base):
    __tablename__ = "emotional_events"

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
    
    # Event metadata
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False
    )
    
    # Emotion data (based on Pydantic schema)
    emotion_primary: Mapped[str] = mapped_column(String(50), nullable=False)
    emotion_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Dimensional representation
    arousal: Mapped[float] = mapped_column(Float, nullable=False)
    valence: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Timestamps
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default="now()",
        nullable=False
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="emotional_events")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index("ix_emotional_events_user_received", "user_id", "received_at"),
        Index("ix_emotional_events_captured_at", "captured_at"),
        Index("ix_emotional_events_emotion_primary", "emotion_primary"),
    )

    def __repr__(self) -> str:
        return f"<EmotionalEvent(id={self.id}, user_id={self.user_id}, emotion='{self.emotion_primary}')>"
