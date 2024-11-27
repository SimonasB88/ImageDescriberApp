from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from google.cloud import vision
from google.oauth2 import service_account
from pydantic import BaseModel
from datetime import timedelta
from auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import find_user, add_user, verify_password, history_collection
from dotenv import load_dotenv
import os
import logging
import datetime
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

# Setup logging for better debugging
logging.basicConfig(level=logging.DEBUG)

router = APIRouter()
templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router.mount("/styles", StaticFiles(directory="styles"), name="styles")
router.mount("/static", StaticFiles(directory="static"), name="static")

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

logging.debug(f"Loaded credentials for project: {os.getenv('PROJECT_ID')}")

credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = vision.ImageAnnotatorClient(credentials=credentials)

class Token(BaseModel):
    access_token: str
    token_type: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token)
    if not username:
        raise credentials_exception
    user = find_user(username)
    if user is None:
        raise credentials_exception
    return user

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register/", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register-completing/")
async def handle_register(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    if not username or not password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username and password are required."}
        )
    user = find_user(username)
    if user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "User already exists in the database."})
    else:
        add_user({"username": username, "password": password})
        return templates.TemplateResponse("login.html", {"request": request, "message": "Thank you for registration, you may login!"})

@router.post("/authenticate", response_class=HTMLResponse)
async def handle_login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    if not username or not password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Username and password are required."}
        )

    user = find_user(username)
    if user and verify_password(password, user["hashed_password"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        response = templates.TemplateResponse(
            "index.html",
            {"request": request, "message": f"Successfully logged in {username}!"}
        )
        response.headers["Authorization"] = f"Bearer {access_token}"
        response.headers["Set-Cookie"] = f"Authorization={access_token}; Path=/; HttpOnly"
        return response
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password."}
        )


@router.post("/analyze-image/")
async def analyze_image(request: Request, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds the 10MB limit.")
        file.seek(0)  # Reset file pointer after reading

        image = vision.Image(content=file_content)
        response = client.label_detection(image=image)
        logging.debug(f"Google Vision API response: {response}")

        labels = response.label_annotations
        results = [{"description": label.description, "score": label.score} for label in labels]

        query_data = {
            "file_name": file.filename,
            "results": results,
            "timestamp": datetime.datetime.now(),
            "user_id": current_user["_id"]
        }

        history_collection.insert_one(query_data)
        logging.debug(f"Inserted data into MongoDB: {query_data}")

        return templates.TemplateResponse("results.html", {"request": request, "labels": results})

    except Exception as e:
        logging.error(f"Error analyzing image: {str(e)}")
        return HTMLResponse(content=f"Error analyzing image: {str(e)}", status_code=500)

@router.get("/history/")
async def show_history(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        records = history_collection.find({"user_id": current_user["_id"]})
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
    
@router.get("/logout/")
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response

def read_index_html():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(file_path, "r") as file:
        html_content = file.read()
    return html_content

# Log MongoDB connection status
try:
    client.admin.command('ping')
    logging.debug("MongoDB connected successfully")
except Exception as e:
    logging.error(f"MongoDB connection error: {e}")