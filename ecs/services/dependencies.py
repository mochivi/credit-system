from typing import Annotated, TypeAlias

from fastapi import Depends

from ecs.repositories import EmotionalEventsRepository

EmotionalEventsRepositoryDep: TypeAlias = Annotated[EmotionalEventsRepository, Depends()]
