#!/bin/bash

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Provide instructions to the user
echo "Setup complete. Activate the virtual environment with 'source .venv/bin/activate'"