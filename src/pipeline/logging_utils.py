"""
Structured logging utilities for pipeline tracing.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from contextlib import contextmanager


class PipelineLogger:
    """Structured logger that writes trace events to JSONL."""

    def __init__(self, output_dir: Path, log_file: str = "trace.jsonl"):
        """
        Initialize pipeline logger.

        Args:
            output_dir: Directory to write log file
            log_file: Name of log file
        """
        self.output_dir = Path(output_dir)
        self.log_path = self.output_dir / log_file
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize log file
        if not self.log_path.exists():
            self.log_path.touch()

    def log(
        self,
        level: str,
        stage: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Write a log entry.

        Args:
            level: Log level (INFO, WARNING, ERROR)
            stage: Pipeline stage name
            message: Log message
            metadata: Additional structured data
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "stage": stage,
            "message": message,
        }

        if metadata:
            entry["metadata"] = metadata

        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def info(self, stage: str, message: str, **metadata) -> None:
        """Log info message."""
        self.log("INFO", stage, message, metadata if metadata else None)

    def warning(self, stage: str, message: str, **metadata) -> None:
        """Log warning message."""
        self.log("WARNING", stage, message, metadata if metadata else None)

    def error(self, stage: str, message: str, **metadata) -> None:
        """Log error message."""
        self.log("ERROR", stage, message, metadata if metadata else None)

    @contextmanager
    def stage_context(self, stage_name: str):
        """
        Context manager for tracking stage execution.

        Usage:
            with logger.stage_context("extract_triples"):
                # do work
        """
        start_time = datetime.now(timezone.utc)
        self.info(stage_name, f"Starting stage: {stage_name}")

        try:
            yield
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            self.info(
                stage_name,
                f"Completed stage: {stage_name}",
                duration_seconds=duration,
            )
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            self.error(
                stage_name,
                f"Failed stage: {stage_name}",
                error=str(e),
                duration_seconds=duration,
            )
            raise


def create_run_summary(
    output_dir: Path,
    stages_completed: list,
    total_duration: float,
    artifacts: Dict[str, str],
    stats: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Create a run summary JSON file.

    Args:
        output_dir: Output directory
        stages_completed: List of completed stage names
        total_duration: Total runtime in seconds
        artifacts: Dict mapping artifact names to file paths
        stats: Optional statistics dictionary
    """
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stages_completed": stages_completed,
        "total_duration_seconds": total_duration,
        "artifacts": artifacts,
        "statistics": stats or {},
    }

    summary_path = output_dir / "run_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
