from fastapi.testclient import TestClient
from routes import get_current_user, add_user, find_user
from main import app

client = TestClient(app)