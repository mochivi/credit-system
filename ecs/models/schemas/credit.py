import uuid

from pydantic import BaseModel, Field
from enum import StrEnum

class RiskCategory(StrEnum):
    very_low_risk = "Very Low Risk"
    low_risk = "Low Risk"
    medium_risk = "Medium Risk"
    high_risk = "High Risk"

class CreditOfferStatus(StrEnum):
    offered = "Offered"
    accepted = "Accepted"
    rejected = "Rejected"
    denied = "Denied"

class CreditType(StrEnum):
    short_term = "Short term"
    long_term = "Long term"

class RiskAssessment(BaseModel):
    risk_score: float = Field(ge=0, le=1, description="Risk score")

    @property
    def risk_category(self) -> str:
        if self.risk_score >= 0.75:
            return RiskCategory.high_risk
        elif self.risk_score >= 0.50:
            return RiskCategory.medium_risk
        elif self.risk_score >= 0.25:
            return RiskCategory.low_risk
        else:
            return RiskCategory.very_low_risk
            
class CreditOffer(BaseModel):
    status: CreditOfferStatus = Field(description="Credit offer status")
    credit_type: CreditType | None = Field(default=None, description="Credit type")
    credit_limit: float | None = Field(default=None, description="Credit limit")
    apr: float | None = Field(default=None, ge=0, le=1, description="Annual percentage interest rate")

class CreditOfferResponse(CreditOffer):
    id: uuid.UUID
    user_id: uuid.UUID

class CreditAcceptResponse(BaseModel):
    id: str
    offer_id: str
    status: str
    message: str