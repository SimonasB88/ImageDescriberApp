from fastapi.testclient import TestClient
from models import get_password_hash, verify_password, add_user, find_user
from main import app
from pymongo import MongoClient

client = TestClient(app)
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["your_database_name"]
user_collection = db["users"]

client = TestClient(app)

def test_get_password_hash():
    password = "password"
    password_hash = get_password_hash(password)
    assert verify_password(password, password_hash) == True
    
def test_add_user():
    user_data = {
        "username": "test_user",
        "password": "password",
        "email": "test@test.com"
    }
    add_user(user_data)
    
    user = find_user("test_user")
    assert user["username"] == "test_user"
    assert user["email"] == "test@test.com"
    assert verify_password("password", user["hashed_password"]) == True
    
    user_collection.delete_one({"username": "test_user"})
    
def test_find_user():
    user_data = {
        "username": "test_user",
        "password": "password",
        "email": "test@test.com"
    }
    add_user(user_data)
    
    user = find_user("test_user")
    assert user["username"] == "test_user"
    assert user["email"] == "test@test.com"
    assert verify_password("password", user["hashed_password"]) == True
    
    user_collection.delete_one({"username": "test_user"})
    
