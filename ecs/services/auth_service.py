from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status

from ecs.core.config import settings
from ecs.core.security import create_access_token
from ecs.models.schemas.token import TokenData, TokenResponse
from ecs.models.schemas.client import Client

# Mocked allowed clients
CLIENTS = {
    "svc:ingest" : "e?<[;Mn.84f$h}l"
}

class AuthService:
    def authenticate(self, client: Client) -> TokenResponse:
        for client_id, client_secret in CLIENTS.items():
            if client.client_id == client_id and client_secret == client.client_secret:
                token_data = TokenData(
                    sub=client.client_id, 
                    exp=datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_SECONDS)
                )

                return create_access_token(token_data.model_dump())

        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="invalid credentials")