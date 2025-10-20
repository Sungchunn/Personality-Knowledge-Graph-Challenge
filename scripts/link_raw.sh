#!/usr/bin/env bash
# Create symbolic link from external Data directory to data/raw_pdf

set -e

DATA_DIR="/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Data"
LINK_TARGET="./data/raw_pdf"

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Data directory does not exist: $DATA_DIR"
    exit 1
fi

# Remove existing link if present
if [ -L "$LINK_TARGET" ]; then
    echo "Removing existing symlink: $LINK_TARGET"
    rm "$LINK_TARGET"
fi

# Create parent directory
mkdir -p "$(dirname "$LINK_TARGET")"

# Create symlink
ln -s "$DATA_DIR" "$LINK_TARGET"

echo "Created symlink: $LINK_TARGET -> $DATA_DIR"
ls -lh "$LINK_TARGET"
