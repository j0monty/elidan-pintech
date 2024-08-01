#!/usr/bin/env bash
# Assumes it's run from the repository root!

set -eux

./pants export ::

# Set your IDE to use the virtual environment output above!
