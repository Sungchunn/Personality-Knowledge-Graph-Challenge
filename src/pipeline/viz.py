"""
Visualization of the knowledge graph using pyvis.
"""

import networkx as nx
from pathlib import Path
from pyvis.network import Network

from .config import PipelineConfig
from .io_utils import load_graphml
from .logging_utils import PipelineLogger


def create_pyvis_graph(G: nx.MultiDiGraph, config: PipelineConfig) -> Network:
    """
    Create pyvis Network from NetworkX graph.

    Args:
        G: NetworkX graph
        config: Pipeline configuration

    Returns:
        Pyvis Network object
    """
    # Initialize pyvis network
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000",
        directed=True,
    )

    # Configure physics
    net.barnes_hut(
        gravity=-80000,
        central_gravity=0.3,
        spring_length=250,
        spring_strength=0.001,
        damping=0.09,
    )

    # Add nodes
    for node in G.nodes():
        attrs = G.nodes[node]
        entity_type = attrs.get("entity_type", "unknown")

        # Color by entity type
        color_map = {
            "person": "#3498db",  # Blue
            "location": "#2ecc71",  # Green
            "organization": "#e74c3c",  # Red
            "event": "#f39c12",  # Orange
            "unknown": "#95a5a6",  # Gray
        }
        color = color_map.get(entity_type, "#95a5a6")

        # Build tooltip with personality traits if available
        title = f"<b>{node}</b><br>Type: {entity_type}"
        if entity_type == "person":
            traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
            trait_info = []
            for trait in traits:
                score_key = f"trait_{trait}"
                if score_key in attrs:
                    score = attrs[score_key]
                    conf = attrs.get(f"{score_key}_conf", 0.0)
                    trait_info.append(f"{trait.capitalize()}: {score:.2f} (conf: {conf:.2f})")

            if trait_info:
                title += "<br><br>Personality:<br>" + "<br>".join(trait_info)

        # Size by degree
        degree = G.degree(node)
        size = 10 + min(degree * 2, 50)

        net.add_node(
            node,
            label=attrs.get("label", node),
            color=color,
            size=size,
            title=title,
        )

    # Add edges
    for u, v, data in G.edges(data=True):
        relation = data.get("relation", "")
        confidence = data.get("confidence", 0.5)
        evidence = data.get("evidence", "")

        # Edge width by confidence
        width = 1 + confidence * 3

        # Edge title
        title = f"{relation}<br>Confidence: {confidence:.2f}"
        if evidence:
            title += f"<br>Evidence: {evidence[:100]}..."

        net.add_edge(
            u,
            v,
            label=relation,
            title=title,
            width=width,
            arrows="to",
        )

    return net


def run_viz(config: PipelineConfig, logger: PipelineLogger) -> Path:
    """
    Create interactive HTML visualization of the graph.

    Args:
        config: Pipeline configuration
        logger: Pipeline logger

    Returns:
        Path to output graph.html file
    """
    with logger.stage_context("viz"):
        # Load graph
        graphml_path = config.output_root / "graph.graphml"
        logger.info("viz", f"Loading graph from {graphml_path}")

        G = load_graphml(graphml_path)

        logger.info(
            "viz",
            f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges",
        )

        # Create pyvis visualization
        logger.info("viz", "Creating interactive visualization")
        net = create_pyvis_graph(G, config)

        # Save HTML
        html_path = config.output_root / "graph.html"
        net.save_graph(str(html_path))

        logger.info("viz", f"Saved visualization to {html_path}")

        return html_path
