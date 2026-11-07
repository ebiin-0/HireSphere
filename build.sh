#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r django_backend/requirements.txt
python django_backend/manage.py collectstatic --no-input
python django_backend/manage.py migrate
