#!/bin/bash
echo "Current directory:"
pwd
echo "Listing contents:"
ls -lah
env > /etc/environment
service cron start
uvicorn main:app --host 0.0.0.0 --port 8000 --reload