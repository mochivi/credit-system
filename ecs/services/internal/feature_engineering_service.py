from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Sequence
import statistics

from ecs.core.config import settings
from ecs.models.schemas import Features

if TYPE_CHECKING:
    from ecs.models.domain import DBTransaction, DBEmotionalEvent

class FeatureEngineeringService:
    def __init__(self) -> None:
        self.transaction_period_days = settings.feature_engineering_transactions_period_days
        self.transaction_limit = settings.feature_engineering_transactions_limit
        self.emotional_events_period_days = settings.feature_engineering_emotional_events_period_days
        self.emotional_events_limit = settings.feature_engineering_emotional_events_limit
    
    @property
    def transactions_since(self) -> datetime:
        return datetime.now() - timedelta(days=self.transaction_period_days)

    @property
    def emotional_events_since(self) -> datetime:
        return datetime.now() - timedelta(days=self.emotional_events_period_days)

    async def create_features(self, transactions: Sequence["DBTransaction"], emotional_events: Sequence["DBEmotionalEvent"]) -> Features:
        """Create ML features from transactional and emotional data"""
        
        # Calculate transactional features
        avg_daily_spend = self._calculate_average_daily_spend(transactions)
        avg_daily_transactions = self._calculate_average_daily_transactions(transactions)
        max_single_transaction = self._calculate_max_single_transaction(transactions)
        income_volatility = self._calculate_income_volatility(transactions)
        
        # Calculate emotional features
        avg_emotional_stability = self._calculate_average_emotional_stability(emotional_events)
        stress_events_count = self._calculate_stress_events_count(emotional_events)
        positive_emotion_ratio = self._calculate_positive_emotion_ratio(emotional_events)
        emotional_volatility = self._calculate_emotional_volatility(emotional_events)
        
        # Calculate time-weighted features
        recent_emotional_trend = self._calculate_recent_emotional_trend(emotional_events)
        spending_pattern_change = self._calculate_spending_pattern_change(transactions)
        
        # Calculate derived features
        emotional_spending_correlation = self._calculate_emotional_spending_correlation(
            transactions, emotional_events
        )
        
        return Features(
            average_daily_spend=avg_daily_spend,
            avg_daily_transactions=avg_daily_transactions,
            max_single_transaction=max_single_transaction,
            income_volatility=income_volatility,
            average_emotional_stability=avg_emotional_stability,
            stress_events_count=stress_events_count,
            positive_emotion_ratio=positive_emotion_ratio,
            emotional_volatility=emotional_volatility,
            recent_emotional_trend=recent_emotional_trend,
            spending_pattern_change=spending_pattern_change,
            emotional_spending_correlation=emotional_spending_correlation
        )
    
    def _calculate_average_daily_spend(self, transactions: Sequence["DBTransaction"]) -> float:
        """Calculate average daily spending"""
        if not transactions:
            return 0.0
        
        # Group transactions by day
        daily_spends = {}
        for transaction in transactions:
            day = transaction.occurred_at.date()
            amount = float(transaction.amount)
            daily_spends[day] = daily_spends.get(day, 0) + amount
        
        return statistics.mean(daily_spends.values()) if daily_spends else 0.0
    
    def _calculate_average_daily_transactions(self, transactions: Sequence["DBTransaction"]) -> int:
        """Calculate average daily transaction count"""
        if not transactions:
            return 0
        
        # Group transactions by day
        daily_counts = {}
        for transaction in transactions:
            day = transaction.occurred_at.date()
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        return round(statistics.mean(daily_counts.values())) if daily_counts else 0
    
    def _calculate_max_single_transaction(self, transactions: Sequence["DBTransaction"]) -> float:
        """Calculate maximum single transaction amount"""
        if not transactions:
            return 0.0
        return max(float(t.amount) for t in transactions)
    
    def _calculate_income_volatility(self, transactions: Sequence["DBTransaction"]) -> float:
        """Calculate income volatility based on transaction amounts"""
        if len(transactions) < 2:
            return 0.0
        
        amounts = [float(t.amount) for t in transactions]
        mean_amount = statistics.mean(amounts)
        
        if mean_amount == 0:
            return 0.0
        
        # Coefficient of variation (standard deviation / mean)
        std_dev = statistics.stdev(amounts)
        return min(1.0, std_dev / mean_amount)
    
    def _calculate_average_emotional_stability(self, emotional_events: Sequence["DBEmotionalEvent"]) -> float:
        """Calculate average emotional stability based on valence consistency"""
        if not emotional_events:
            return 0  # Neutral stability
        
        # Use valence as a proxy for emotional stability
        # Higher valence = more positive emotions = more stable
        valences = [event.valence for event in emotional_events]
        return statistics.mean(valences)
    
    def _calculate_stress_events_count(self, emotional_events: Sequence["DBEmotionalEvent"]) -> int:
        """Count stressful emotional events"""
        if not emotional_events:
            return 0
        
        # Define stress indicators: low valence, high arousal, or specific emotions
        stress_count = 0
        for event in emotional_events:
            # Low valence (negative emotions) or high arousal (stress)
            if event.valence < 0.3 or event.arousal > 0.7:
                stress_count += 1
            # Specific stress emotions
            elif event.emotion_primary.lower() in ["anger", "fear", "anxiety", "stress"]:
                stress_count += 1
        
        return stress_count
    
    def _calculate_positive_emotion_ratio(self, emotional_events: Sequence["DBEmotionalEvent"]) -> float:
        """Calculate ratio of positive emotions"""
        if not emotional_events:
            return 0  # Neutral ratio
        
        positive_count = 0
        for event in emotional_events:
            # High valence indicates positive emotions
            if event.valence > 0.35:
                positive_count += 1
            # Specific positive emotions
            elif event.emotion_primary.lower() in ["joy", "happiness", "excitement", "contentment"]:
                positive_count += 1
        
        return positive_count / len(emotional_events)
    
    def _calculate_emotional_volatility(self, emotional_events: Sequence["DBEmotionalEvent"]) -> float:
        """Calculate emotional volatility based on valence changes"""
        if len(emotional_events) < 2:
            return 0.0
        
        # Sort by timestamp and calculate valence changes
        sorted_events = sorted(emotional_events, key=lambda x: x.captured_at)
        valence_changes = []
        
        for i in range(1, len(sorted_events)):
            change = abs(sorted_events[i].valence - sorted_events[i-1].valence)
            valence_changes.append(change)
        
        return statistics.mean(valence_changes) if valence_changes else 0.0
    
    def _calculate_recent_emotional_trend(self, emotional_events: Sequence["DBEmotionalEvent"]) -> float:
        """Calculate recent emotional trend (positive = improving, negative = declining)"""
        if len(emotional_events) < 2:
            return 0.0
        
        # Sort by timestamp and split into recent vs older
        sorted_events = sorted(emotional_events, key=lambda x: x.captured_at)
        mid_point = len(sorted_events) // 2
        
        older_events = sorted_events[:mid_point]
        recent_events = sorted_events[mid_point:]
        
        older_avg_valence = statistics.mean([e.valence for e in older_events])
        recent_avg_valence = statistics.mean([e.valence for e in recent_events])
        
        # Return trend (-1 to 1)
        return max(-1.0, min(1.0, recent_avg_valence - older_avg_valence))
    
    def _calculate_spending_pattern_change(self, transactions: Sequence["DBTransaction"]) -> float:
        """Calculate spending pattern change over time"""
        if len(transactions) < 4:
            return 0.0
        
        # Sort by timestamp and split into recent vs older
        sorted_transactions = sorted(transactions, key=lambda x: x.occurred_at)
        mid_point = len(sorted_transactions) // 2
        
        older_transactions = sorted_transactions[:mid_point]
        recent_transactions = sorted_transactions[mid_point:]
        
        older_avg_amount = statistics.mean([float(t.amount) for t in older_transactions])
        recent_avg_amount = statistics.mean([float(t.amount) for t in recent_transactions])
        
        if older_avg_amount == 0:
            return 0.0
        
        # Calculate percentage change
        change_ratio = (recent_avg_amount - older_avg_amount) / older_avg_amount
        return max(-1.0, min(1.0, change_ratio))
    
    def _calculate_emotional_spending_correlation(self, transactions: Sequence["DBTransaction"], emotional_events: Sequence["DBEmotionalEvent"]) -> float:
        """Calculate correlation between emotional state and spending patterns"""
        if not transactions or not emotional_events:
            return 0.0
        
        # This is a simplified correlation calculation
        
        # Calculate average transaction amount
        avg_transaction_amount = statistics.mean([float(t.amount) for t in transactions])
        
        # Calculate average emotional valence
        avg_valence = statistics.mean([e.valence for e in emotional_events])
        
        # Simple correlation: if both are high or both are low, positive correlation
        # This is a placeholder - real implementation would need time-aligned data
        if avg_transaction_amount > 100 and avg_valence > 0.6:
            return 0.3  # Positive correlation
        elif avg_transaction_amount < 50 and avg_valence < 0.4:
            return 0.2  # Positive correlation
        else:
            return 0.0  # No clear correlation