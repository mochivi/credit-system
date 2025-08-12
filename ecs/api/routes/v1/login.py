from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ecs.models.schemas.token import TokenResponse
from ecs.api.dependencies import AuthServiceDep
from ecs.models.schemas.client import Client

router = APIRouter(prefix="/token", tags=["Token"])

@router.post(
    path="/token",
    status_code=status.HTTP_200_OK,
    summary="Authenticate",
    response_model=TokenResponse
)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep
) -> TokenResponse:
    user_login = Client(client_id=form_data.username, client_secret=form_data.password) 
    return auth_service.authenticate(user_login)