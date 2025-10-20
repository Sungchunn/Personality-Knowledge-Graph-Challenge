#!/bin/bash
# Process multiple novels through the knowledge graph pipeline
# Usage: ./scripts/process_all_novels.sh [max_passages]

set -e  # Exit on error

PROJECT_ROOT="/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project"
cd "$PROJECT_ROOT"

# Activate virtual environment
source .venv/bin/activate

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable not set"
    echo "Please run: export ANTHROPIC_API_KEY='your-api-key-here'"
    exit 1
fi

# Get max passages parameter (default: 50 for demo, or "all" for full run)
MAX_PASSAGES="${1:-50}"

echo "=========================================="
echo "Multi-Novel Knowledge Graph Pipeline"
echo "=========================================="
echo "Max passages per novel: $MAX_PASSAGES"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Define novels to process
declare -A NOVELS=(
    ["dune"]="data/jsonl/dune-1-herbert-brian-herbert-frank-dune-libgen-li.jsonl"
    ["bladerunner"]="data/jsonl/bladerunner-1-dick-philip-kindred-do-androids-dream-of-electric-sheep-libgen-li-2.jsonl"
    ["foundation"]="data/jsonl/foundation-1-asimov-isaac-foundation-libgen-li.jsonl"
)

# Process each novel
for novel_name in "${!NOVELS[@]}"; do
    input_file="${NOVELS[$novel_name]}"
    timestamp=$(date '+%Y%m%d_%H%M%S')
    output_dir="outputs/${novel_name}_run_${timestamp}"

    echo "=========================================="
    echo "Processing: $novel_name"
    echo "Input: $input_file"
    echo "Output: $output_dir"
    echo "=========================================="

    # Check if input file exists
    if [ ! -f "$input_file" ]; then
        echo "Warning: Input file not found: $input_file"
        echo "Skipping $novel_name"
        echo ""
        continue
    fi

    # Run pipeline
    if [ "$MAX_PASSAGES" = "all" ]; then
        echo "Running full pipeline (all passages)..."
        python -m src.pipeline.cli \
            --input-file "$input_file" \
            --output-root "$output_dir" \
            all
    else
        echo "Running pipeline with max $MAX_PASSAGES passages..."
        python -m src.pipeline.cli \
            --input-file "$input_file" \
            --output-root "$output_dir" \
            --max-passages "$MAX_PASSAGES" \
            all
    fi

    # Check if pipeline succeeded
    if [ $? -eq 0 ]; then
        echo "✓ Successfully processed $novel_name"
        echo "  Output directory: $output_dir"
        echo "  View graph: open $output_dir/graph.html"
        echo ""
    else
        echo "✗ Error processing $novel_name"
        echo ""
    fi
done

echo "=========================================="
echo "Pipeline Complete"
echo "=========================================="
echo "Summary of outputs:"
ls -d outputs/*_run_* 2>/dev/null | tail -3
echo ""
echo "To view results:"
echo "  - Triples: cat outputs/NOVEL_run_*/triples_canonical.jsonl | head"
echo "  - Traits: cat outputs/NOVEL_run_*/traits_final.jsonl | head"
echo "  - Graph: open outputs/NOVEL_run_*/graph.html"
echo "  - Metrics: cat outputs/NOVEL_run_*/metrics.json"
