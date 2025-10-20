#!/bin/bash
# Process a single novel through the knowledge graph pipeline
# Usage: ./scripts/process_individual.sh <novel_name> [max_passages]
#   novel_name: dune, bladerunner, foundation, neuromancer, dune2, foundation2, foundation3
#   max_passages: number or "all" (default: 50)

set -e

PROJECT_ROOT="/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
cd "$PROJECT_ROOT"

source .venv/bin/activate

# Note: API key should be in .env file (OPENAI_API_KEY or ANTHROPIC_API_KEY)

# Parse arguments
NOVEL_NAME="${1:-dune}"
MAX_PASSAGES="${2:-50}"

# Define available novels (bash 3.x compatible)
get_novel_path() {
    case "$1" in
        dune)
            echo "data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl"
            ;;
        bladerunner)
            echo "data/jsonl/bladerunner-1-dick-philip-kindred-do-androids-dream-of-electric-sheep-libgen-li-2.jsonl"
            ;;
        foundation)
            echo "data/jsonl/foundation-1-asimov-isaac-foundation-libgen-li.jsonl"
            ;;
        neuromancer)
            echo "data/jsonl/cyberpunk-1-gibson-william-neuromancer-libgen-li-2.jsonl"
            ;;
        dune2)
            echo "data/jsonl/dune-2-herbert-brian-herbert-frank-dune-messiah-libgen-li.jsonl"
            ;;
        foundation2)
            echo "data/jsonl/foundation-2-asimov-isaac-foundation-and-empire-libgen-li.jsonl"
            ;;
        foundation3)
            echo "data/jsonl/foundation-3-asimov-isaac-second-foundation-libgen-li.jsonl"
            ;;
        *)
            echo ""
            ;;
    esac
}

INPUT_FILE=$(get_novel_path "$NOVEL_NAME")

# Validate novel name
if [ -z "$INPUT_FILE" ]; then
    echo "Error: Unknown novel '$NOVEL_NAME'"
    echo "Available novels: dune, bladerunner, foundation, neuromancer, dune2, foundation2, foundation3"
    exit 1
fi
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_DIR="outputs/${NOVEL_NAME}_run_${TIMESTAMP}"

echo "=========================================="
echo "Processing: $NOVEL_NAME"
echo "Input: $INPUT_FILE"
echo "Output: $OUTPUT_DIR"
echo "Max passages: $MAX_PASSAGES"
echo "=========================================="

# Run pipeline
if [ "$MAX_PASSAGES" = "all" ]; then
    python -m src.pipeline.cli \
        --input-file "$INPUT_FILE" \
        --output-root "$OUTPUT_DIR" \
        all
else
    python -m src.pipeline.cli \
        --input-file "$INPUT_FILE" \
        --output-root "$OUTPUT_DIR" \
        --max-passages "$MAX_PASSAGES" \
        all
fi

echo ""
echo "✓ Complete! Results saved to: $OUTPUT_DIR"
echo ""
echo "Quick commands:"
echo "  View graph:   open $OUTPUT_DIR/graph.html"
echo "  View triples: cat $OUTPUT_DIR/triples_canonical.jsonl | head -10"
echo "  View traits:  cat $OUTPUT_DIR/traits_final.jsonl | head -5"
echo "  View metrics: cat $OUTPUT_DIR/metrics.json"
