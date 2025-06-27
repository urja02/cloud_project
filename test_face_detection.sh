#!/bin/bash

# Test script for face detection API
# This script sends a curl request to the face_detection endpoint

# Configuration
API_URL="http://localhost:8000/face_detection"
IMAGES_DIR="../face_images_1000"

# Check if images directory exists
if [ ! -d "$IMAGES_DIR" ]; then
    echo "Error: Images directory $IMAGES_DIR not found!"
    exit 1
fi

# Get a random image file from the directory
# Find all image files (jpg, jpeg, png, etc.)
IMAGE_FILES=($(find "$IMAGES_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.bmp" -o -name "*.gif" \) | head -10))

if [ ${#IMAGE_FILES[@]} -eq 0 ]; then
    echo "Error: No image files found in $IMAGES_DIR"
    exit 1
fi

# Select a random image
RANDOM_INDEX=$((RANDOM % ${#IMAGE_FILES[@]}))
SELECTED_IMAGE="${IMAGE_FILES[$RANDOM_INDEX]}"

echo "Selected image: $SELECTED_IMAGE"
echo "Sending request to: $API_URL"

# Send the curl request
curl -X POST \
     -F "file=@$SELECTED_IMAGE" \
     "$API_URL" \
     -H "Content-Type: multipart/form-data" \
     -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n"

echo ""
echo "Request completed!" 