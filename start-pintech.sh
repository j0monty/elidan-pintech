#!/bin/bash

# start-pintech.sh
# This script starts the Pintech API with its MongoDB dependency.
# Ensure Docker is running before executing this script.

set -e

# Add any necessary environment variables here
export PANTS_CONCURRENT=True 2>/dev/null
export BETTER_EXCEPTIONS=1


#initialize variables
DEBUG_MODE=0
LOG_JSON_FORMAT=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            DEBUG_MODE=1
            shift # Remove --debug from processing
            ;;
        --json_logging)
            JSON_LOGGING=true
            shift # Remove --json_logging from processing
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set LOG_JSON_FORMAT based on JSON_LOGGING flag
if [ "$JSON_LOGGING" = true ]; then
    export LOG_JSON_FORMAT=true
    echo "JSON logging enabled."
else
    unset LOG_JSON_FORMAT
    echo "JSON logging disabled."
fi

# Start the API with its DB dependency
if [ $DEBUG_MODE -eq 1 ]; then
    echo "Starting pintech_api in debug mode..."
    pants run :run_api_with_db_debug
else
    echo "Starting pintech_api in normal mode..."
    pants run :run_api_with_db
fi
