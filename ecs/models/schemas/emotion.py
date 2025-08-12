import uuid
from datetime import datetime
from enum import StrEnum
from typing import Dict, Optional

from pydantic import BaseModel, Field

# https://en.wikipedia.org/wiki/Emotion_classification
# -> Paul Ekman identified six basic emotions: anger, disgust, fear, happiness, sadness and surprise.
class PrimaryEmotion(StrEnum):
    happiness = "happiness"
    sadness = "sadness"
    fear = "fear"
    anger = "anger"
    surprise = "surprise"
    disgust = "disgust"

# Reference: https://en.wikipedia.org/wiki/Emotion_classification
# Circumplex model of emotions -> arousal/valence define a vector which could be useful for ML Model
class EmotionalEvent(BaseModel):
    """
    Single emotional reading captured from a client device/sensor.

    All intensity-like fields are normalized to [0.0, 1.0].
    """
    
    event_id: uuid.UUID
    user_id: uuid.UUID

    # When the signal was captured on device
    captured_at: datetime

    # Categorical primary label + confidence
    emotion_primary: PrimaryEmotion
    emotion_confidence: float = Field(ge=0.0, le=1.0)

    # Dimensional representation (normalized)
    arousal: float = Field(ge=0.0, le=1.0)
    valence: float = Field(ge=0.0, le=1.0)