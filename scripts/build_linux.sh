#!/bin/bash
# Build DSPloit PC for Linux using PyInstaller

set -e

echo "=== DSPloit PC Linux Build ==="
echo ""

pip3 install -r requirements.txt
pip3 install pyinstaller

pyinstaller --onefile \
    --name "dsploit-pc" \
    --add-data "payloads:payloads" \
    main.py

echo ""
echo "Build complete! Check dist/ folder."
