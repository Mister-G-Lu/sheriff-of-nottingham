#!/bin/bash
# Pre-commit checks for Sheriff of Nottingham
# Run this before committing: ./scripts/shell/pre-commit.sh

set -e  # Exit on error

# Step 1: Ruff linting
echo "🔍 Step 1/3: Linting with Ruff..."
ruff check --fix .
echo "   ✅ Linting complete"
echo ""

# Step 2: Ruff formatting
echo "🎨 Step 2/3: Formatting with Ruff..."
ruff format .
echo "   ✅ Formatting complete"
echo ""

# Step 3: Run tests
echo "🧪 Step 3/3: Running tests..."
pytest tests/ -q
echo "   RUN SUCCESS    "
echo ""