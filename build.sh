#!/usr/bin/env bash
# Render.com build script

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
# First run the safe forms migration
python manage.py migrate_forms_safe

# Then run all other migrations
python manage.py migrate --noinput

echo "Build complete!"
