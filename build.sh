#!/usr/bin/env bash
# Render.com build script

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
# Use --run-syncdb to handle existing tables gracefully
python manage.py migrate --run-syncdb --noinput 2>&1 | grep -v "relation.*already exists" || python manage.py migrate tools_forms --fake-initial --noinput

echo "Build complete!"
