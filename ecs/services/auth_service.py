from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
import structlog

from ecs.core.config import settings
from ecs.core.security import create_access_token, verify_password
from ecs.core.db import AsyncSessionDep
from ecs.repositories.exceptions import NotFoundError
from ecs.services.dependencies import UserRepositoryDep, ClientRepositoryDep
from ecs.models.schemas.token import TokenData, TokenResponse, PrincipalType
from ecs.models.schemas.client import Client
from ecs.models.schemas.user import UserLogin
from ecs.services.exceptions import UnauthorizedError

# Mocked allowed clients
CLIENTS = {
    "svc:ingest" : "e?<[;Mn.84f$h}l"
}

# Mocked users (for MVP)
USERS = {
    "user@example.com": "Passw0rd!"
}

class AuthService:

    def __init__(
        self,
        user_repository: UserRepositoryDep,
        client_repository: ClientRepositoryDep,
        session: AsyncSessionDep
    ) -> None:
        self.user_repository = user_repository
        self.client_repository = client_repository
        self.db = session

    async def authenticate_user(self, user: UserLogin) -> TokenResponse:
        logger = structlog.get_logger()

        try:
            db_user = await self.user_repository.get_by_email(user.email, self.db)
        except NotFoundError as e:
            # Convert to UnauthorizedError to avoid exposing details
            raise UnauthorizedError("Invalid password or username", original_error=e)

        logger.debug("Verifying user password")
        if not verify_password(user.password, db_user.password):
            raise UnauthorizedError("Invalid password or username")

        logger.debug("Creating access token")
        token_data = TokenData(
            sub=db_user.email,
            exp=datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_SECONDS),
            typ=PrincipalType.user,
        )
        return create_access_token(token_data.model_dump())
    
    async def authenticate_client(self, client: Client) -> TokenResponse:
        logger = structlog.get_logger()

        try:
            db_client = await self.client_repository.get_by_client_id(client.client_id, self.db)
        except NotFoundError as e:
            # Convert to UnauthorizedError to avoid exposing details
            raise UnauthorizedError("Invalid client ID or secret", original_error=e)

        logger.debug("Verifying client secret")
        if not verify_password(client.client_secret, db_client.client_secret):
            raise UnauthorizedError("Invalid client ID or secret")

        logger.debug("Creating access token")
        token_data = TokenData(
            sub=db_client.client_id,
            exp=datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_SECONDS),
            typ=PrincipalType.client,
        )
        return create_access_token(token_data.model_dump())