import pytest
from datetime import timedelta
from auth import create_access_token, verify_token
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@pytest.fixture
def token_data():
    return {"sub": "testuser"}

@pytest.fixture
def token(token_data):
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

def test_create_access_token(token_data):
    token = create_access_token(data=token_data)
    assert token is not None

def test_verify_token(token_data, token):
    decoded_username = verify_token(token)
    assert decoded_username == token_data["sub"]

def test_verify_token_invalid():
    with pytest.raises(Exception):
        verify_token("invalid_token")

def test_token_expiration(token_data):
    token = create_access_token(data=token_data, expires_delta=timedelta(seconds=1))
    import time
    time.sleep(2)  # Wait for the token to expire
    with pytest.raises(Exception):
        verify_token(token)
