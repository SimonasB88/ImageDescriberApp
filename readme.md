# Image Describer App

A simple Python application, that is used for any image describing by Google Cloud API OCR Label Detection. After the image upload, the application outputs the image labels using OCR (Optical character recognition) technology, and adds the Google confidence scores for all the words, that has been described.

A confidence score in Google Cloud Vision API represents how certain the model is about the label it assigned to an object in an image. It's a number between 0 and 1, where a higher score indicates greater confidence. For example, if the model labels an object as "cat" with a confidence score of 0.95, it means the model is 95% confident that the object is a cat. This score helps users gauge the reliability of the label provided by the model.

More information about [Google Vision API and OCR Label Detection](https://cloud.google.com/vision/docs/features-list).

## Installation

