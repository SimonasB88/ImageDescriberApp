from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import vision
from google.oauth2 import service_account
from pymongo import MongoClient
import datetime
import os

# Initialize FastAPI app
app = FastAPI()

# Mount the static files directory
app.mount("/styles", StaticFiles(directory="styles"), name="output.css")

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
async def analyze_image(file: UploadFile = File(...)):
    # Read the image file
    image_content = await file.read()
    
    # Create an image object for Google Vision API
    image = vision.Image(content=image_content)

    # Call the Vision API
    response = client.label_detection(image=image)

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

    return {"labels": results}

# Initialize MongoDB client
mongo_client = MongoClient('mongodb://localhost:27017/')

db = mongo_client["vision_api_history"]
collection = db["vision_api_history_collection"]

# Load the service account key file and initialize the Vision client
credentials = service_account.Credentials.from_service_account_file('responsive-amp-431818-n3-76277e347b39.json')
client = vision.ImageAnnotatorClient(credentials=credentials)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
