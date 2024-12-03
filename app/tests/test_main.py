from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    
def test_read_login():
    response = client.get("/login/")
    assert response.status_code == 200
    
def test_read_register():
    response = client.get("/register/")
    assert response.status_code == 200
    
def test_read_register_completing():
    response = client.post("/register-completing/")
    assert response.status_code == 200
    
def test_read_authenticate():
    response = client.post("/authenticate/")
    assert response.status_code == 200