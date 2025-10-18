"""
Evaluation and metrics generation for pipeline outputs.
"""

import networkx as nx
from pathlib import Path
from typing import Dict, Any
from collections import Counter

from .config import PipelineConfig
from .io_utils import load_jsonl, load_graphml, save_json
from .logging_utils import PipelineLogger


def compute_triple_stats(triples: list) -> Dict[str, Any]:
    """Compute statistics on extracted triples."""
    if not triples:
        return {}

    # Confidence distribution
    confidences = [t.get("confidence", 0.0) for t in triples]
    avg_confidence = sum(confidences) / len(confidences)

    # Relation types
    relations = [t.get("relation") for t in triples]
    relation_counts = Counter(relations)

    return {
        "total_triples": len(triples),
        "avg_confidence": round(avg_confidence, 3),
        "min_confidence": round(min(confidences), 3),
        "max_confidence": round(max(confidences), 3),
        "unique_relations": len(set(relations)),
        "relation_distribution": dict(relation_counts.most_common(10)),
    }


def compute_personality_stats(profiles: list) -> Dict[str, Any]:
    """Compute statistics on personality profiles."""
    if not profiles:
        return {}

    # Trait averages
    trait_scores = {
        "openness": [],
        "conscientiousness": [],
        "extraversion": [],
        "agreeableness": [],
        "neuroticism": [],
    }

    for profile in profiles:
        for trait in profile.get("traits", []):
            trait_name = trait["trait_name"]
            if trait_name in trait_scores:
                trait_scores[trait_name].append(trait["score"])

    avg_scores = {
        trait: round(sum(scores) / len(scores), 3) if scores else 0.0
        for trait, scores in trait_scores.items()
    }

    return {
        "total_profiles": len(profiles),
        "avg_trait_scores": avg_scores,
    }


def compute_graph_stats(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """Compute network statistics on the graph."""
    stats = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "density": round(nx.density(G), 4),
    }

    # Degree statistics
    degrees = dict(G.degree())
    if degrees:
        stats["avg_degree"] = round(sum(degrees.values()) / len(degrees), 2)
        stats["max_degree"] = max(degrees.values())

        # Most connected nodes
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        stats["most_connected_nodes"] = [
            {"node": node, "degree": degree} for node, degree in top_nodes
        ]

    # Connected components
    if G.number_of_nodes() > 0:
        # Convert to undirected for component analysis
        G_undirected = G.to_undirected()
        stats["num_components"] = nx.number_connected_components(G_undirected)

        largest_cc = max(nx.connected_components(G_undirected), key=len)
        stats["largest_component_size"] = len(largest_cc)

    return stats


def run_evaluate(config: PipelineConfig, logger: PipelineLogger) -> Path:
    """
    Run evaluation and generate metrics.

    Args:
        config: Pipeline configuration
        logger: Pipeline logger

    Returns:
        Path to output metrics.json file
    """
    with logger.stage_context("evaluate"):
        metrics = {
            "pipeline_config": {
                "model_name": config.model_name,
                "confidence_threshold": config.confidence_threshold,
            }
        }

        # Triple statistics
        triples_path = config.output_root / "triples_canonical.jsonl"
        if triples_path.exists():
            logger.info("evaluate", f"Computing triple statistics")
            triples = load_jsonl(triples_path)
            metrics["triple_stats"] = compute_triple_stats(triples)

        # Personality statistics
        traits_path = config.output_root / "traits_final.jsonl"
        if traits_path.exists():
            logger.info("evaluate", f"Computing personality statistics")
            profiles = load_jsonl(traits_path)
            metrics["personality_stats"] = compute_personality_stats(profiles)

        # Graph statistics
        graph_path = config.output_root / "graph.graphml"
        if graph_path.exists():
            logger.info("evaluate", f"Computing graph statistics")
            G = load_graphml(graph_path)
            metrics["graph_stats"] = compute_graph_stats(G)

        # Save metrics
        output_path = config.output_root / "metrics.json"
        save_json(metrics, output_path, indent=2)

        logger.info("evaluate", f"Saved metrics to {output_path}")

        return output_path
