from fastapi import FastAPI, File, UploadFile
from google.cloud import vision
from google.oauth2 import service_account
from pymongo import MongoClient
import datetime

# Initialize FastAPI app
app = FastAPI()

# Initialize homepage route
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Image Analysis API!"}

# Initialize MongoDB client
mongo_client = MongoClient('mongodb://localhost:27017/')

db = mongo_client["vision_api_history"]
collection = db["vision_api_history_collection"]

# Load the service account key file and initialize the Vision client
credentials = service_account.Credentials.from_service_account_file('responsive-amp-431818-n3-76277e347b39.json')
client = vision.ImageAnnotatorClient(credentials=credentials)

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
    "timestamp": datetime.datetime.utcnow()
    }

    # Insert the data into MongoDB
    collection.insert_one(query_data)

    return {"labels": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
