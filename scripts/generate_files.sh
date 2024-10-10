#!/bin/bash

# Create the directory for Nginx files
mkdir -p ./nginx/www

# Generate a small HTML file (1KB)
echo "<html><body><h1>Small File</h1></body></html>" > ../nginx/www/small.html

# Generate a medium file (1MB)
dd if=/dev/zero of=./nginx/www/medium.html bs=1M count=1

# List the created files
echo "Files created in the nginx/www directory:"
ls -lh ./nginx/www