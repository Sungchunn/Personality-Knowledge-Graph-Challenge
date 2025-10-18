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

    # Import pipeline modules
    try:
        import time
        from .config import PipelineConfig
        from .logging_utils import PipelineLogger, create_run_summary
        from .extract_triples import run_extract
        from .canonicalize import run_canonicalize
        from .infer_personality import run_personality
        from .qa_filters import apply_filters
        from .build_graph import run_build_graph
        from .viz import run_viz
        from .evaluate import run_evaluate
        from .io_utils import load_jsonl, save_jsonl

        config = PipelineConfig(
            input_jsonl_root=args.input_jsonl_root,
            output_root=args.output_root,
            confidence_threshold=args.confidence_threshold,
            model_name=args.model_name,
            max_passages_per_book=args.max_passages,
        )

        logger = PipelineLogger(config.output_root)
        start_time = time.time()
        stages_completed = []
        artifacts = {}

        # Execute command
        if args.command == "extract":
            print("\n=== EXTRACT TRIPLES ===\n")
            output_path = run_extract(config, logger)
            artifacts["triples_raw"] = str(output_path)
            stages_completed.append("extract")

        elif args.command == "canonicalize":
            print("\n=== CANONICALIZE ENTITIES ===\n")
            output_path = run_canonicalize(config, logger)
            artifacts["triples_canonical"] = str(output_path)
            stages_completed.append("canonicalize")

        elif args.command == "traits":
            print("\n=== INFER PERSONALITY TRAITS ===\n")
            output_path = run_personality(config, logger)
            artifacts["traits_final"] = str(output_path)
            stages_completed.append("traits")

        elif args.command == "graph":
            print("\n=== BUILD GRAPH ===\n")
            graph_path = run_build_graph(config, logger)
            viz_path = run_viz(config, logger)
            artifacts["graph"] = str(graph_path)
            artifacts["graph_html"] = str(viz_path)
            stages_completed.extend(["build_graph", "viz"])

        elif args.command == "eval":
            print("\n=== EVALUATE ===\n")
            metrics_path = run_evaluate(config, logger)
            artifacts["metrics"] = str(metrics_path)
            stages_completed.append("evaluate")

        elif args.command == "all":
            print("\n=== RUNNING COMPLETE PIPELINE ===\n")

            # Stage 1: Extract triples
            print("\n--- Stage 1/7: Extract Triples ---")
            triples_raw_path = run_extract(config, logger)
            artifacts["triples_raw"] = str(triples_raw_path)
            stages_completed.append("extract")

            # Stage 2: Canonicalize entities
            print("\n--- Stage 2/7: Canonicalize Entities ---")
            triples_canon_path = run_canonicalize(config, logger)
            artifacts["triples_canonical"] = str(triples_canon_path)
            stages_completed.append("canonicalize")

            # Stage 3: Apply QA filters
            print("\n--- Stage 3/7: QA Filtering ---")
            triples = load_jsonl(triples_canon_path)
            filtered_triples = apply_filters(triples, config, logger)
            save_jsonl(filtered_triples, triples_canon_path)
            logger.info("qa_filters", f"Updated {triples_canon_path} with filtered triples")
            stages_completed.append("qa_filters")

            # Stage 4: Infer personality traits
            print("\n--- Stage 4/7: Infer Personality Traits ---")
            traits_path = run_personality(config, logger)
            artifacts["traits_final"] = str(traits_path)
            stages_completed.append("traits")

            # Stage 5: Build graph
            print("\n--- Stage 5/7: Build Property Graph ---")
            graph_path = run_build_graph(config, logger)
            artifacts["graph"] = str(graph_path)
            stages_completed.append("build_graph")

            # Stage 6: Create visualization
            print("\n--- Stage 6/7: Create Visualization ---")
            viz_path = run_viz(config, logger)
            artifacts["graph_html"] = str(viz_path)
            stages_completed.append("viz")

            # Stage 7: Evaluate
            print("\n--- Stage 7/7: Evaluate and Generate Metrics ---")
            metrics_path = run_evaluate(config, logger)
            artifacts["metrics"] = str(metrics_path)
            stages_completed.append("evaluate")

            print("\n=== PIPELINE COMPLETE ===\n")

        # Create run summary
        total_duration = time.time() - start_time
        create_run_summary(
            config.output_root,
            stages_completed,
            total_duration,
            artifacts,
        )

        print(f"\n{'='*60}")
        print(f"Pipeline completed successfully!")
        print(f"Duration: {total_duration:.1f}s")
        print(f"Output: {config.output_root}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
