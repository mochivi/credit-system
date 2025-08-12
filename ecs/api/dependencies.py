from typing import Annotated, TypeAlias

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ecs.core.security import verify_access_token
from ecs.models.schemas.token import TokenData
from ecs.services import auth_service

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

# Validate access token and return principal claims (service or user)
def get_current_principal(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    token_data: TokenData = verify_access_token(token)
    return token_data

CurrentPrincipalDep: TypeAlias = Annotated[TokenData, Depends(get_current_principal)]

# Service dependencies
AuthServiceDep: TypeAlias = Annotated[auth_service.AuthService, Depends()]