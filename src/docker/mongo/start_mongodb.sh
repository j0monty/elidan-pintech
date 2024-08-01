#!/bin/bash

set -eux

# Check if MongoDB container is running
if ! docker compose -f src/docker/mongo/docker-compose.yml ps | grep -q "pintech_mongodb.*Up"; then
    echo "MongoDB container is not running. Starting it now..." 2>/dev/null
    docker compose -f src/docker/mongo/docker-compose.yml up -d

    # Wait for MongoDB to be ready
    echo "Waiting for MongoDB to be ready..."  2>/dev/null
    sleep 5  # Adjust this value if needed
fi

echo "MongoDB is ready." 2>/dev/null
