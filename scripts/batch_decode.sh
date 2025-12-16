#!/bin/bash
# Batch decode all .prst files to JSON

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DECODER="$SCRIPT_DIR/prst_decoder.py"

if [ $# -eq 0 ]; then
    echo "Usage: batch_decode.sh <directory>"
    echo "  Decodes all .prst files in the specified directory to JSON"
    exit 1
fi

DIR="$1"

if [ ! -d "$DIR" ]; then
    echo "Error: Directory not found: $DIR"
    exit 1
fi

COUNT=0
SUCCESS=0
FAILED=0

echo "Decoding .prst files in: $DIR"
echo "----------------------------------------"

for file in "$DIR"/*.prst; do
    if [ -f "$file" ]; then
        COUNT=$((COUNT + 1))
        if python3 "$DECODER" "$file"; then
            SUCCESS=$((SUCCESS + 1))
        else
            FAILED=$((FAILED + 1))
        fi
    fi
done

echo "----------------------------------------"
echo "Total: $COUNT files"
echo "Success: $SUCCESS"
echo "Failed: $FAILED"
