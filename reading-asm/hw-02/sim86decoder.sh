#!/bin/bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <file.asm>" >&2
    exit 1
fi

strip_comments() {
    sed 's/;.*//' "$1" | grep -v '^\s*$'
}

ASM_FILE=$1

echo "Assembling '$ASM_FILE'..."
echo "======== ASM File Content: ========"
strip_comments "$ASM_FILE"


if [[ ! -f "$ASM_FILE" ]]; then
    echo "Error: File '$ASM_FILE' not found." >&2
    exit 1
fi

BASE=$(basename "${ASM_FILE%.*}")
OUTPUT_FILE="${BASE}.bin"

mkdir -p binaries test

nasm -f bin "$ASM_FILE" -o "binaries/$OUTPUT_FILE"

PYTHON_RESULT="$(python3 decoder.py "binaries/$OUTPUT_FILE")"
echo "======== Decoded Result: ========"
echo "$PYTHON_RESULT"

echo "$PYTHON_RESULT" > "test/$BASE-decoded.bin"

nasm -f bin "test/$BASE-decoded.bin" -o "test/$BASE-roundtrip.bin"

echo "======== Comparison: ========"
if cmp "binaries/$OUTPUT_FILE" "test/$BASE-roundtrip.bin"; then
    echo "✅ SUCCESS: decoded output reassembles to identical bytes."
else
    echo "❌ FAILURE: round-trip binary differs from the original."
fi
