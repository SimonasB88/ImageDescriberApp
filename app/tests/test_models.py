import pytest
from models import get_password_hash, verify_password, add_user, find_user
from pymongo import MongoClient

@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient("mongodb://localhost:27017/")
    yield client
    client.close()

@pytest.fixture(scope="module")
def db(mongo_client):
    db = mongo_client["your_database_name"]
    yield db

@pytest.fixture(scope="module")
def user_collection(db):
    collection = db["users"]
    yield collection
    collection.delete_many({})  # Clean up after tests

def test_get_password_hash():
    password = "password"
    password_hash = get_password_hash(password)
    assert verify_password(password, password_hash) == True

def test_add_user(user_collection):
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

def test_find_user(user_collection):
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
