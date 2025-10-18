"""
Tests for Pydantic schemas.
"""

import pytest
from pydantic import ValidationError
from src.pipeline.schemas import (
    TextSpan,
    Triple,
    PersonalityTrait,
    PersonalityProfile,
)


def test_text_span_valid():
    """Test valid TextSpan creation."""
    span = TextSpan(text="Hello world", start=0, end=11)
    assert span.text == "Hello world"
    assert span.start == 0
    assert span.end == 11


def test_text_span_invalid_offsets():
    """Test TextSpan with invalid offsets."""
    with pytest.raises(ValidationError):
        # end <= start should fail
        TextSpan(text="test", start=10, end=5)


def test_triple_valid():
    """Test valid Triple creation."""
    span = TextSpan(text="Alice knows Bob", start=0, end=15)
    triple = Triple(
        subject="Alice",
        relation="KNOWS",
        object="Bob",
        confidence=0.95,
        evidence_span=span,
    )

    assert triple.subject == "Alice"
    assert triple.relation == "KNOWS"
    assert triple.object == "Bob"
    assert triple.confidence == 0.95


def test_triple_invalid_confidence():
    """Test Triple with invalid confidence."""
    with pytest.raises(ValidationError):
        # Confidence > 1.0 should fail
        Triple(
            subject="A",
            relation="REL",
            object="B",
            confidence=1.5,
        )


def test_personality_trait_valid():
    """Test valid PersonalityTrait creation."""
    span = TextSpan(text="Evidence", start=0, end=8)
    trait = PersonalityTrait(
        trait_name="openness",
        score=0.75,
        confidence=0.8,
        evidence_spans=[span],
    )

    assert trait.trait_name == "openness"
    assert trait.score == 0.75
    assert trait.confidence == 0.8


def test_personality_trait_invalid_name():
    """Test PersonalityTrait with invalid trait name."""
    with pytest.raises(ValidationError):
        PersonalityTrait(
            trait_name="invalid_trait",
            score=0.5,
            confidence=0.7,
        )


def test_personality_profile_valid():
    """Test valid PersonalityProfile creation."""
    traits = [
        PersonalityTrait(trait_name="openness", score=0.7, confidence=0.8),
        PersonalityTrait(trait_name="conscientiousness", score=0.6, confidence=0.7),
        PersonalityTrait(trait_name="extraversion", score=0.5, confidence=0.6),
        PersonalityTrait(trait_name="agreeableness", score=0.8, confidence=0.9),
        PersonalityTrait(trait_name="neuroticism", score=0.4, confidence=0.7),
    ]

    profile = PersonalityProfile(
        person_name="Alice",
        traits=traits,
    )

    assert profile.person_name == "Alice"
    assert len(profile.traits) == 5


def test_personality_profile_missing_traits():
    """Test PersonalityProfile with missing traits."""
    # Only 3 traits instead of 5
    traits = [
        PersonalityTrait(trait_name="openness", score=0.7, confidence=0.8),
        PersonalityTrait(trait_name="conscientiousness", score=0.6, confidence=0.7),
        PersonalityTrait(trait_name="extraversion", score=0.5, confidence=0.6),
    ]

    with pytest.raises(ValidationError):
        PersonalityProfile(
            person_name="Bob",
            traits=traits,
        )
