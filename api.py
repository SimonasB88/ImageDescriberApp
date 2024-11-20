from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import vision
from google.oauth2 import service_account
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os
import logging

# Setup logging for better debugging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Mount static files and templates directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/styles", StaticFiles(directory="styles"), name="styles")
templates = Jinja2Templates(directory="templates")

# Initialize MongoDB client
MONGO_URL = os.getenv("MONGO_URL")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["vision_api_history"]
collection = db["vision_api_history_collection"]

# Construct the credentials for Google Vision API from environment variables
credentials_info = {
    'type': os.getenv('TYPE'),
    'project_id': os.getenv('PROJECT_ID'),
    'private_key_id': os.getenv('PRIVATE_KEY_ID'),
    'private_key': os.getenv('PRIVATE_KEY').replace('\\n', '\n'),
    'client_email': os.getenv('CLIENT_EMAIL'),
    'client_id': os.getenv('CLIENT_ID'),
    'auth_uri': os.getenv('AUTH_URI'),
    'token_uri': os.getenv('TOKEN_URI'),
    'auth_provider_x509_cert_url': os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
    'client_x509_cert_url': os.getenv('CLIENT_X509_CERT_URL')
}

# Log credentials (use with caution in production)
logging.debug(f"Loaded credentials for project: {os.getenv('PROJECT_ID')}")

credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = vision.ImageAnnotatorClient(credentials=credentials)

# Function to read the index.html file
def read_index_html():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(file_path, "r") as file:
        html_content = file.read()
    return html_content

# Initialize routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=read_index_html(), status_code=200)

@app.get("/index.html", response_class=HTMLResponse)
async def serve_index_html():
    return HTMLResponse(content=read_index_html(), status_code=200)

@app.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register/", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register-completing/")
async def handle_register(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required.")

    # Check if the user already exists in the database
    user = collection.find_one({"username": username})
    if user:
        raise HTTPException(status_code=400, detail="User already exists in the database.")
    else:
        # Insert the new user into the new collection
        new_user_collection = db["users"]
        new_user_collection.insert_one({"username": username, "password": password})
        return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login-processing/")
async def handle_login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required.")

    # Check if the user exists in the database
    user = collection.find_one({"username": username, "password": password})
    if user:
        return templates.TemplateResponse("welcome.html", {"request": request, "username": username})
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

@app.post("/analyze-image/")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    try:
        # Check file size limit (e.g., 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds the 10MB limit.")
        file.seek(0)  # Reset file pointer after reading
        
        # Create an image object for Google Vision API
        image = vision.Image(content=file_content)
        
        # Call the Vision API
        response = client.label_detection(image=image)
        logging.debug(f"Google Vision API response: {response}")

        # Extract labels and their descriptions
        labels = response.label_annotations
        results = [{"description": label.description, "score": label.score} for label in labels]
        
        # Prepare data to store in MongoDB
        query_data = {
            "file_name": file.filename,
            "results": results,
            "timestamp": datetime.datetime.now()
        }
        
        # Insert the data into MongoDB
        collection.insert_one(query_data)
        logging.debug(f"Inserted data into MongoDB: {query_data}")
        
        # Return results to the user via template
        return templates.TemplateResponse("results.html", {"request": request, "labels": results})
    
    except Exception as e:
        logging.error(f"Error analyzing image: {str(e)}")
        return HTMLResponse(content=f"Error analyzing image: {str(e)}", status_code=500)

@app.get("/history/")
async def show_history(request: Request):
    try:
        # Fetch all records from MongoDB
        records = collection.find({})
        results = [
            {
                "file_name": record["file_name"],
                "results": record["results"],
                "timestamp": record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            }
            for record in records
        ]
        return templates.TemplateResponse("history.html", {"request": request, "results": results})

    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        return HTMLResponse(content=f"Error fetching history: {str(e)}", status_code=500)

# Log MongoDB connection status
try:
    mongo_client.admin.command('ping')
    logging.debug("MongoDB connected successfully")
except Exception as e:
    logging.error(f"MongoDB connection error: {e}")

# Start FastAPI app using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
