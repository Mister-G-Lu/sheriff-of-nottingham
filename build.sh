#!/bin/bash
# Universal build script for Sheriff of Nottingham GUI executable
# Works on macOS, Linux, and Windows (via Git Bash/WSL)

echo "Building Sheriff of Nottingham GUI executable..."
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    CYGWIN*|MINGW*|MSYS*)    PLATFORM=Windows;;
    *)          PLATFORM="Unknown"
esac

echo "Detected platform: $PLATFORM"
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build the GUI executable
echo "Building GUI executable..."
if [ "$PLATFORM" = "Windows" ]; then
    # Windows: use semicolon separator
    pyinstaller --onefile \
        --name "SheriffOfNottingham" \
        --add-data "characters;characters" \
        --add-data "core;core" \
        --add-data "ui;ui" \
        --add-data "data;data" \
        --hidden-import=tkinter \
        --hidden-import=tkinter.scrolledtext \
        --collect-all tkinter \
        --windowed \
        --clean \
        --noconfirm \
        gui_launcher.py
else
    # macOS/Linux: use colon separator
    pyinstaller --onefile \
        --name "SheriffOfNottingham" \
        --add-data "characters:characters" \
        --add-data "core:core" \
        --add-data "ui:ui" \
        --add-data "data:data" \
        --hidden-import=tkinter \
        --hidden-import=tkinter.scrolledtext \
        --collect-all tkinter \
        --windowed \
        --clean \
        --noconfirm \
        gui_launcher.py
fi

echo ""
echo "✅ Build complete!"
echo ""

if [ "$PLATFORM" = "Windows" ]; then
    echo "Executable: dist/SheriffOfNottingham.exe"
    echo "To test: dist\\SheriffOfNottingham.exe"
else
    echo "Executable: dist/SheriffOfNottingham"
    echo "To test: ./dist/SheriffOfNottingham"
fi

echo ""
echo "This version:"
echo "  - Opens in its own window (not terminal)"
echo "  - No shell messages or environment pollution"
echo "  - Clean, professional appearance"
echo "  - Double-click to run!"
