from fastapi.testclient import TestClient
from auth import create_access_token, verify_token
from main import app
import os
from dotenv import load_dotenv

client = TestClient(app)

def test_create_access_token():
    data = {"sub": "test"}
    token = create_access_token(data)
    assert verify_token(token) == "test"
    
def test_verify_token():
    data = {"sub": "test"}
    token = create_access_token(data)
    assert verify_token(token) == "test"