from fastapi.testclient import TestClient
from routes import create_access_token, verify_token, read_index_html, get_current_user
from main import app

client = TestClient(app)

def test_create_access_token():
    token = create_access_token(data={"sub": "  [email protected]"})
    assert token is not None
    
def test_verify_token():
    token = create_access_token(data={"sub": "  [email protected]"})
    verified_token = verify_token(token)
    assert verified_token is not None
    
def test_read_index_html():
    response = read_index_html()
    assert response is not None
    
def test_get_current_user():
    token = create_access_token(data={"sub": "  [email protected]"})
    current_user = get_current_user(token)
    assert current_user is not None