from typing import Annotated, TypeAlias

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from structlog.contextvars import bind_contextvars

from ecs.core.security import verify_access_token
from ecs.models.schemas.token import PrincipalType, TokenData
from ecs.services import auth_service, emotion_service
from ecs.services.exceptions import UnauthorizedError

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

# Validate access token and return principal claims (service or user)
def get_current_principal(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    token_data: TokenData = verify_access_token(token)
    bind_contextvars(principal_type=token_data.typ)
    return token_data

def get_current_client_principal(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    token_data: TokenData = verify_access_token(token)

    if token_data.typ != PrincipalType.client:
        raise UnauthorizedError("unauthorized operation")

    bind_contextvars(principal_type=token_data.typ)
    return token_data


CurrentPrincipalDep: TypeAlias = Annotated[TokenData, Depends(get_current_principal)]
CurrentClientPrincipalDep: TypeAlias = Annotated[TokenData, Depends(get_current_client_principal)]

# Service dependencies
AuthServiceDep: TypeAlias = Annotated[auth_service.AuthService, Depends()]
EmotionalEventsServiceDep: TypeAlias = Annotated[emotion_service.EmotionService, Depends()]