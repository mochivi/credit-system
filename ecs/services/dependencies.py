from typing import Annotated, TypeAlias

from fastapi import Depends

from ecs.repositories import (
    EmotionalEventsRepository,
    UserRepository,
    ClientRepository
)

EmotionalEventsRepositoryDep: TypeAlias = Annotated[EmotionalEventsRepository, Depends()]
UserRepositoryDep: TypeAlias = Annotated[UserRepository, Depends()]
ClientRepositoryDep: TypeAlias = Annotated[ClientRepository, Depends()]