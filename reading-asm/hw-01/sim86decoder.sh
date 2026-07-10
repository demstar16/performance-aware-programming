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

echo "$PYTHON_RESULT" > "test/$BASE-test.asm"

echo "======== Comparison: ========"
if diff <(strip_comments "$ASM_FILE") "test/$BASE-test.asm" > "test/$BASE-diff.txt"; then
    echo "✅ SUCCESS: decoded output matches the original."
else
    echo "❌ FAILURE: decoded output differs from the original. See test/$BASE-diff.txt"
fi
