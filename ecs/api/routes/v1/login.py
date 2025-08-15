from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, status, Form

from ecs.api.dependencies import AuthServiceDep
from ecs.api.exceptions import BadRequestError
from ecs.models.schemas import TokenResponse, Client, UserLogin

# Minimal custom form to allow both password and client_credentials without the strict regex on grant_type
class OAuth2PasswordOrClientCredentialsRequestForm:
    def __init__(
        self,
        grant_type: str = Form(default=None),
        username: str = Form(default=None),
        password: str = Form(default=None),
        scope: str = Form(default=""),
        client_id: str = Form(default=None),
        client_secret: str = Form(default=None),
    ) -> None:
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split() if scope else []
        self.client_id = client_id
        self.client_secret = client_secret

router = APIRouter(tags=["Token"])

@router.post(
    path="/token",
    status_code=status.HTTP_200_OK,
    summary="Authenticate",
    response_model=TokenResponse
)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordOrClientCredentialsRequestForm, Depends()],
    auth_service: AuthServiceDep
) -> TokenResponse:
    """Single authentication endpoint both for users and clients"""
    logger = structlog.get_logger()
    logger.info("Login request")

    if form_data.grant_type == "password":
        if not form_data.username or not form_data.password:
            raise BadRequestError(f"Username and password are required for user authentication.")
        
        user_login = UserLogin(email=form_data.username, password=form_data.password)
        token = await auth_service.authenticate_user(user_login)
        
        logger.debug("User authenticated")
        return token
    elif form_data.grant_type == "client_credentials":
        if not form_data.client_id and form_data.client_secret:
            raise BadRequestError("Client credentials are required for client authentication")
        
        client_login = Client(client_id=form_data.client_id, client_secret=form_data.client_secret)
        token = await auth_service.authenticate_client(client_login)
        
        logger.debug("Client authenticated")
        return token

    raise BadRequestError(f"Invalid request fields")