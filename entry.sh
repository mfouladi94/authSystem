#!/bin/bash

# Apply Django database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Django development server
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
