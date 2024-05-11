#!/bin/sh

cd /app

while [ 1 ]; do
  echo "Starting workflow-runner"

  python3 app.py
  sleep 1

done
