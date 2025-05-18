#!/bin/bash

# Configuration
SERVER1="192.168.2.2:8000"
SERVER2="192.168.2.3:8000"
LISTEN_PORT=8001
SELECTED_FILE="/tmp/selected_server.txt"
CURRENT_TARGET=""

SOCAT_PID_FILE="/tmp/lb_socat.pid"

# Function to get ping latency (ms)
get_ping() {
    ping -c 1 -W 1 "$1" | awk -F '/' 'END {print ($5 == "") ? 9999 : $5}'
}

# Function to start socat forwarding
start_socat() {
    local HOST=$1
    local PORT=$2
    echo "Starting new socat to $HOST:$PORT"
    
    # Start socat in background and save its PID
    socat TCP-LISTEN:$LISTEN_PORT,reuseaddr,fork TCP:$HOST:$PORT &
    echo $! > "$SOCAT_PID_FILE"
}

# Function to stop socat
stop_socat() {
    if [[ -f "$SOCAT_PID_FILE" ]]; then
        PID=$(cat "$SOCAT_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping old socat process ($PID)"
            kill $PID
        fi
        rm -f "$SOCAT_PID_FILE"
    fi
}

# Background latency checker
check_servers() {
    while true; do
        HOST1=$(echo $SERVER1 | cut -d: -f1)
        HOST2=$(echo $SERVER2 | cut -d: -f1)

        PING1=$(get_ping "$HOST1")
        PING2=$(get_ping "$HOST2")

        echo "Ping $HOST1 average latency: $PING1 ms"
        echo "Ping $HOST2 average latency: $PING2 ms"

        if (( $(echo "$PING1 < $PING2" | bc -l) )); then
            BEST_SERVER="$SERVER1"
        else
            BEST_SERVER="$SERVER2"
        fi

        echo "Best server based on ping: $BEST_SERVER"

        if [[ "$BEST_SERVER" != "$CURRENT_TARGET" ]]; then
            echo "Changing server: $CURRENT_TARGET → $BEST_SERVER"
            CURRENT_TARGET="$BEST_SERVER"
            echo "$CURRENT_TARGET" > "$SELECTED_FILE"

            stop_socat
            HOST=$(echo "$CURRENT_TARGET" | cut -d: -f1)
            PORT=$(echo "$CURRENT_TARGET" | cut -d: -f2)
            start_socat "$HOST" "$PORT"
        fi

        sleep 10
    done
}


# Start background checker
echo "Starting load balancer on port $LISTEN_PORT..."
check_servers
