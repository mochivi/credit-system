from pydantic import BaseModel, Field

class Features(BaseModel):
    # Transactional features
    average_daily_spend: float = Field(ge=0, description="Average daily spend")
    avg_daily_transactions: int = Field(ge=0, description="Average daily transactions")
    max_single_transaction: float = Field(ge=0, description="Maximum spend in single transaction")
    income_volatility: float = Field(ge=0, le=1, description="Income volatility (0=stable, 1=highly volatile)")

    # Emotional features
    average_emotional_stability: float = Field(ge=-1, le=1, description="Average emotional stability (-1=unstable, 0=neutral, 1=stable)")
    stress_events_count: int = Field(ge=0, description="Count of stressful events")
    positive_emotion_ratio: float = Field(ge=-1, le=1, description="Positive emotion ratio (-1=all negative, 0=neutral, 1=all positive)")
    emotional_volatility: float = Field(ge=0, le=1, description="Emotional volatility (0=stable, 1=highly volatile)")

    # Time-weighted features
    recent_emotional_trend: float = Field(ge=-1, le=1, description="Recent emotional trend (-1=declining, 0=stable, 1=improving)")
    spending_pattern_change: float = Field(ge=-1, le=1, description="Spending pattern change (-1=decreasing, 0=stable, 1=increasing)")

    # Derived features
    emotional_spending_correlation: float = Field(ge=-1, le=1, description="Emotional spending correlation (-1=negative, 0=no correlation, 1=positive)")