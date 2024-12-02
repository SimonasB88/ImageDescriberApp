#!/bin/bash
python3 -m venv venv
sleep 1
source venv/bin/activate
sleep 1
cd app
sleep 1
pip install -r requirements.txt --upgrade
sleep 1
uvicorn main:app --reload
sleep 1