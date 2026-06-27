#!/bin/bash

# run using 'sh start.sh'

echo "Checking and installing dependencies..."

pip3 install -r requirements.txt

start_app() {
    python3 app.py &
    APP_PID=$!
    echo "--- Finance App Started (PID: $APP_PID) ---"
}

start_app

echo "Commands: [r] Restart | [q] Quit"

while true; do
    read -r -n 1 user_input
    echo "" 

    if [[ "$user_input" == "r" ]]; then
        echo "Restarting Betting Application..."
        kill -TERM $APP_PID 2>/dev/null
        wait $APP_PID 2>/dev/null
        start_app
    elif [[ "$user_input" == "q" ]]; then
        echo "Exiting..."
        kill -TERM $APP_PID 2>/dev/null
        exit 0
    fi
done