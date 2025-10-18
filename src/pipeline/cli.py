"""
Master CLI for the knowledge graph extraction pipeline.
"""

import argparse
from pathlib import Path
from datetime import datetime


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Knowledge Graph Extraction and Personality Analysis Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--input-jsonl-root",
        type=Path,
        default="/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project/data/jsonl",
        help="Root directory containing input JSONL files",
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        help="Output directory for pipeline artifacts (default: auto-generated)",
    )

    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.65,
        help="Minimum confidence threshold for filtering",
    )

    parser.add_argument(
        "--model-name",
        type=str,
        default="claude-3-5-sonnet-20241022",
        help="LLM model name",
    )

    parser.add_argument(
        "--max-passages",
        type=int,
        help="Maximum passages to process per book (for testing)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Pipeline command")

    # Subcommand: extract
    subparsers.add_parser(
        "extract", help="Extract raw triples from passages"
    )

    # Subcommand: canonicalize
    subparsers.add_parser(
        "canonicalize", help="Canonicalize entities and merge aliases"
    )

    # Subcommand: traits
    subparsers.add_parser(
        "traits", help="Infer Big Five personality traits"
    )

    # Subcommand: graph
    subparsers.add_parser(
        "graph", help="Build property graph and generate visualizations"
    )

    # Subcommand: eval
    subparsers.add_parser(
        "eval", help="Evaluate and generate metrics"
    )

    # Subcommand: all
    subparsers.add_parser(
        "all", help="Run complete end-to-end pipeline"
    )

    return parser


def main():
    """Main CLI entrypoint."""
    parser = create_parser()
    args = parser.parse_args()

    # Auto-generate output directory if not specified
    if args.output_root is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_root = Path(f"./outputs/run_{timestamp}")

    # Validate input directory
    if not args.input_jsonl_root.exists():
        print(f"Error: Input directory does not exist: {args.input_jsonl_root}")
        return 1

    # Create output directory
    args.output_root.mkdir(parents=True, exist_ok=True)

    print(f"Pipeline Configuration:")
    print(f"  Input:       {args.input_jsonl_root}")
    print(f"  Output:      {args.output_root}")
    print(f"  Confidence:  {args.confidence_threshold}")
    print(f"  Model:       {args.model_name}")
    print()

    if not args.command:
        parser.print_help()
        return 1

    # Import pipeline modules (will be implemented in next steps)
    try:
        from .config import PipelineConfig

        config = PipelineConfig(
            input_jsonl_root=args.input_jsonl_root,
            output_root=args.output_root,
            confidence_threshold=args.confidence_threshold,
            model_name=args.model_name,
            max_passages_per_book=args.max_passages,
        )

        # Execute command (implementations will be added in step 4)
        if args.command == "extract":
            print("Extract command not yet implemented")
            return 1
        elif args.command == "canonicalize":
            print("Canonicalize command not yet implemented")
            return 1
        elif args.command == "traits":
            print("Traits command not yet implemented")
            return 1
        elif args.command == "graph":
            print("Graph command not yet implemented")
            return 1
        elif args.command == "eval":
            print("Eval command not yet implemented")
            return 1
        elif args.command == "all":
            print("All command not yet implemented")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
