from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status

from ecs.core.config import settings
from ecs.core.security import create_access_token
from ecs.models.schemas.token import TokenData, TokenResponse, PrincipalType
from ecs.models.schemas.client import Client
from ecs.models.schemas.user import UserLogin

# Mocked allowed clients
CLIENTS = {
    "svc:ingest" : "e?<[;Mn.84f$h}l"
}

# Mocked users (for MVP)
USERS = {
    "user@example.com": "Passw0rd!"
}

class AuthService:
    async def authenticate_user(self, user: UserLogin):
        for user_email, user_password in USERS.items():
            if user.email == user_email and user.password == user_password:
                token_data = TokenData(
                    sub=user_email,
                    exp=datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_SECONDS),
                    typ=PrincipalType.user,
                )
                return create_access_token(token_data.model_dump())

        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="invalid credentials")
    
    async def authenticate_client(self, client: Client) -> TokenResponse:
        for client_id, client_secret in CLIENTS.items():
            if client.client_id == client_id and client_secret == client.client_secret:
                token_data = TokenData(
                    sub=client.client_id,
                    exp=datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_SECONDS),
                    typ=PrincipalType.client,
                )
                return create_access_token(token_data.model_dump())

        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="invalid credentials")

    