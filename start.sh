#!/bin/bash

# Function to start your run.py
start_app() {
    # Run in background and suppress "Terminated" messages
    python3 run.py &
    APP_PID=$!
    echo "--- Finance App Started (PID: $APP_PID) ---"
}

# Initial start
start_app

echo "Commands: [r] Restart | [q] Quit"

while true; do
    # Read 1 character of input
    read -r -n 1 user_input
    echo "" # Move to new line

    if [[ "$user_input" == "r" ]]; then
        echo "Restarting Finance Application..."
        # Kill the specific process group to ensure child processes die
        kill -TERM $APP_PID 2>/dev/null
        wait $APP_PID 2>/dev/null
        start_app
    elif [[ "$user_input" == "q" ]]; then
        echo "Exiting..."
        kill -TERM $APP_PID 2>/dev/null
        exit 0
    fi
done