#!/bin/bash

# Azure App Service Startup Script for Django + Channels
# This script runs when your app starts on Azure

echo "Starting ConnectFlow Pro on Azure..."

# Install dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create media directories
echo "Creating media directories..."
mkdir -p media/avatars
mkdir -p media/messages/attachments
mkdir -p media/messages/voice

# Start Daphne server (for Django Channels + WebSockets)
echo "Starting Daphne server..."
daphne -b 0.0.0.0 -p 8000 connectflow.asgi:application
