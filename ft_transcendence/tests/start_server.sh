#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 {re|prod}"
    exit 1
fi

MAKE_RULE=$1

echo "Starting the server..."
make clean > /dev/null 2>&1
make $MAKE_RULE > /dev/null 2>&1 &  # Lance le serveur en arrière-plan

echo "Waiting for Docker containers to be ready..."
until docker ps --filter "name=ctn_nginx" --filter "status=running" | grep -q "ctn_nginx"; do
    sleep 1
done
echo "Docker containers are up and running!"
