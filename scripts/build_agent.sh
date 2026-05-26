#!/bin/bash
# Build DSPloit Agent binary (requires macOS + Xcode)

set -e

echo "=== DSPloit Agent Build ==="
echo "Requires: macOS, Xcode, ldid"
echo ""

ARCH="${1:-arm64e}"
echo "Target: $ARCH"

cd "$(dirname "$0")/../agent"
make ARCH=$ARCH clean all

echo ""
echo "Build complete! Binary at: payloads/dsploit_agent_$ARCH"
