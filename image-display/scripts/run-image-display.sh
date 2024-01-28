#!/bin/bash

# Relative path from the root folder of the project to the image-display binary
EXECUTABLE="./image-display/bin/image-display"

# Run the command with sudo and pass all script arguments to the executable
sudo $EXECUTABLE "$@"