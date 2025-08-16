from datetime import datetime

from enum import StrEnum
from pydantic import BaseModel


class PrincipalType(StrEnum):
    client = "client"
    user = "user"

# The information encoded into the token
class TokenData(BaseModel):
    sub: str  # principal id, an UUID converted to str
    exp: datetime
    typ: PrincipalType  # principal type: client or user

# We reply back with the token + expiry details
class TokenResponse(BaseModel):
    access_token: str
    expires_seconds: int