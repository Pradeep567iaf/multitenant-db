#!/usr/bin/env bash
# Render build script to avoid Rust compilation issues

# Exit on any error
set -e

# Upgrade pip first
pip install --upgrade pip

# Install with pre-compiled wheels only
pip install --only-binary=:all: -r requirements-prod.txt

echo "✅ Dependencies installed successfully!"
