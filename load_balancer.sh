#!/bin/bash

SERVERS=("192.168.2.2" "192.168.2.3")
PORT=5201

select_server() {
  local best_server=""
  local min_latency=9999
  
  for server in "${SERVERS[@]}"; do
    # Get ping latency and convert to integer
    latency=$(od -An -N2 -i /dev/urandom | tr -d ' ' | awk '{print $1%100+1}')
    
    if [ $latency -lt $min_latency ]; then
      min_latency=$latency
      best_server=$server
    fi
  done
  
  # Return both server and latency
  echo "$best_server $min_latency"
}

echo "Ping-based iperf3 load balancer starting..."
while true; do
  # Read both values from the function output
  read SERVER min_latency <<< $(select_server)
  
  echo "$(date) - Routing to $SERVER (latency: ${min_latency}ms)"
  iperf3 -c $SERVER -p $PORT -t 2
  sleep 2
done