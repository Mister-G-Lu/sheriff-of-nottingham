#!/bin/bash
# Package script for Sheriff of Nottingham
# Creates a distribution zip with all git-tracked files (similar to git archive)

# Automatically change to repository root if we're in the scripts directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to repository root
cd "$REPO_ROOT" || exit 1

echo "📦 Packaging Sheriff of Nottingham..."
echo "📁 Working directory: $REPO_ROOT"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Step 1: Clean development artifacts
echo "Step 1: Running cleanup..."
./scripts/shell/clean.sh
echo ""

# Step 2: Optimize git repository
echo "Step 2: Optimizing git repository..."
./scripts/shell/optimize-git.sh
echo ""

# Get repository name from git
REPO_NAME=$(basename "$REPO_ROOT")

# Define package name with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PACKAGE_NAME="../${REPO_NAME}-${TIMESTAMP}.zip"

echo "Creating package: $(basename $PACKAGE_NAME)"
echo "Output location: $(cd .. && pwd)/$(basename $PACKAGE_NAME)"
echo ""

# Count files to be included
FILE_COUNT=$(git ls-files | wc -l | tr -d ' ')
echo "Including $FILE_COUNT git-tracked files:"
echo "  ✅ All source code"
echo "  ✅ Tests and documentation"
echo "  ✅ Configuration files"
echo "  ✅ Game assets"
echo ""
echo "Automatically excluding (via .gitignore):"
echo "  ❌ __pycache__/ and *.pyc files"
echo "  ❌ Virtual environments"
echo "  ❌ .DS_Store and system files"
echo "  ❌ Build artifacts"
echo ""

# Create the zip file using git ls-files
# This respects .gitignore and only includes tracked files
echo "Packaging files..."
git ls-files | zip -q "$PACKAGE_NAME" -@ 

if [ $? -eq 0 ]; then
    PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)
    FULL_PATH="$(cd .. && pwd)/$(basename $PACKAGE_NAME)"
    echo "✅ Package created successfully!"
    echo ""
    echo "📦 Package: $(basename $PACKAGE_NAME)"
    echo "📁 Location: $FULL_PATH"
    echo "📊 Size: $PACKAGE_SIZE"
    echo ""
    echo "This package includes:"
    echo "  - All source code needed to run the game"
    echo "  - Game assets (characters, data)"
    echo "  - Configuration files"
    echo ""
    echo "To use:"
    echo "  1. Unzip the package"
    echo "  2. Install dependencies: pip install -r requirements.txt"
    echo "  3. Run the game: python main.py"
else
    echo "❌ Error creating package"
    exit 1
fi
