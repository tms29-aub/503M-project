#!/bin/bash

# Ports to terminate processes on
PORTS=(3000 5000 5001 5002 5003 5004)

echo "Killing processes running on the following ports: ${PORTS[@]}"

for PORT in "${PORTS[@]}"
do
    # Find the PID of the process running on the port
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        echo "Killing process on port $PORT with PID $PID"
        kill -9 $PID
    else
        echo "No process found running on port $PORT"
    fi
done

echo "All specified ports are now free."
