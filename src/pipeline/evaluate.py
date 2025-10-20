"""
Evaluation and metrics generation for pipeline outputs.

Comprehensive metrics covering:
- Triple extraction quality (confidence, coverage, diversity)
- Personality inference quality (evidence strength, trait distribution)
- Graph structure quality (connectivity, modularity, centrality)
- Data quality indicators (completeness, consistency)
"""

import networkx as nx
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter
import math

from .config import PipelineConfig
from .io_utils import load_jsonl, load_graphml, save_json
from .logging_utils import PipelineLogger


def compute_evidence_quality(triples: List[Dict]) -> Dict[str, Any]:
    """
    Evaluate quality of evidence spans in triples.

    Metrics:
    - Evidence coverage: % of triples with evidence spans
    - Avg evidence length: Mean characters in evidence
    - Evidence diversity: Unique evidence texts / total triples
    """
    if not triples:
        return {}

    with_evidence = 0
    evidence_lengths = []
    evidence_texts = set()

    for triple in triples:
        evidence = triple.get("evidence_span", {})
        if evidence and evidence.get("text"):
            with_evidence += 1
            text = evidence["text"]
            evidence_lengths.append(len(text))
            evidence_texts.add(text[:100])  # First 100 chars for uniqueness

    return {
        "evidence_coverage": round(with_evidence / len(triples), 3),
        "avg_evidence_length": round(sum(evidence_lengths) / len(evidence_lengths), 1) if evidence_lengths else 0,
        "evidence_diversity": round(len(evidence_texts) / len(triples), 3),
    }


def compute_confidence_distribution(triples: List[Dict]) -> Dict[str, Any]:
    """
    Analyze confidence score distribution to detect potential issues.

    High-quality extraction should show:
    - Most scores in 0.7-0.95 range (not clustered at extremes)
    - Low standard deviation indicates potential calibration issues
    """
    if not triples:
        return {}

    confidences = [t.get("confidence", 0.0) for t in triples]

    # Binning
    bins = {"0.0-0.5": 0, "0.5-0.7": 0, "0.7-0.85": 0, "0.85-0.95": 0, "0.95-1.0": 0}
    for conf in confidences:
        if conf < 0.5:
            bins["0.0-0.5"] += 1
        elif conf < 0.7:
            bins["0.5-0.7"] += 1
        elif conf < 0.85:
            bins["0.7-0.85"] += 1
        elif conf < 0.95:
            bins["0.85-0.95"] += 1
        else:
            bins["0.95-1.0"] += 1

    # Standard deviation
    mean_conf = sum(confidences) / len(confidences)
    variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
    std_dev = math.sqrt(variance)

    return {
        "confidence_bins": bins,
        "confidence_std_dev": round(std_dev, 3),
    }


def compute_relation_diversity(triples: List[Dict]) -> Dict[str, Any]:
    """
    Measure diversity of relation types extracted.

    Shannon entropy of relation distribution:
    - Higher entropy = more diverse relations (better coverage)
    - Lower entropy = dominated by few relations (potential extraction bias)
    """
    if not triples:
        return {}

    relations = [t.get("relation") for t in triples]
    counts = Counter(relations)
    total = len(relations)

    # Shannon entropy
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
    max_entropy = math.log2(len(counts))  # Max possible entropy
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    return {
        "relation_entropy": round(entropy, 3),
        "relation_entropy_normalized": round(normalized_entropy, 3),
        "relation_gini_coefficient": round(_gini_coefficient(list(counts.values())), 3),
    }


def _gini_coefficient(values: List[int]) -> float:
    """
    Compute Gini coefficient for distribution inequality.
    0 = perfectly equal, 1 = maximally unequal
    """
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(values)
    cumsum = sum((i + 1) * val for i, val in enumerate(sorted_values))
    return (2 * cumsum) / (n * sum(values)) - (n + 1) / n


def compute_personality_quality(profiles: List[Dict]) -> Dict[str, Any]:
    """
    Evaluate personality inference quality beyond basic statistics.

    Metrics:
    - Evidence per trait: Avg evidence spans per trait
    - Trait completeness: % of profiles with all 5 Big Five traits
    - Confidence consistency: Std dev of confidences within each profile
    """
    if not profiles:
        return {}

    evidence_counts = []
    complete_profiles = 0
    trait_confidences_per_profile = []

    for profile in profiles:
        traits = profile.get("traits", [])

        # Count evidence spans
        for trait in traits:
            spans = trait.get("evidence_spans", [])
            evidence_counts.append(len(spans))

        # Check completeness (all 5 Big Five traits)
        trait_names = {t["trait_name"] for t in traits}
        if len(trait_names) == 5:
            complete_profiles += 1

        # Confidence consistency within profile
        confidences = [t.get("confidence", 0.0) for t in traits]
        if len(confidences) > 1:
            mean = sum(confidences) / len(confidences)
            variance = sum((c - mean) ** 2 for c in confidences) / len(confidences)
            trait_confidences_per_profile.append(math.sqrt(variance))

    return {
        "avg_evidence_per_trait": round(sum(evidence_counts) / len(evidence_counts), 2) if evidence_counts else 0,
        "trait_completeness": round(complete_profiles / len(profiles), 3),
        "avg_confidence_std_within_profile": round(sum(trait_confidences_per_profile) / len(trait_confidences_per_profile), 3) if trait_confidences_per_profile else 0,
    }


def compute_graph_quality(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Advanced graph quality metrics beyond basic stats.

    Metrics:
    - Clustering coefficient: Measure of local density
    - Assortativity: Do high-degree nodes connect to other high-degree nodes?
    - Modularity: Community structure strength
    - Average path length: Measure of graph navigability
    """
    if G.number_of_nodes() == 0:
        return {}

    G_undirected = G.to_undirected()

    quality = {}

    # Clustering coefficient
    try:
        quality["avg_clustering_coefficient"] = round(nx.average_clustering(G_undirected), 4)
    except:
        quality["avg_clustering_coefficient"] = None

    # Assortativity (degree correlation)
    try:
        quality["degree_assortativity"] = round(nx.degree_assortativity_coefficient(G), 4)
    except:
        quality["degree_assortativity"] = None

    # Average shortest path (only on largest connected component)
    try:
        largest_cc = max(nx.connected_components(G_undirected), key=len)
        subgraph = G_undirected.subgraph(largest_cc)
        quality["avg_shortest_path_length"] = round(nx.average_shortest_path_length(subgraph), 2)
        quality["diameter"] = nx.diameter(subgraph)
    except:
        quality["avg_shortest_path_length"] = None
        quality["diameter"] = None

    # Graph density interpretation
    density = nx.density(G)
    if density < 0.01:
        quality["density_interpretation"] = "very_sparse"
    elif density < 0.05:
        quality["density_interpretation"] = "sparse"
    elif density < 0.2:
        quality["density_interpretation"] = "moderate"
    else:
        quality["density_interpretation"] = "dense"

    return quality


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
            metrics["evidence_quality"] = compute_evidence_quality(triples)
            metrics["confidence_distribution"] = compute_confidence_distribution(triples)
            metrics["relation_diversity"] = compute_relation_diversity(triples)

        # Personality statistics
        traits_path = config.output_root / "traits_final.jsonl"
        if traits_path.exists():
            logger.info("evaluate", f"Computing personality statistics")
            profiles = load_jsonl(traits_path)
            metrics["personality_stats"] = compute_personality_stats(profiles)
            metrics["personality_quality"] = compute_personality_quality(profiles)

        # Graph statistics
        graph_path = config.output_root / "graph.graphml"
        if graph_path.exists():
            logger.info("evaluate", f"Computing graph statistics")
            G = load_graphml(graph_path)
            metrics["graph_stats"] = compute_graph_stats(G)
            metrics["graph_quality"] = compute_graph_quality(G)

        # Save metrics
        output_path = config.output_root / "metrics.json"
        save_json(metrics, output_path, indent=2)

        logger.info("evaluate", f"Saved metrics to {output_path}")

        return output_path
