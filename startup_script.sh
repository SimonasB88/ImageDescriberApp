#!/bin/bash
python3 -m venv venv
source venv/bin/activate
cd app
pip install -r requirements.txt --upgrade