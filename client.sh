#!/bin/sh

LB_ADDRESS="192.168.2.4:8001"
REQUESTS=10000

for i in $(seq 1 "$REQUESTS"); do
  echo "Request $i:"
  curl -X GET "http://$LB_ADDRESS/"
  sleep 1
done