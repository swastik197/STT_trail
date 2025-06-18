#!/bin/bash

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Install dependencies if not already installed
pip install -r requirements.txt

# Start the server
uvicorn server:app --host 0.0.0.0 --port 5000 --reload 