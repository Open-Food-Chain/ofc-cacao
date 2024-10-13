#!/bin/bash

# Navigate to the orgs directory
cd orgs || exit 1

# Load the .env environment file if it exists
if [ -f .env ]; then
    source .env
    echo "Loaded .env environment variables."
else
    echo ".env environment file not found."
fi

# Run the Python script
python3 populate-db.py