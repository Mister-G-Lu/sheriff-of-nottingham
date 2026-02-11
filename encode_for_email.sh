#!/bin/bash
# Encode the project as base64 text to bypass email filters
# The output is a plain text file that can be safely emailed

echo "Sheriff of Nottingham - Email-Safe Encoder"
echo "=========================================="
echo ""

# Create the zip file first
echo "Step 1: Creating zip file..."
./zip_project.sh

# Find the most recent zip file
ZIPFILE=$(ls -t ../sheriff-of-nottingham_*.zip 2>/dev/null | head -1)

if [ -z "$ZIPFILE" ]; then
    echo "Error: No zip file found!"
    exit 1
fi

echo "Found: $ZIPFILE"
echo ""

# Encode to base64
OUTPUT_FILE="../sheriff-encoded.txt"
echo "Step 2: Encoding to base64..."
base64 -i "$ZIPFILE" -o "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    SIZE=$(wc -c < "$OUTPUT_FILE" | tr -d ' ')
    SIZE_MB=$(echo "scale=2; $SIZE / 1024 / 1024" | bc)
    
    echo ""
    echo "=========================================="
    echo "SUCCESS! Encoded file created:"
    echo "=========================================="
    echo "File: $OUTPUT_FILE"
    echo "Size: ${SIZE_MB} MB"
    echo ""
    echo "This is a plain text file that can be safely emailed."
    echo ""
    echo "To decode (recipient instructions):"
    echo "-----------------------------------"
    echo "Save the attached text file and run:"
    echo "  base64 -d -i sheriff-encoded.txt -o sheriff-of-nottingham.zip"
    echo "  unzip sheriff-of-nottingham.zip"
    echo ""
    
    # Create a decoder script for the recipient
    DECODER="../decode_sheriff.sh"
    cat > "$DECODER" << 'EOF'
#!/bin/bash
# Decoder script for Sheriff of Nottingham
# Usage: ./decode_sheriff.sh sheriff-encoded.txt

if [ -z "$1" ]; then
    echo "Usage: ./decode_sheriff.sh <encoded-file.txt>"
    exit 1
fi

ENCODED_FILE="$1"
OUTPUT_ZIP="sheriff-of-nottingham.zip"

echo "Decoding $ENCODED_FILE..."
base64 -d -i "$ENCODED_FILE" -o "$OUTPUT_ZIP"

if [ $? -eq 0 ]; then
    echo "✓ Decoded to $OUTPUT_ZIP"
    echo ""
    echo "Extracting..."
    unzip -q "$OUTPUT_ZIP"
    echo "✓ Extracted to sheriff-of-nottingham/"
    echo ""
    echo "Done! You can now use the project."
else
    echo "✗ Error decoding file"
    exit 1
fi
EOF
    
    chmod +x "$DECODER"
    echo "Also created: $DECODER"
    echo "Send both files to make it easy for the recipient!"
    
else
    echo "✗ Error encoding file"
    exit 1
fi
