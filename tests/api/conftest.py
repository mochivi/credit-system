import pytest
import jwt
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from ecs.app import app
from ecs.core.config import settings
from ecs.models.schemas.token import PrincipalType


@pytest.fixture
def test_client():
    """Create a TestClient for testing FastAPI endpoints."""
    return TestClient(app)


@pytest.fixture
def user_token():
    """Generate a valid user JWT token for testing."""
    to_encode = {
        "sub": "12345678-1234-5678-1234-567812345678",  # User ID
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(tz=timezone.utc),
        "typ": PrincipalType.user
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


@pytest.fixture
def auth_headers(user_token):
    """Create authorization headers with the user token."""
    return {"Authorization": f"Bearer {user_token}"}
