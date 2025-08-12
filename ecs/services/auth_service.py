from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status

from ecs.core.config import settings
from ecs.core.security import create_access_token
from ecs.models.schemas.token import TokenData, TokenResponse, PrincipalType
from ecs.models.schemas.client import Client

# Mocked allowed clients
CLIENTS = {
    "svc:ingest" : "e?<[;Mn.84f$h}l"
}

# Mocked users (for MVP)
USERS = {
    # user principal id is namespaced as usr:<uuid>
    "usr:11111111-1111-1111-1111-111111111111": "Passw0rd!"
}

class AuthService:
    def authenticate(self, client: Client) -> TokenResponse:
        # First, try client credentials (client_id/client_secret)
        for client_id, client_secret in CLIENTS.items():
            if client.client_id == client_id and client_secret == client.client_secret:
                token_data = TokenData(
                    sub=client.client_id,
                    exp=datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_SECONDS),
                    typ=PrincipalType.client,
                )
                return create_access_token(token_data.model_dump())

        # Then, try user credentials (client_id is user principal; client_secret is password for MVP)
        for user_id, user_password in USERS.items():
            if client.client_id == user_id and client.client_secret == user_password:
                token_data = TokenData(
                    sub=user_id,
                    exp=datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_SECONDS),
                    typ=PrincipalType.user,
                )
                return create_access_token(token_data.model_dump())

        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="invalid credentials")