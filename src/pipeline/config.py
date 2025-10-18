"""
Pipeline configuration and settings.
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class PipelineConfig:
    """Configuration for the extraction pipeline."""

    # Input/Output paths
    input_jsonl_root: Path
    output_root: Path

    # LLM settings
    model_name: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.0
    max_tokens: int = 4096

    # Quality thresholds
    confidence_threshold: float = 0.65
    min_span_length: int = 10
    max_span_length: int = 500

    # Processing limits
    max_passages_per_book: Optional[int] = None
    batch_size: int = 10

    # Relation types (schema)
    allowed_relations: list = None

    def __post_init__(self):
        """Set default allowed relations if not provided."""
        if self.allowed_relations is None:
            self.allowed_relations = [
                "PERSON",
                "LOCATION",
                "ORGANIZATION",
                "EVENT",
                "RELATIONSHIP",
                "OWNS",
                "WORKS_FOR",
                "LOCATED_IN",
                "PARTICIPATES_IN",
                "KNOWS",
                "FAMILY_OF",
                "FRIENDS_WITH",
                "ENEMY_OF",
                "LOVES",
                "HATES",
                "LEADS",
                "MEMBER_OF",
                "CREATED",
                "MENTIONED_IN",
            ]

        # Ensure paths are Path objects
        self.input_jsonl_root = Path(self.input_jsonl_root)
        self.output_root = Path(self.output_root)

        # Create output directory
        self.output_root.mkdir(parents=True, exist_ok=True)

    def get_prompt_path(self, name: str) -> Path:
        """Get path to a prompt template file."""
        return Path(__file__).parent.parent.parent / "prompts" / f"{name}.txt"

    def load_prompt(self, name: str) -> str:
        """Load a prompt template by name."""
        prompt_path = self.get_prompt_path(name)
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")
