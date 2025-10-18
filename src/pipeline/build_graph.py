"""
Build NetworkX property graph from triples and personality data.
"""

import networkx as nx
from pathlib import Path
from typing import List, Dict, Any

from .config import PipelineConfig
from .io_utils import load_jsonl, save_graphml, save_json
from .logging_utils import PipelineLogger


def create_graph_from_triples(
    triples: List[Dict[str, Any]], traits: List[Dict[str, Any]]
) -> nx.MultiDiGraph:
    """
    Create NetworkX graph from triples and personality traits.

    Args:
        triples: List of triple dictionaries
        traits: List of personality profile dictionaries

    Returns:
        NetworkX MultiDiGraph
    """
    G = nx.MultiDiGraph()

    # Add nodes and edges from triples
    for triple in triples:
        subject = triple["subject"]
        obj = triple["object"]
        relation = triple["relation"]

        # Add nodes
        if not G.has_node(subject):
            G.add_node(subject, entity_type="unknown", label=subject)

        if not G.has_node(obj):
            G.add_node(obj, entity_type="unknown", label=obj)

        # Add edge
        G.add_edge(
            subject,
            obj,
            relation=relation,
            confidence=triple.get("confidence", 0.0),
            evidence=triple.get("evidence_span", {}).get("text", ""),
        )

    # Add personality traits as node attributes
    trait_map = {profile["person_name"]: profile for profile in traits}

    for node in G.nodes():
        if node in trait_map:
            profile = trait_map[node]
            G.nodes[node]["entity_type"] = "person"

            # Add trait scores as attributes
            for trait in profile.get("traits", []):
                trait_name = trait["trait_name"]
                G.nodes[node][f"trait_{trait_name}"] = trait["score"]
                G.nodes[node][f"trait_{trait_name}_conf"] = trait["confidence"]

    return G


def export_graph_json(G: nx.MultiDiGraph, output_path: Path) -> None:
    """
    Export graph to JSON format for custom processing.

    Args:
        G: NetworkX graph
        output_path: Output JSON path
    """
    graph_data = {
        "nodes": [
            {
                "id": node,
                "attributes": dict(G.nodes[node]),
            }
            for node in G.nodes()
        ],
        "edges": [
            {
                "source": u,
                "target": v,
                "attributes": dict(data),
            }
            for u, v, data in G.edges(data=True)
        ],
    }

    save_json(graph_data, output_path)


def run_build_graph(config: PipelineConfig, logger: PipelineLogger) -> Path:
    """
    Build property graph from canonical triples and personality traits.

    Args:
        config: Pipeline configuration
        logger: Pipeline logger

    Returns:
        Path to output graph.graphml file
    """
    with logger.stage_context("build_graph"):
        # Load canonical triples
        triples_path = config.output_root / "triples_canonical.jsonl"
        logger.info("build_graph", f"Loading triples from {triples_path}")
        triples = load_jsonl(triples_path)

        # Load personality traits
        traits_path = config.output_root / "traits_final.jsonl"
        traits = []
        if traits_path.exists():
            logger.info("build_graph", f"Loading traits from {traits_path}")
            traits = load_jsonl(traits_path)
        else:
            logger.warning("build_graph", "No traits file found, creating graph without personality data")

        logger.info(
            "build_graph",
            f"Creating graph from {len(triples)} triples and {len(traits)} profiles",
        )

        # Create graph
        G = create_graph_from_triples(triples, traits)

        logger.info(
            "build_graph",
            f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges",
            node_count=G.number_of_nodes(),
            edge_count=G.number_of_edges(),
        )

        # Save as GraphML
        graphml_path = config.output_root / "graph.graphml"
        save_graphml(G, graphml_path)
        logger.info("build_graph", f"Saved GraphML to {graphml_path}")

        # Save as JSON
        json_path = config.output_root / "graph.json"
        export_graph_json(G, json_path)
        logger.info("build_graph", f"Saved JSON to {json_path}")

        return graphml_path
