#!/usr/bin/env bash
# Wrapper script to run PDF ingestion with standard settings

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Activate virtual environment
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Run 'make setup' first."
    exit 1
fi

source .venv/bin/activate

# Default paths
PDF_ROOT="${PDF_ROOT:-/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Data}"
OUT_ROOT="${OUT_ROOT:-./data}"
OCR_MODE="${OCR_MODE:-auto}"
MIN_CHARS="${MIN_CHARS:-1200}"
MAX_CHARS="${MAX_CHARS:-2000}"
OVERLAP="${OVERLAP:-200}"

echo "====================================="
echo "PDF Ingestion Pipeline"
echo "====================================="
echo "PDF Root:    $PDF_ROOT"
echo "Output Root: $OUT_ROOT"
echo "OCR Mode:    $OCR_MODE"
echo "Chunk Size:  $MIN_CHARS - $MAX_CHARS chars"
echo "Overlap:     $OVERLAP chars"
echo "====================================="
echo ""

python -m src.ingest.cli \
    --pdf-root "$PDF_ROOT" \
    --out-root "$OUT_ROOT" \
    --ocr "$OCR_MODE" \
    --min-chars "$MIN_CHARS" \
    --max-chars "$MAX_CHARS" \
    --overlap "$OVERLAP"

echo ""
echo "====================================="
echo "Ingestion complete!"
echo "====================================="
