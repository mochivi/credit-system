from datetime import datetime, timedelta

import uuid

import structlog
from structlog.contextvars import bind_contextvars

from ecs.services.dependencies import (
    EmotionalEventsRepositoryDep, CreditRepositoryDep,
    TransactionRepositoryDep, FeatureEngineeringServiceDep, CreditModelServiceDep
)
from ecs.core.db import AsyncSessionDep, RQQueueDep
from ecs.models.schemas import (
    Features, CreditOffer, RiskCategory, CreditType, CreditOfferStatus, RiskAssessment
)
from ecs.models.domain import DBCreditOffer, DBRiskAssessment
from ecs.services.exceptions import (
    ActiveCreditOfferExistsError, CreditAccountExistsError, 
    NoActiveCreditOfferExistsError, InvalidCreditOfferError
)

class CreditService:
    def __init__(
        self, 
        credit_repository: CreditRepositoryDep,
        transaction_repository: TransactionRepositoryDep,
        emotional_events_repo: EmotionalEventsRepositoryDep,
        feature_engineering_service: FeatureEngineeringServiceDep,
        credit_model_service: CreditModelServiceDep,
        session: AsyncSessionDep,
        redis_queue: RQQueueDep
    ) -> None:
        self.db = session
        self.credit_repository = credit_repository
        self.transaction_repository = transaction_repository
        self.emotional_events_repo = emotional_events_repo
        self.feature_engineering_service = feature_engineering_service
        self.credit_model_service = credit_model_service
        self.redis_queue = redis_queue

    async def apply_for_credit_line(self, user_id: uuid.UUID) -> DBCreditOffer:
        logger = structlog.get_logger()

        # If user already has an active credit account, we won't allow them to request for another
        # or more credit
        # This doesn't reflect the reality of the business, its a choice made for simplificaton purposes
        active_credit_account = await self.credit_repository.get_credit_account_for_user(user_id, self.db)
        if active_credit_account is not None:
            raise CreditAccountExistsError("User already has an active credit account")

        # If user already has an active credit offer, return that
        active_offer = await self.credit_repository.get_active_credit_offer_for_user(user_id, self.db)
        if active_offer is not None:
            bind_contextvars(offer_id=active_offer.id)
            logger.debug("User has an active credit offer")
            raise ActiveCreditOfferExistsError(credit_offer=active_offer, message="User already has an active credit offer")

        # Get raw data from database
        logger.debug("Retrieving data for credit line analysis")
        transactions = await self.transaction_repository.get_recent_transactions(
            user_id,
            self.db,
            since=self.feature_engineering_service.transactions_since,
            limit=self.feature_engineering_service.transaction_limit
        )
        emotional_events = await self.emotional_events_repo.get_recent_emotional_events(
            user_id,
            self.db,
            self.feature_engineering_service.emotional_events_since,
            self.feature_engineering_service.emotional_events_limit
        )

        # Perform feature engineering
        logger.debug("Creating features from user data")
        features: Features = await self.feature_engineering_service.create_features(
            transactions, emotional_events
        )
        
        try:
            # Check if there's a non expired risk assessment
            db_risk_assessment: DBRiskAssessment | None = await self.credit_repository.get_valid_risk_assessment(user_id, self.db)   
            if db_risk_assessment is None:
                # Submit request to credit ML model
                logger.debug("Sending request to credit model service")
                risk_assessment: RiskAssessment = await self.credit_model_service.predict_credit_risk(features)

                # Create risk assessment in the db
                logger.debug("Creating risk assessment")
                db_risk_assessment = DBRiskAssessment(
                    user_id=user_id,
                    expires_at=datetime.now()+timedelta(days=15),
                    **risk_assessment.model_dump()
                )
                await self.credit_repository.create_risk_assessment(db_risk_assessment, self.db)
            else:
                logger.debug("Reusing valid previous risk assessment")
                risk_assessment = RiskAssessment(risk_score=db_risk_assessment.risk_score)

            logger.debug("Calculating credit offer")
            credit_offer: CreditOffer = CreditOfferCalculator().calculate_offer(risk_assessment, features)

            # Create credit offer in the database
            logger.debug("Creating credit offer")
            db_credit_offer: DBCreditOffer = DBCreditOffer(
                user_id=user_id,
                risk_assessment_id=db_risk_assessment.id,
                expires_at=datetime.now()+timedelta(days=15),
                **credit_offer.model_dump()
            )
            await self.credit_repository.create_credit_offer(db_credit_offer, self.db)
            
            print("we got here?")
            logger.debug("Committing changes")
            await self.db.commit() # Commit both changes as a unit
            return db_credit_offer # Already refreshed
        except Exception:
            await self.db.rollback()
            raise

    async def accept_credit_offer(self, offer_id: uuid.UUID,user_id: uuid.UUID) -> str:

        # If user already has an active credit account, we won't allow them to request for another or more credit
        # This doesn't reflect the reality of the business, its a choice made for simplificaton purposes
        # We check for this again in case the user tries to accept some other offer somehow
        active_credit_account = await self.credit_repository.get_credit_account_for_user(user_id, self.db)
        if active_credit_account is not None:
            raise CreditAccountExistsError("User already has an active credit account")

        # Query by the user_id, that way, we avoid other users being able to query the database for offer_ids
        # Safer to query by the user_id by default
        credit_offer: DBCreditOffer | None = await self.credit_repository.get_active_credit_offer_for_user(user_id, self.db)
        if credit_offer is None:
            raise NoActiveCreditOfferExistsError("No active credit offer found")

        # Second layer of defense, validate the provided offer_id matches the retrieved id
        # Business rule is that there can be only one active credit_offer for each user at the moment
        # This avoids any coding errors between the offer_id the user wants to accept and the offer_id we retrieved
        # by querying by the user_id
        if credit_offer.id != offer_id:
            raise InvalidCreditOfferError("Provided offer ID does not match the expected ID")

        # Check if credit offer is still valid
        if credit_offer.expires_at < datetime.now(credit_offer.expires_at.tzinfo):
            raise InvalidCreditOfferError("Credit offer has expired")

        # Trigger async job to create credit account and then mark the credit offer as accepted
        _ =  self.redis_queue.enqueue("ecs.workers.jobs.process_credit_acceptance", offer_id=str(offer_id), user_id=str(user_id))
        
        # Create an internal tracker for the job, not used as of this implementation
        # No status checking endpoint requirement.
        job_id: str = str(uuid.uuid4())

        return job_id

class CreditOfferCalculator:

    def calculate_offer(self, risk_assessment: RiskAssessment, features: Features) -> CreditOffer:
        if risk_assessment.risk_category == RiskCategory.high_risk:
            return CreditOffer(status=CreditOfferStatus.rejected)

        # Base credit limit calculation
        base_limit = self._calculate_base_limit(risk_assessment.risk_score)
        
        # Adjustments based on multiple factors
        adjusted_limit = base_limit * self._get_multipliers(risk_assessment.risk_score, features)
        
        return CreditOffer(
            status=CreditOfferStatus.offered,
            credit_limit=adjusted_limit,
            apr=self._calculate_interest_rate(risk_assessment.risk_score, features),
            credit_type=self._determine_credit_type(risk_assessment.risk_category)
        )
    
    def _calculate_base_limit(self, risk_score: float) -> float:
        # Inverse relationship: lower risk = higher limit
        max_limit = 50000  # Maximum credit limit
        min_limit = 1000   # Minimum credit limit
        
        # Exponential decay function
        base_limit = max_limit * (1 - risk_score ** 2)
        return max(min_limit, base_limit)
    
    def _get_multipliers(self, risk_score: float, features: Features) -> float:
        """Post processing
            Individual features can be weighted differently based on business requirements
            Aligns more closely with business requirements
        """
        multiplier = 1.0

        # Average daily spend
        # What this means
        # If someone spends less than $50 a day, we are always going to apply the lowest possible multiplier
        # If someone spends more then $5000 a day, we are still going to apply the highest possible multiplier
        normalized_avg_daily_spend = self._normalize(features.average_daily_spend, lower_bound=50, upper_bound=5000)
        avg_daily_spend_multiplier = self._interpolate(metric=normalized_avg_daily_spend, min_value=1, max_value=1.5, bias_factor=2)
        
        # Average daily transactions - heavily biased towards high daily transaction volume
        normalized_avg_daily_transactions = self._normalize(features.avg_daily_transactions, lower_bound=0.1, upper_bound=1000)
        avg_daily_transactions_multiplier = self._interpolate(metric=normalized_avg_daily_transactions, min_value=0.9, max_value=1.8, bias_factor=2.5)

        # Emotional trend multiplier - linearly penalizes downward emotional trends
        normalized_avg_emotional_trend = self._normalize(features.recent_emotional_trend, lower_bound=-1, upper_bound=1)
        avg_emotional_trend_multiplier = self._interpolate(normalized_avg_emotional_trend, min_value=0.5, max_value=1.5, bias_factor=1)
        
        # Risk score multiplier - penalizes higher risk scores
        # Normalize risk_score (already in [0,1]), invert so that lower risk gets higher multiplier
        risk_score_multiplier = self._interpolate(metric=risk_score,  min_value=0.7, max_value=1.2, bias_factor=2, invert=True)

        return multiplier * avg_daily_spend_multiplier * avg_daily_transactions_multiplier * avg_emotional_trend_multiplier * risk_score_multiplier    

    def _calculate_interest_rate(self, risk_score: float, features: Features) -> float:
        """Post processing
            Individual features can be weighted differently based on business requirements
            Aligns more closely with business requirements
            Currently, only risk_score is used to calculate apr
        """

        # Base interest rate range
        min_rate = 0.08  # 8% APR
        max_rate = 0.25  # 25% APR
        base_rate: float = self._interpolate(metric=risk_score, min_value=min_rate, max_value=max_rate, bias_factor=1.75)
        
        return base_rate
    
    def _determine_credit_type(self, risk_category: str) -> CreditType:
        """Determine credit type based on credit risk category"""
        match risk_category:
            case RiskCategory.high_risk | RiskCategory.medium_risk:
                return CreditType.short_term
            case RiskCategory.low_risk | RiskCategory.very_low_risk:
                return CreditType.long_term
        raise ValueError("Invalid credit category")

    @staticmethod
    def _interpolate(metric: float, min_value: float, max_value: float, bias_factor: float, invert: bool = False) -> float:
        """
        Interpolates between min_value and max_value using a bias factor.
        The metric should be in [0, 1].

        If invert is True, the interpolation is performed with (1 - metric).
        Effectively, this pushed the X axis to the right and uses the "other side" of the curve

        The interpolation formula is:
            result = (max_value - min_value) * (metric ** bias_factor) + min_value

        - bias_factor < 1: bias towards lower metric values (faster growth)
        - bias_factor == 1: linear interpolation
        - bias_factor > 1: bias towards higher metric values (slower growth)

        Examples:
            bias_factor = 2, metric = 0.0 -> min_value
            bias_factor = 2, metric = 0.5 -> (max_value - min_value) * 0.25 + min_value
            bias_factor = 2, metric = 1.0 -> max_value
            invert=True, metric=0.2 -> uses 0.8 instead of 0.2
        """
        if not (0.0 <= metric <= 1.0):
            raise ValueError("Metric must be in the interval [0, 1].")
        if invert:
            metric = 1.0 - metric
        return (max_value - min_value) * (metric ** bias_factor) + min_value

    @staticmethod
    def _normalize(metric: float, lower_bound: float, upper_bound: float) -> float:
        """
        Normalize some metric to [0, 1] given lower and upper bounds.
        Values below lower_bound get mapped to 0
        Values above upper_bound get mapped to 1
        """
        if upper_bound == lower_bound:
            raise ValueError("Upper and lower bounds must be different for normalization.")
        if metric <= lower_bound:
            return 0.0
        if metric >= upper_bound:
            return 1.0
        return (metric - lower_bound) / (upper_bound - lower_bound)