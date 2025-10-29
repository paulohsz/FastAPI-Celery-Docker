#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! PGPASSWORD=postgres pg_isready -h db -U postgres > /dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL is ready!"

# Check if database exists, if not create it
if ! PGPASSWORD=postgres psql -h db -U postgres -lqt | cut -d \| -f 1 | grep -qw appdb; then
    echo "Creating database appdb..."
    PGPASSWORD=postgres psql -h db -U postgres -c "CREATE DATABASE appdb;"
    echo "Database created!"
else
    echo "Database appdb already exists."
fi

echo "Initializing database tables..."
python init_db.py

echo "Installing taskipy..."
pip install --no-cache-dir taskipy==1.14.1 || echo "Warning: taskipy installation failed, continuing anyway..."

echo "Starting application..."
exec "$@"
