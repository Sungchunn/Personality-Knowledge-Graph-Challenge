"""
Fix duplicate personality profiles in existing pipeline output by:
1. Loading canonical triples to build entity mapping
2. Normalizing personality profile names using the mapping
3. Merging duplicate profiles (keeping highest confidence traits)
4. Rebuilding graph and visualization
"""

import sys
from pathlib import Path
from collections import defaultdict
import json

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.io_utils import load_jsonl, save_jsonl
from pipeline.config import PipelineConfig
from pipeline.logging_utils import PipelineLogger
from pipeline.build_graph import run_build_graph
from pipeline.viz import run_viz

def build_entity_mapping(triples):
    """
    Build mapping of entity variants to their canonical forms.
    Uses frequency and completeness heuristics.
    """
    # Group entities by lowercased form
    variant_groups = defaultdict(set)
    entity_freq = defaultdict(int)

    for triple in triples:
        for entity in [triple["subject"], triple["object"]]:
            variant_groups[entity.lower()].add(entity)
            entity_freq[entity] += 1

    # Manual mappings for common Dune characters (applied to person_name in profiles)
    manual_profile_mappings = {
        "paul": "Paul Atreides",
        "his mother": "Lady Jessica",
        "my mother": "Lady Jessica",
        "jessica": "Lady Jessica",
        "the duke": "Leto Atreides",
        "duke": "Leto Atreides",
        "duke leto atreides": "Leto Atreides",
        "baron": "Baron Vladimir Harkonnen",
        "harkonnen": "Baron Vladimir Harkonnen",
        "vladimir harkonnen": "Baron Vladimir Harkonnen",
        "baron vladimir harkonnen": "Baron Vladimir Harkonnen",
        "gurney": "Gurney Halleck",
        "hawat": "Thufir Hawat",
        "thufir hawat": "Thufir Hawat",
        "stilgar": "Stilgar",
        "kynes": "Liet-Kynes",
        "liet-kynes": "Liet-Kynes",
        "son": "Paul Atreides",
        "his son": "Paul Atreides",
        "fremen woman": "Fremen",  # Generic
        "duke of arrakis": "Leto Atreides",
        "bene gesserit": "Bene Gesserit Sisterhood",  # Organization
        "house atreides": "House Atreides",  # Organization
        "reverend mother": "Reverend Mother Gaius Helen Mohiam",
    }

    # Build mapping: variant -> canonical
    mapping = {}

    for base, variants in variant_groups.items():
        if len(variants) == 1:
            continue

        # Check manual mapping first
        if base in manual_profile_mappings:
            canonical = manual_profile_mappings[base]
            for variant in variants:
                if variant != canonical:
                    mapping[variant] = canonical
            continue

        # Otherwise, pick longest form with highest frequency as canonical
        canonical = max(variants, key=lambda x: (len(x), entity_freq[x]))

        for variant in variants:
            if variant != canonical:
                # Only map if it's a clear substring or very similar
                if variant.lower() in canonical.lower() or canonical.lower() in variant.lower():
                    mapping[variant] = canonical

    return mapping


def merge_personality_profiles(profiles, entity_mapping):
    """
    Merge duplicate personality profiles using entity mapping.
    For duplicates, keep traits with highest confidence.
    """
    # Direct manual mappings for profile names
    manual_mappings = {
        "Paul": "Paul Atreides",
        "son": "Paul Atreides",  # Usually refers to Paul
        "Jessica": "Lady Jessica",
        "His mother": "Lady Jessica",
        "woman": "Lady Jessica",  # Context-dependent, often Jessica
        "Harkonnen": "Baron Vladimir Harkonnen",
        "Vladimir Harkonnen": "Baron Vladimir Harkonnen",
        "Duke": "Leto Atreides",
        "Duke Leto Atreides": "Leto Atreides",
        "Duke of Arrakis": "Leto Atreides",
        "uncle": "Leto Atreides",  # Context: Paul's uncle figure
    }

    # Normalize profile names
    normalized_profiles = {}

    for profile in profiles:
        person_name = profile["person_name"]

        # Apply manual mapping first
        canonical_name = manual_mappings.get(person_name, None)

        # If no manual mapping, use entity mapping from triples
        if canonical_name is None:
            canonical_name = entity_mapping.get(person_name, person_name)

        # If we already have a profile for this canonical name, merge traits
        if canonical_name in normalized_profiles:
            existing = normalized_profiles[canonical_name]

            # Merge traits, keeping highest confidence for each trait type
            existing_traits = {t["trait_name"]: t for t in existing["traits"]}
            new_traits = {t["trait_name"]: t for t in profile["traits"]}

            for trait_name, new_trait in new_traits.items():
                if trait_name not in existing_traits:
                    existing_traits[trait_name] = new_trait
                else:
                    # Keep trait with higher confidence
                    if new_trait["confidence"] > existing_traits[trait_name]["confidence"]:
                        existing_traits[trait_name] = new_trait

            existing["traits"] = list(existing_traits.values())

            # Merge source passage IDs
            existing_ids = set(existing.get("source_passage_ids", []))
            new_ids = set(profile.get("source_passage_ids", []))
            existing["source_passage_ids"] = list(existing_ids | new_ids)

        else:
            # First time seeing this canonical name
            profile_copy = profile.copy()
            profile_copy["person_name"] = canonical_name
            if person_name != canonical_name:
                profile_copy["original_name"] = person_name
            normalized_profiles[canonical_name] = profile_copy

    return list(normalized_profiles.values())


def filter_non_characters(profiles):
    """
    Remove profiles for non-character entities (objects, concepts, pronouns).
    """
    non_characters = {
        "sun", "moons", "moon", "shai-hulud", "sandworm",
        "chakobsa", "bene gesserit way", "these people",
        "mentat",  # Job title, not specific person
        "fremen",  # Group, not individual (unless specific character)
        "fremen woman",  # Generic
        "sardaukar",  # Group
        "guild",  # Organization
        "crysknife",  # Object (knife)
        "mother",  # Generic pronoun
        "my mother",  # Pronoun
        "his mother",  # Pronoun
        "natives",  # Generic group
        "royal blood",  # Concept
        "bene gesserit",  # Organization (unless specific sister)
        "house atreides",  # Organization/house
    }

    filtered = []
    for profile in profiles:
        name_lower = profile["person_name"].lower()

        # Skip if in non-character list
        if name_lower in non_characters:
            continue

        # Skip if very generic pronoun-like
        if name_lower in ["he", "she", "they", "him", "her", "them", "it", "this", "that"]:
            continue

        filtered.append(profile)

    return filtered


def main():
    output_dir = Path("/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project/outputs/run_20251020_010533")

    print("=" * 60)
    print("Fixing duplicate personality profiles...")
    print("=" * 60)

    # Load data
    print("\n1. Loading canonical triples...")
    triples = load_jsonl(output_dir / "triples_canonical.jsonl")
    print(f"   Loaded {len(triples)} triples")

    print("\n2. Loading personality profiles...")
    profiles = load_jsonl(output_dir / "traits_final.jsonl")
    print(f"   Loaded {len(profiles)} profiles")
    print(f"   Example names: {[p['person_name'] for p in profiles[:5]]}")

    # Build entity mapping
    print("\n3. Building entity mapping...")
    entity_mapping = build_entity_mapping(triples)
    print(f"   Created {len(entity_mapping)} mappings")
    print(f"   Example mappings:")
    for alias, canonical in list(entity_mapping.items())[:10]:
        print(f"     {alias} → {canonical}")

    # Merge duplicate profiles
    print("\n4. Merging duplicate profiles...")
    merged_profiles = merge_personality_profiles(profiles, entity_mapping)
    print(f"   Merged from {len(profiles)} to {len(merged_profiles)} profiles")

    # Filter non-characters
    print("\n5. Filtering non-character entities...")
    filtered_profiles = filter_non_characters(merged_profiles)
    print(f"   Filtered from {len(merged_profiles)} to {len(filtered_profiles)} profiles")

    # Save fixed profiles
    print("\n6. Saving fixed profiles...")
    save_jsonl(filtered_profiles, output_dir / "traits_final.jsonl")
    print(f"   Saved to {output_dir / 'traits_final.jsonl'}")

    # Backup old files
    import shutil
    shutil.copy(output_dir / "graph.graphml", output_dir / "graph.graphml.backup")
    shutil.copy(output_dir / "graph.html", output_dir / "graph.html.backup")
    print(f"\n7. Backed up old graph files (.backup)")

    # Rebuild graph and visualization
    print("\n8. Rebuilding graph and visualization...")
    config = PipelineConfig(
        input_jsonl_root=Path("data/jsonl"),
        output_root=output_dir,
    )
    logger = PipelineLogger(output_dir)

    run_build_graph(config, logger)
    run_viz(config, logger)

    print("\n" + "=" * 60)
    print("✓ Fixed! Open the new visualization:")
    print(f"  {output_dir / 'graph.html'}")
    print("=" * 60)

    # Print summary
    print("\nSummary of changes:")
    print(f"  Original profiles: {len(profiles)}")
    print(f"  After merging duplicates: {len(merged_profiles)}")
    print(f"  After filtering non-characters: {len(filtered_profiles)}")
    print(f"\n  Final character profiles:")
    for profile in sorted(filtered_profiles, key=lambda p: p["person_name"])[:20]:
        num_traits = len(profile["traits"])
        print(f"    - {profile['person_name']} ({num_traits} traits)")


if __name__ == "__main__":
    main()
