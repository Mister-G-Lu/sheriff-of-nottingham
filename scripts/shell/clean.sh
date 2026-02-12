#!/bin/bash
# Cleanup script for Sheriff of Nottingham project
# Removes temporary files, caches, and coverage artifacts

echo "🧹 Cleaning Sheriff of Nottingham project..."
echo ""
echo "Before cleanup:"
du -sh .
echo ""

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove pytest cache
echo "Removing pytest cache..."
rm -rf .pytest_cache

# Remove coverage artifacts
echo "Removing coverage artifacts..."
rm -rf htmlcov
rm -f .coverage
rm -f .coverage.*

# Remove test backup files
echo "Removing test backup files..."
find tests -name "*.backup" -delete 2>/dev/null

# Remove log files and logs directory
echo "Removing log files..."
rm -f *.log
rm -rf logs/
rm -rf core/logs/ 2>/dev/null

# Remove macOS system files
echo "Removing macOS system files..."
find . -name ".DS_Store" -delete 2>/dev/null

# Remove virtual environment (if exists)
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo "Removing virtual environment..."
    rm -rf venv .venv
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "After cleanup:"
du -sh .
echo ""
echo "Size breakdown:"
du -sh .git tests characters core ui ai_strategy data 2>/dev/null
echo ""
echo "💡 Tip: Run './scripts/shell/package.sh' to create a distribution zip"
