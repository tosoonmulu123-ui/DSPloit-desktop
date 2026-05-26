#!/bin/bash
# Build DSPloit PC for macOS using PyInstaller

set -e

echo "=== DSPloit PC macOS Build ==="
echo ""

pip3 install -r requirements.txt
pip3 install pyinstaller

pyinstaller --onefile --windowed \
    --name "DSPloit PC" \
    --add-data "payloads:payloads" \
    main.py

echo ""
echo "Build complete! Check dist/ folder."
