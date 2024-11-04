from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates  # Add this import
from google.cloud import vision
from google.oauth2 import service_account
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the static files directory
app.mount("/styles", StaticFiles(directory="styles"), name="styles")

# Initialize Jinja2 templates directory
templates = Jinja2Templates(directory="templates")  # Add this line

# Function to read the index.html file
def read_index_html():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(file_path, "r") as file:
        html_content = file.read()
    return html_content

# Initialize the server that returns HTML at root
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=read_index_html(), status_code=200)

# Serve index.html for /index.html path as well
@app.get("/index.html", response_class=HTMLResponse)
async def serve_index_html():
    return HTMLResponse(content=read_index_html(), status_code=200)

# Function to analyze the image and store the results in MongoDB
@app.post("/analyze-image/")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    # Read the image file
    image_content = await file.read()
    
    # Create an image object for Google Vision API
    image = vision.Image(content=image_content)

    # Call the Vision API
    try:
        response = client.label_detection(image=image)
    except Exception as e:
        return HTMLResponse(content=f"Error calling Vision API: {str(e)}", status_code=500)

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
    try:
        collection.insert_one(query_data)
    except Exception as e:
        return HTMLResponse(content=f"Error inserting into MongoDB: {str(e)}", status_code=500)

    # Render the results template with the labels
    return templates.TemplateResponse("results.html", {"request": request, "labels": results})

@app.get("/history/")
async def show_history(request: Request):
    # Fetch all the records from MongoDB
    records = collection.find({})
    
    # Prepare the results to send to the template
    results = [
        {
            "file_name": record["file_name"],
            "results": record["results"],
            "timestamp": record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        }
        for record in records
    ]

    return templates.TemplateResponse("history.html", {"request": request, "results": results})


# Initialize MongoDB client
MONGO_URL = os.getenv("MONGO_URL")

mongo_client = MongoClient(MONGO_URL)
db = mongo_client["vision_api_history"]
collection = db["vision_api_history_collection"]

# Construct the credentials from environment variables
credentials_info = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),  # Replace escaped \n with actual newlines
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN")
}

credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = vision.ImageAnnotatorClient(credentials=credentials)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
