from pymongo import MongoClient
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["image_describer_db"]
user_collection = db["users"]
history_collection = db["vision_api_history_collection"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def add_user(user_data: dict):
    user_data["hashed_password"] = get_password_hash(user_data["password"])
    del user_data["password"]
    return user_collection.insert_one(user_data)
    
def find_user(username: str):
    return user_collection.find_one({"username": username})
