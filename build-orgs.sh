#!/bin/bash

# Navigate to the api-provider directory
cd orgs || exit 1

# Iterate through subdirectories
for folder in */; do
    # Remove trailing slash to get the folder name
    folder_name="${folder%/}"

    # Check if the folder contains a Dockerfile
    if [ -f "${folder_name}/Dockerfile" ]; then
        echo "Building Docker image for ${folder_name}..."
        
        # Build the Docker image with the folder name as the tag
        docker build -t "${folder_name}" "${folder_name}"

        if [ $? -eq 0 ]; then
            echo "Image for ${folder_name} built successfully."
        else
            echo "Error building image for ${folder_name}."
        fi
    else
        echo "Skipping ${folder_name} - No Dockerfile found."
    fi
done
