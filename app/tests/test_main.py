import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200

def test_read_login(client):
    response = client.get("/login/")
    assert response.status_code == 200

def test_read_register(client):
    response = client.get("/register/")
    assert response.status_code == 200

def test_read_register_completing(client):
    response = client.post("/register-completing/")
    assert response.status_code == 200

def test_read_authenticate(client):
    response = client.post("/authenticate/")
    assert response.status_code == 200