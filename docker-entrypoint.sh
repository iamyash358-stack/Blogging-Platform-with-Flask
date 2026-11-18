#!/bin/sh
set -e
export FLASK_APP=wsgi.py

# Create migrations on first run only if they were not generated locally.
if [ ! -d migrations ]; then
  flask db init
  flask db migrate -m "initial schema"
fi

flask db upgrade
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile - wsgi:app
