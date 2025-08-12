from datetime import datetime

from pydantic import BaseModel

# The information encoded into the token
class TokenData(BaseModel):
    sub: str  # principal id, e.g., svc:ingest, key:abc123, usr:uuid
    exp: datetime

# We reply back with the token + expiry details
class TokenResponse(BaseModel):
    access_token: str
    expires_seconds: int