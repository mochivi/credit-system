from typing import Annotated, TypeAlias

from fastapi import Depends

from ecs.repositories import (
    EmotionalEventsRepository, UserRepository, ClientRepository,
    TransactionRepository, CreditRepository
)
from ecs.services.internal import FeatureEngineeringService, CreditModelService


EmotionalEventsRepositoryDep: TypeAlias = Annotated[EmotionalEventsRepository, Depends()]
UserRepositoryDep: TypeAlias = Annotated[UserRepository, Depends()]
ClientRepositoryDep: TypeAlias = Annotated[ClientRepository, Depends()]
CreditRepositoryDep: TypeAlias = Annotated[CreditRepository, Depends()]
TransactionRepositoryDep: TypeAlias = Annotated[TransactionRepository, Depends()]

FeatureEngineeringServiceDep: TypeAlias = Annotated[FeatureEngineeringService, Depends()]
CreditModelServiceDep: TypeAlias = Annotated[CreditModelService, Depends()]
