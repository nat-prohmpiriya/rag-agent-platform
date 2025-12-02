#!/bin/bash

# Kill process running on a specific port
# Usage: ./kill-port.sh <port>

if [ -z "$1" ]; then
    echo "Usage: ./kill-port.sh <port>"
    echo "Example: ./kill-port.sh 8000"
    exit 1
fi

PORT=$1

# Find and kill process on the specified port
PID=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PID" ]; then
    echo "No process found on port $PORT"
    exit 0
fi

echo "Killing process $PID on port $PORT..."
kill -9 $PID 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Successfully killed process on port $PORT"
else
    echo "Failed to kill process on port $PORT"
    exit 1
fi
