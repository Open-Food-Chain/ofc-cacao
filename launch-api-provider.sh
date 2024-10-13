#!/bin/bash

# Navigate to the api-provider directory
cd api-provider || exit 1

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is not installed. Please install tmux and try again."
    exit 1
fi

# Start a new tmux session named 'api-provider-session'
tmux new-session -d -s api-provider-session

# Send the 'docker-compose up' command to the tmux session
tmux send-keys -t api-provider-session "docker-compose up" C-m

# Attach to the tmux session to see the Docker Compose output
tmux attach-session -t api-provider-session
