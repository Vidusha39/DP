#!/bin/bash
# Script to deploy / update Daham Pasala on PythonAnywhere

echo "=== Pulling latest changes from GitHub ==="
git pull origin main

echo "=== Activating virtual environment ==="
source venv/bin/activate

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Running database migrations ==="
python manage.py migrate

echo "=== Populating initial seed data ==="
python manage.py seed_data

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Setup complete! ==="
echo "Go to the Web tab in PythonAnywhere and click 'Reload <your-username>.pythonanywhere.com'"
