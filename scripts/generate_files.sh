#!/bin/bash

set -e

mkdir -p ./nginx/www

# Generate a small file (1KB)
dd if=/dev/zero of=./nginx/www/small.html bs=1K count=1 status=none

# Generate a medium file (1MB)
dd if=/dev/zero of=./nginx/www/medium.html bs=1M count=1 status=none

echo "Files created in the nginx/www directory:"
ls -lh ./nginx/www
