# Image Describer App

A simple Python application, that is used for any image describing by Google Cloud API OCR Label Detection. After the image upload, the application outputs the image labels using OCR (Optical character recognition) technology, and adds the Google confidence scores for all the words, that has been described.

A confidence score in Google Cloud Vision API represents how certain the model is about the label it assigned to an object in an image. It's a number between 0 and 1, where a higher score indicates greater confidence. For example, if the model labels an object as "cat" with a confidence score of 0.95, it means the model is 95% confident that the object is a cat. This score helps users gauge the reliability of the label provided by the model.

The Google Cloud Vision API's confidence score can be used in various daily life applications:

- Photo Organization: Automatically categorize photos in personal albums (e.g., identifying pets, locations, events).
- Retail: Enhance online shopping by tagging products with high confidence.
- Security: Identify and categorize objects in surveillance footage.
- Healthcare: Assist in diagnosing medical images with high-confidence labels.
- Social Media: Improve content tagging and search functionality.

These applications leverage the confidence score to ensure accurate and reliable results.

More information about [Google Vision API and OCR Label Detection](https://cloud.google.com/vision/docs/features-list).

## Generating a Google Vision API Key

To use the Google Vision API in this project, you'll need to generate an API key. Follow these steps:

1. **Go to the Google Cloud Console**:
   - Navigate to the [Google Cloud Console](https://console.cloud.google.com/).

2. **Create a New Project**:
   - Click on the project drop-down at the top of the page.
   - Select "New Project."
   - Enter a name for your project and click "Create."

3. **Enable the Vision API**:
   - After the project is created, make sure it is selected.
   - Go to the [Vision API page](https://console.cloud.google.com/apis/library/vision.googleapis.com).
   - Click "Enable" to enable the Vision API for your project.

4. **Create Credentials**:
   - In the left-hand menu, navigate to "APIs & Services" > "Credentials."
   - Click on "Create Credentials" and select "API key."
   - Your new API key will be created and displayed. Copy it for later use.

5. **Restrict Your API Key (Optional but recommended)**:
   - Click on the "Edit API key" (pencil icon) next to your newly created key.
   - Under "API restrictions," select "Restrict key."
   - Add the Google Vision API to the list of APIs that the key can access.
   - Save the changes.

6. **Store the API Key Securely to your gitignored `.env` file**:
   - Refactor your API key as the `.env.example` file is defined. Place the `.json` retrieved from Google vision API securely and never expose it publicly.

You can now use this API key in your application to make requests to the Google Vision API.

## Installation of the app

App is dockerized (make sure you have Docker) and uses makefile shortcuts, so to launch it, simply run from root:

```
make build
```

After build is finished, run:
```
make up
```
## Additional commands for app managing

```
# Stop the services
make down

# Restart the services
make restart

# Show the status of the services
make status

# Tail logs of the services
make logs

# Run the tests
make test
```

## Tehcnologies used

- FastAPI
- Jinja 2
- MongoDB
- Docker
- Pytest
- Google Cloud API