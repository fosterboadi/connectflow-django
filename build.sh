#!/usr/bin/env bash
# Render.com build script
set -o errexit
set -o pipefail

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
# Fake the tools_forms initial migration if tables already exist
python manage.py migrate tools_forms 0001 --fake-initial --noinput

# Then run all other migrations normally
python manage.py migrate --noinput

echo "Build complete!"
