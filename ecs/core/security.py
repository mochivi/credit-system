import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import ValidationError

from ecs.core.config import settings
from ecs.models.schemas.token import TokenData, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> TokenResponse:    
    encoded_jwt = jwt.encode(
        payload=data,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return TokenResponse(
        access_token=encoded_jwt,
        expires_seconds=settings.JWT_EXPIRES_SECONDS
    )

def verify_access_token(access_token: str) -> TokenData:
    try:
        claims = jwt.decode(access_token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="invalid access token")
    except Exception:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="invalid access token")

    try:
        token_data: TokenData = TokenData.model_validate(claims)
    except ValidationError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid token")
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="something went wrong")

    return token_data

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)