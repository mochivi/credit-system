from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ecs.models.schemas.token import TokenResponse
from ecs.api.dependencies import AuthServiceDep
from ecs.models.schemas.client import Client
from ecs.models.schemas.user import UserLogin

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

    from fastapi import HTTPException
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required."
        )

    # If client_id and client_secret are provided, treat as client credentials
    if form_data.client_id and form_data.client_secret:
        client_login = Client(
            client_id=form_data.client_id,
            client_secret=form_data.client_secret
        )
        return auth_service.authenticate_client(client_login)
    
    # If only username and password are present, treat as user login
    user_login = UserLogin(
        email=form_data.username,
        password=form_data.password
    )
    return auth_service.authenticate_user(user_login)