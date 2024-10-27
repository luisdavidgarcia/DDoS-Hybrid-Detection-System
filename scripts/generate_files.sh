#!/bin/bash

# Exit script on any command failure
set -e

# Create the directory for Nginx files
mkdir -p ./nginx/www

# Generate a small file (1KB)
dd if=/dev/zero of=./nginx/www/small.html bs=1K count=1 status=none

# Generate a medium file (1MB)
dd if=/dev/zero of=./nginx/www/medium.html bs=1M count=1 status=none

# List the created files with readable file sizes
echo "Files created in the nginx/www directory:"
ls -lh ./nginx/www
