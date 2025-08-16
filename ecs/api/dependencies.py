from typing import Annotated, TypeAlias, TYPE_CHECKING

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from structlog.contextvars import bind_contextvars

from ecs.core.security import verify_access_token
from ecs.models.schemas.token import PrincipalType
from ecs.services import AuthService, EmotionService, CreditService
from ecs.services.exceptions import UnauthorizedError
from ecs.models.schemas.token import TokenData

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

# Validate access token and return principalType of user and claims
def get_current_user_principal(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    token_data: TokenData = verify_access_token(token)
    
    if token_data.typ != PrincipalType.user:
        raise UnauthorizedError("unauthorized access")
    
    bind_contextvars(principal_type=token_data.typ)
    return token_data

def get_current_client_principal(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    token_data: TokenData = verify_access_token(token)

    if token_data.typ != PrincipalType.client:
        raise UnauthorizedError("unauthorized access")

    bind_contextvars(principal_type=token_data.typ)
    return token_data

CurrentUserPrincipalDep: TypeAlias = Annotated[TokenData, Depends(get_current_user_principal)]
CurrentClientPrincipalDep: TypeAlias = Annotated[TokenData, Depends(get_current_client_principal)]

# Service dependencies
AuthServiceDep: TypeAlias = Annotated[AuthService, Depends()]
EmotionalEventsServiceDep: TypeAlias = Annotated[EmotionService, Depends()]
CreditServiceDep: TypeAlias = Annotated[CreditService, Depends()]