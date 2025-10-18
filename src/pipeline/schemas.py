"""
Pydantic schemas for pipeline data structures.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class TextSpan(BaseModel):
    """A span of text with start/end character offsets."""

    text: str = Field(..., description="The actual text span")
    start: int = Field(..., ge=0, description="Start character offset")
    end: int = Field(..., gt=0, description="End character offset")

    @field_validator("end")
    @classmethod
    def end_after_start(cls, v, info):
        """Validate that end > start."""
        if "start" in info.data and v <= info.data["start"]:
            raise ValueError("end must be greater than start")
        return v


class Triple(BaseModel):
    """A knowledge graph triple (subject, relation, object)."""

    subject: str = Field(..., min_length=1, description="Subject entity")
    relation: str = Field(..., min_length=1, description="Relation type")
    object: str = Field(..., min_length=1, description="Object entity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    evidence_span: Optional[TextSpan] = Field(
        None, description="Source text span supporting this triple"
    )
    source_passage_id: Optional[str] = Field(
        None, description="ID of source passage"
    )
    book_id: Optional[str] = Field(None, description="ID of source book")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            "subject": self.subject,
            "relation": self.relation,
            "object": self.object,
            "confidence": self.confidence,
        }

        if self.evidence_span:
            data["evidence_span"] = {
                "text": self.evidence_span.text,
                "start": self.evidence_span.start,
                "end": self.evidence_span.end,
            }

        if self.source_passage_id:
            data["source_passage_id"] = self.source_passage_id

        if self.book_id:
            data["book_id"] = self.book_id

        return data


class PersonalityTrait(BaseModel):
    """A Big Five personality trait score."""

    trait_name: str = Field(
        ...,
        description="Trait name (openness, conscientiousness, extraversion, agreeableness, neuroticism)",
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Trait score [0, 1]")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in score")
    evidence_spans: List[TextSpan] = Field(
        default_factory=list, description="Supporting text spans"
    )

    @field_validator("trait_name")
    @classmethod
    def valid_trait(cls, v):
        """Validate trait name is one of Big Five."""
        valid_traits = [
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        ]
        if v.lower() not in valid_traits:
            raise ValueError(f"trait_name must be one of {valid_traits}")
        return v.lower()


class PersonalityProfile(BaseModel):
    """Complete Big Five personality profile for a person."""

    person_name: str = Field(..., min_length=1, description="Person's name")
    traits: List[PersonalityTrait] = Field(
        ..., min_length=5, max_length=5, description="Big Five trait scores"
    )
    source_passage_ids: List[str] = Field(
        default_factory=list, description="Source passage IDs"
    )
    book_id: Optional[str] = Field(None, description="Source book ID")

    @field_validator("traits")
    @classmethod
    def all_traits_present(cls, v):
        """Validate all Big Five traits are present."""
        trait_names = {trait.trait_name for trait in v}
        required = {
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        }
        if trait_names != required:
            raise ValueError(f"All Big Five traits required: {required}")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "person_name": self.person_name,
            "traits": [
                {
                    "trait_name": t.trait_name,
                    "score": t.score,
                    "confidence": t.confidence,
                    "evidence_spans": [
                        {"text": span.text, "start": span.start, "end": span.end}
                        for span in t.evidence_spans
                    ],
                }
                for t in self.traits
            ],
            "source_passage_ids": self.source_passage_ids,
            "book_id": self.book_id,
        }


class CanonicalMapping(BaseModel):
    """Mapping from alias to canonical entity name."""

    alias: str = Field(..., description="Alias or variant name")
    canonical: str = Field(..., description="Canonical name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in mapping")
    evidence: Optional[str] = Field(
        None, description="Evidence for this canonicalization"
    )
