#!/bin/bash

# start-pintech.sh
# This script starts the Pintech API with its MongoDB dependency.
# Ensure Docker is running before executing this script.

set -eux

# Add any necessary environment variables here
export PANTS_CONCURRENT=True 2>/dev/null

# Start the API with its DB dependency
pants run :run_api_with_db

# Add any post-startup steps here if needed
