from fastapi import FastAPI, File, UploadFile
from google.cloud import vision
from google.oauth2 import service_account
import io

# Initialize FastAPI app
app = FastAPI()

# Load the service account key file and initialize the Vision client
credentials = service_account.Credentials.from_service_account_file('path/to/your/service-account-file.json')
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

    return {"labels": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
