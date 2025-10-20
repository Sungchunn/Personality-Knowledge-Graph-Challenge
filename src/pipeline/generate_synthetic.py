"""
Generate synthetic narrative text with ground truth knowledge graph and personality labels.

This module demonstrates how synthetic data COULD be generated for the pipeline,
with known ground truth for evaluation. However, we chose real data (Dune) for
the main implementation to test robustness to authentic complexity.

See DESIGN_REPORT.md Section 2.2 for justification.
"""

import json
import random
from typing import List, Dict, Any
from pathlib import Path


# Synthetic character templates with predefined personalities
SYNTHETIC_CHARACTERS = {
    "Princess Elena": {
        "personality": {
            "openness": 0.85,
            "conscientiousness": 0.70,
            "extraversion": 0.60,
            "agreeableness": 0.75,
            "neuroticism": 0.40
        },
        "traits": ["curious", "imaginative", "diplomatic", "compassionate"],
        "role": "royal",
        "gender": "female"
    },
    "Sir Marcus": {
        "personality": {
            "openness": 0.45,
            "conscientiousness": 0.90,
            "extraversion": 0.55,
            "agreeableness": 0.60,
            "neuroticism": 0.30
        },
        "traits": ["disciplined", "loyal", "dutiful", "brave"],
        "role": "knight",
        "gender": "male"
    },
    "Wizard Aldric": {
        "personality": {
            "openness": 0.95,
            "conscientiousness": 0.65,
            "extraversion": 0.30,
            "agreeableness": 0.50,
            "neuroticism": 0.55
        },
        "traits": ["wise", "eccentric", "reclusive", "brilliant"],
        "role": "mage",
        "gender": "male"
    },
    "General Thorne": {
        "personality": {
            "openness": 0.40,
            "conscientiousness": 0.85,
            "extraversion": 0.75,
            "agreeableness": 0.35,
            "neuroticism": 0.25
        },
        "traits": ["strategic", "commanding", "ruthless", "ambitious"],
        "role": "military",
        "gender": "male"
    },
    "Lady Aria": {
        "personality": {
            "openness": 0.70,
            "conscientiousness": 0.55,
            "extraversion": 0.80,
            "agreeableness": 0.45,
            "neuroticism": 0.60
        },
        "traits": ["charismatic", "manipulative", "charming", "cunning"],
        "role": "noble",
        "gender": "female"
    }
}

# Predefined relationships (ground truth)
GROUND_TRUTH_RELATIONSHIPS = [
    ("Princess Elena", "FAMILY_OF", "King Aldwin"),
    ("Princess Elena", "KNOWS", "Sir Marcus"),
    ("Princess Elena", "KNOWS", "Wizard Aldric"),
    ("Sir Marcus", "SERVES", "Princess Elena"),
    ("Sir Marcus", "ENEMY_OF", "General Thorne"),
    ("Wizard Aldric", "MENTORS", "Princess Elena"),
    ("Wizard Aldric", "LIVES_IN", "Tower of Mysteries"),
    ("General Thorne", "LEADS", "Shadow Army"),
    ("General Thorne", "ENEMY_OF", "Kingdom of Light"),
    ("Lady Aria", "ALLIED_WITH", "General Thorne"),
    ("Lady Aria", "KNOWS", "Princess Elena"),
    ("Sir Marcus", "LOCATED_IN", "Castle Brightstone"),
]

# Template sentences for generating narrative text
SENTENCE_TEMPLATES = {
    "FAMILY_OF": [
        "{subj} was the {relation} of {obj}, born into a lineage of power.",
        "The bond between {subj} and {obj} was unbreakable, for they were {relation}.",
        "{subj} often thought of {obj}, their beloved {relation}."
    ],
    "KNOWS": [
        "{subj} had known {obj} for many years, their paths crossing often.",
        "In the great hall, {subj} greeted {obj} with familiarity.",
        "{subj} and {obj} were well acquainted through their shared experiences."
    ],
    "SERVES": [
        "{subj} pledged loyalty to {obj}, serving with unwavering dedication.",
        "Day and night, {subj} stood ready to serve {obj}.",
        "{subj}'s duty was clear: to serve {obj} until the end."
    ],
    "ENEMY_OF": [
        "{subj} despised {obj}, their enmity known throughout the land.",
        "Conflict between {subj} and {obj} was inevitable and bitter.",
        "{subj} plotted against {obj}, seeking their downfall."
    ],
    "MENTORS": [
        "{subj} taught {obj} the ancient ways, sharing wisdom earned over decades.",
        "Under {subj}'s guidance, {obj} flourished and grew in knowledge.",
        "{subj} saw great potential in {obj}, mentoring them carefully."
    ],
    "LEADS": [
        "{subj} commanded {obj} with authority and strategic brilliance.",
        "At the head of {obj}, {subj} led them into battle.",
        "{subj} was the supreme leader of {obj}, unchallenged."
    ]
}

# Personality trait templates
TRAIT_TEMPLATES = {
    "openness": {
        "high": [
            "{char} eagerly explored new ideas, always seeking knowledge beyond the familiar.",
            "Curiosity drove {char} to question everything, never satisfied with simple answers.",
            "{char}'s imagination knew no bounds, creating visions others couldn't fathom."
        ],
        "low": [
            "{char} preferred tradition and routine, uncomfortable with change.",
            "Practical matters consumed {char}'s attention, leaving no room for flights of fancy.",
            "{char} valued the tried and true, skeptical of new approaches."
        ]
    },
    "conscientiousness": {
        "high": [
            "{char} meticulously planned every detail, leaving nothing to chance.",
            "Discipline defined {char}'s every action, always prepared and organized.",
            "{char} took their duties seriously, never shirking responsibility."
        ],
        "low": [
            "{char} often acted on impulse, rarely thinking ahead.",
            "Organization was not {char}'s strength, preferring spontaneity.",
            "{char} had a relaxed approach to obligations, sometimes too relaxed."
        ]
    },
    "extraversion": {
        "high": [
            "{char} thrived in social gatherings, energized by crowds and conversation.",
            "Charisma radiated from {char}, drawing others to their presence.",
            "{char} spoke boldly and often, commanding attention naturally."
        ],
        "low": [
            "{char} preferred solitude, finding crowds draining and overwhelming.",
            "Quiet contemplation suited {char} better than boisterous company.",
            "{char} spoke only when necessary, valuing silence."
        ]
    },
    "agreeableness": {
        "high": [
            "{char} showed compassion to all, always seeking harmony over conflict.",
            "Kindness came naturally to {char}, who trusted others readily.",
            "{char} prioritized others' needs, often at their own expense."
        ],
        "low": [
            "{char} was skeptical of others' motives, guarding trust carefully.",
            "Direct and uncompromising, {char} didn't soften harsh truths.",
            "{char} put their own interests first, unapologetic in their ambition."
        ]
    },
    "neuroticism": {
        "high": [
            "{char} worried constantly, anxious thoughts plaguing their mind.",
            "Stress affected {char} deeply, emotions running high and unpredictable.",
            "{char} struggled with inner turmoil, rarely finding peace."
        ],
        "low": [
            "{char} remained calm under pressure, unshaken by adversity.",
            "Emotional stability defined {char}, who rarely let stress show.",
            "{char} faced challenges with composure, never losing their cool."
        ]
    }
}


def generate_relationship_sentences(
    subject: str,
    relation: str,
    obj: str,
    num_sentences: int = 2
) -> List[str]:
    """Generate narrative sentences for a given relationship."""
    templates = SENTENCE_TEMPLATES.get(relation, [
        "{subj} had a relationship with {obj}.",
        "{subj} and {obj} were connected in important ways."
    ])

    sentences = []
    for _ in range(num_sentences):
        template = random.choice(templates)
        sentence = template.format(
            subj=subject,
            obj=obj,
            relation=relation.lower().replace("_", " ")
        )
        sentences.append(sentence)

    return sentences


def generate_personality_sentences(
    char_name: str,
    personality: Dict[str, float],
    num_per_trait: int = 2
) -> List[str]:
    """Generate narrative sentences demonstrating personality traits."""
    sentences = []

    for trait_name, score in personality.items():
        # Determine if high or low
        level = "high" if score >= 0.5 else "low"

        templates = TRAIT_TEMPLATES.get(trait_name, {}).get(level, [
            f"{{char}} exhibited {trait_name}."
        ])

        for _ in range(num_per_trait):
            template = random.choice(templates)
            sentence = template.format(char=char_name)
            sentences.append(sentence)

    return sentences


def generate_synthetic_passages(
    num_passages: int = 20,
    min_chars: int = 800,
    max_chars: int = 1500
) -> List[Dict[str, Any]]:
    """
    Generate synthetic narrative passages with ground truth labels.

    Returns:
        List of passages, each with:
        - text: narrative content
        - ground_truth_triples: list of (subject, relation, object) tuples
        - ground_truth_personalities: dict of {char_name: {trait: score}}
    """
    passages = []

    for i in range(num_passages):
        # Select random relationships to include
        num_relations = random.randint(2, 4)
        selected_relations = random.sample(GROUND_TRUTH_RELATIONSHIPS, num_relations)

        # Select 2-3 characters to feature
        featured_chars = random.sample(list(SYNTHETIC_CHARACTERS.keys()), random.randint(2, 3))

        # Generate text
        text_parts = []

        # Add opening context
        text_parts.append(f"In the Kingdom of Light, events unfolded that would change everything.")

        # Add relationship sentences
        for subj, rel, obj in selected_relations:
            if subj in featured_chars or obj in featured_chars:
                sentences = generate_relationship_sentences(subj, rel, obj, num_sentences=1)
                text_parts.extend(sentences)

        # Add personality demonstrations
        for char in featured_chars:
            if char in SYNTHETIC_CHARACTERS:
                personality = SYNTHETIC_CHARACTERS[char]["personality"]
                # Pick 2-3 random traits to demonstrate
                traits_to_show = random.sample(list(personality.items()), random.randint(2, 3))
                for trait_name, score in traits_to_show:
                    sentences = generate_personality_sentences(
                        char, {trait_name: score}, num_per_trait=1
                    )
                    text_parts.extend(sentences)

        # Add filler to reach min length
        while len(" ".join(text_parts)) < min_chars:
            filler_char = random.choice(featured_chars)
            text_parts.append(f"{filler_char} continued their journey through the realm.")

        # Combine and truncate if needed
        full_text = " ".join(text_parts)
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "..."

        # Create ground truth labels
        ground_truth_triples = [
            {"subject": subj, "relation": rel, "object": obj, "confidence": 1.0}
            for subj, rel, obj in selected_relations
            if subj in featured_chars or obj in featured_chars
        ]

        ground_truth_personalities = {
            char: SYNTHETIC_CHARACTERS[char]["personality"]
            for char in featured_chars
            if char in SYNTHETIC_CHARACTERS
        }

        passages.append({
            "passage_id": f"synthetic_{i:03d}",
            "text": full_text,
            "ground_truth_triples": ground_truth_triples,
            "ground_truth_personalities": ground_truth_personalities,
            "featured_characters": featured_chars
        })

    return passages


def save_synthetic_data(output_dir: Path, num_passages: int = 50):
    """Generate and save synthetic data with ground truth labels."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate passages
    passages = generate_synthetic_passages(num_passages)

    # Save passages (without ground truth, for pipeline input)
    passages_for_pipeline = [
        {
            "book_id": "synthetic_novel",
            "title": "The Chronicles of the Kingdom of Light",
            "chunk_index": i,
            "text": p["text"]
        }
        for i, p in enumerate(passages)
    ]

    with open(output_dir / "synthetic_passages.jsonl", "w") as f:
        for passage in passages_for_pipeline:
            f.write(json.dumps(passage) + "\n")

    # Save ground truth separately (for evaluation)
    ground_truth = {
        "characters": SYNTHETIC_CHARACTERS,
        "relationships": GROUND_TRUTH_RELATIONSHIPS,
        "passages": [
            {
                "passage_id": p["passage_id"],
                "triples": p["ground_truth_triples"],
                "personalities": p["ground_truth_personalities"]
            }
            for p in passages
        ]
    }

    with open(output_dir / "ground_truth.json", "w") as f:
        json.dump(ground_truth, f, indent=2)

    # Save metadata
    metadata = {
        "num_passages": len(passages),
        "num_characters": len(SYNTHETIC_CHARACTERS),
        "num_ground_truth_relations": len(GROUND_TRUTH_RELATIONSHIPS),
        "generation_method": "template_based",
        "purpose": "Demonstration of synthetic data generation approach"
    }

    with open(output_dir / "synthetic_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return output_dir


if __name__ == "__main__":
    # Generate synthetic data
    output_dir = Path("data/synthetic")
    save_synthetic_data(output_dir, num_passages=50)

    print(f"✓ Synthetic data generated at {output_dir}")
    print(f"  - synthetic_passages.jsonl: Input for pipeline")
    print(f"  - ground_truth.json: Ground truth labels for evaluation")
    print(f"  - synthetic_metadata.json: Generation metadata")

    # Show sample
    with open(output_dir / "synthetic_passages.jsonl") as f:
        sample = json.loads(f.readline())

    print(f"\nSample passage:")
    print(f"  {sample['text'][:200]}...")
