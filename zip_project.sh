#!/bin/bash

# Sheriff of Nottingham - Project Zipper
# Creates a clean zip file of the project, excluding unnecessary files

PROJECT_NAME="sheriff-of-nottingham"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_NAME="${PROJECT_NAME}_${TIMESTAMP}.zip"

echo "=========================================="
echo "Sheriff of Nottingham - Project Zipper"
echo "=========================================="
echo ""

# Move to parent directory
cd "$(dirname "$0")/.." || exit 1

echo "Current directory: $(pwd)"
echo "Creating zip: ${ZIP_NAME}"
echo ""

# Create zip excluding unnecessary files
zip -r "${ZIP_NAME}" "${PROJECT_NAME}" \
    -x "${PROJECT_NAME}/__pycache__/*" \
    -x "${PROJECT_NAME}/*/__pycache__/*" \
    -x "${PROJECT_NAME}/*/*/__pycache__/*" \
    -x "${PROJECT_NAME}/.git/*" \
    -x "${PROJECT_NAME}/.DS_Store" \
    -x "${PROJECT_NAME}/*/.DS_Store" \
    -x "${PROJECT_NAME}/build/*" \
    -x "${PROJECT_NAME}/dist/*" \
    -x "${PROJECT_NAME}/*.spec" \
    -x "${PROJECT_NAME}/.venv/*" \
    -x "${PROJECT_NAME}/venv/*" \
    -x "${PROJECT_NAME}/*.pyc"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Success! Created: ${ZIP_NAME}"
    echo ""
    echo "File location: $(pwd)/${ZIP_NAME}"
    echo "File size: $(du -h "${ZIP_NAME}" | cut -f1)"
    echo ""
    echo "You can now share this file!"
else
    echo ""
    echo "✗ Error creating zip file"
    exit 1
fi
