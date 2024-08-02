#!/bin/bash

# start-pintech.sh
# This script starts the Pintech API with its MongoDB dependency.
# Ensure Docker is running before executing this script.

set -eu

# Add any necessary environment variables here
export PANTS_CONCURRENT=True 2>/dev/null

# Check if debug mode is requested
DEBUG_MODE=0
if [ "$#" -eq 1 ] && [ "$1" = "--debug" ]; then
    DEBUG_MODE=1
fi

# Start the API with its DB dependency
if [ $DEBUG_MODE -eq 1 ]; then
    echo "Starting pintech_api in debug mode..."
    pants run :run_api_with_db_debug
else
    echo "Starting pintech_api in normal mode..."
    pants run :run_api_with_db
fi
