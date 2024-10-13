#!/bin/bash

./build-api-provider.sh
./build-orgs.sh
./launch-api-provider.sh
./launch-orgs.sh

# Navigate to the orgs directory
cd orgs || exit 1

# Load the .env environment file if it exists
if [ -f .env ]; then
    source .env
    echo ${CHAIN_API_PORT}
    echo "Loaded .env environment variables."
else
    echo ".env environment file not found."
fi

# Run the Python script
python3 e2e.py