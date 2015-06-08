#!/bin/bash
while true; do
    inotifywait -e modify *.py;
    python curvebeats.py
    echo "Rendered..."
    sleep 1
done
