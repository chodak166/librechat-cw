#!/bin/bash

# Function to handle cleanup on SIGINT and SIGTERM
cleanup() {
  echo "Caught SIGINT or SIGTERM. Cleaning up and exiting..."
  run=0
  pkill -TERM -P $$
  exit 0
}

# Set trap for SIGINT and SIGTERM
trap cleanup INT TERM
run=1
cd /app

# If workflow directory does not exist or is empty
if [ ! -d "workflows" ] || [ -z "$(ls -A workflows)" ]; then
  echo "No workflows found. Populating with defaults."
  mkdir -p /app/workflows 2>/dev/null ||:
  cp -r /app/workflows.default/* /app/workflows/
fi

# Loop to start the workflow runner
while [ $run -eq 1 ]; do
  echo "Starting workflow-runner"

  # Source environment variables from .env file
  if [ -f .env ]; then
    export $(grep -v '^#' .env | grep _KEY | xargs)
  fi

  # Start the Python script using exec to replace the shell
  exec python3 file-server.py dashboard ${AI_WORKFLOWS_DASHBOARD_PORT:-8002} &
  exec python3 tree-clone-server.py &
  exec python3 app.py

  # If exec fails, we exit the loop
  echo "Python script exited. Restarting..."
  sleep 1
done
