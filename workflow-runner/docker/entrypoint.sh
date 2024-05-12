#!/bin/sh

cd /app

# if workflow directory does not exists or is empty
if [ ! -d "workflow" ] || [ -z "$(ls -A workflow)" ]; then
  echo "No workflows found. Populating with defaults."
  mkdir -p /app/workflows 2>/dev/null ||:
  cp -r /app/workflows.default/*.py /app/workflows/
fi


while [ 1 ]; do
  echo "Starting workflow-runner"

  python3 app.py
  sleep 1

done
