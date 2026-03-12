#!/usr/bin/env bash
# exit on error
set -o errexit

# Update pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Agar aapko custom build steps chahiye toh yahan add karein
echo "Build process completed successfully!"