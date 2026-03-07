#!/bin/bash
# Build and publish to PyPI
# Usage: ./build.sh

set -e  # Exit on error

echo "=========================================="
echo "  Yuque SDK - Build & Publish Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# PyPI Token (from environment variable)
# SECURITY: Never hardcode tokens! Use: export PYPI_TOKEN="your-token-here"
if [ -z "$PYPI_TOKEN" ]; then
    print_error "PYPI_TOKEN environment variable is not set!"
    echo "  Please run: export PYPI_TOKEN='your-pypi-token'"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
python_version=$(python --version 2>&1)
echo "  $python_version"
print_status "Python version check passed"

# Step 2: Install build tools
echo ""
echo "Step 2: Installing build tools..."
uv pip install build twine
print_status "Build tools installed"

# Step 3: Clean old builds
echo ""
echo "Step 3: Cleaning old builds..."
rm -rf dist/ build/ *.egg-info/
print_status "Old builds cleaned"

# Step 4: Install dependencies
echo ""
echo "Step 4: Installing dependencies..."
uv pip install -e ".[dev]"
print_status "Dependencies installed"

# Step 5: Run linting
echo ""
echo "Step 5: Running linter (ruff)..."
uv run ruff check src/yuque/
print_status "Linting passed"

# Step 6: Run unit tests
echo ""
echo "Step 6: Running unit tests..."
uv run pytest tests/test_client.py -v
print_status "Unit tests passed"

# Step 7: Build the package
echo ""
echo "Step 7: Building package..."
uv run python -m build
echo "Build artifacts:"
ls -la dist/
print_status "Package built successfully"

# Step 8: Verify the build
echo ""
echo "Step 8: Verifying package..."
uv run twine check dist/*
print_status "Package verification passed"

# Step 9: Upload to PyPI
echo ""
echo "Step 9: Uploading to PyPI..."
uv run twine upload dist/* -u __token__ -p "$PYPI_TOKEN"
print_status "Successfully uploaded to PyPI!"

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}  Build & Publish Complete!${NC}"
echo "=========================================="
echo ""
echo "Package published to: https://pypi.org/project/yuque-sdk/"
echo ""
echo "To install:"
echo "  pip install yuque-sdk"
echo ""
