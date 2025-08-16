import random

import structlog

from ecs.models.schemas import Features, RiskAssessment

class CreditModelService:
    
    async def predict_credit_risk(self, features: Features) -> RiskAssessment:
        """Mocked credit ML model call"""
        logger = structlog.get_logger()
        logger.debug("Sending predict risk score request to external ML model")
        
        return RiskAssessment(risk_score = random.randint(0, 1))