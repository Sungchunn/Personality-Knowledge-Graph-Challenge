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
    Create enhanced pyvis Network from NetworkX graph with modern styling.

    Args:
        G: NetworkX graph
        config: Pipeline configuration

    Returns:
        Pyvis Network object with advanced visualizations
    """
    # Initialize pyvis network with dark theme
    net = Network(
        height="900px",
        width="100%",
        bgcolor="#0f1419",  # Dark background
        font_color="#e8eaed",  # Light text
        directed=True,
        select_menu=True,  # Enable selection menu
        filter_menu=True,  # Enable filter menu
    )

    # Configure physics for better layout
    net.barnes_hut(
        gravity=-50000,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.002,
        damping=0.15,
        overlap=0.5,
    )

    # Set options for interactivity
    net.set_options("""
    {
        "nodes": {
            "borderWidth": 2,
            "borderWidthSelected": 4,
            "font": {
                "size": 14,
                "face": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                "color": "#e8eaed"
            },
            "shadow": {
                "enabled": true,
                "color": "rgba(0,0,0,0.3)",
                "size": 10,
                "x": 2,
                "y": 2
            }
        },
        "edges": {
            "smooth": {
                "type": "cubicBezier",
                "forceDirection": "none",
                "roundness": 0.5
            },
            "font": {
                "size": 12,
                "face": "Inter, sans-serif",
                "color": "#9aa0a6",
                "strokeWidth": 0,
                "align": "middle"
            },
            "shadow": {
                "enabled": true,
                "color": "rgba(0,0,0,0.2)",
                "size": 5,
                "x": 1,
                "y": 1
            }
        },
        "physics": {
            "barnesHut": {
                "avoidOverlap": 0.5
            }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "hideEdgesOnDrag": true,
            "hideEdgesOnZoom": true
        }
    }
    """)

    # Calculate node importance for sizing
    degrees = dict(G.degree())
    max_degree = max(degrees.values()) if degrees else 1

    # Add nodes with enhanced styling
    for node in G.nodes():
        attrs = G.nodes[node]
        entity_type = attrs.get("entity_type", "unknown")

        # Modern color palette by entity type
        color_map = {
            "person": "#8ab4f8",      # Google Blue
            "location": "#81c995",    # Green
            "organization": "#f28b82", # Coral Red
            "event": "#fdd663",       # Yellow
            "unknown": "#9aa0a6",     # Gray
        }
        base_color = color_map.get(entity_type, "#9aa0a6")

        # Calculate average confidence for opacity
        avg_confidence = 0.8  # Default
        if entity_type == "person":
            traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
            confidences = []
            for trait in traits:
                conf_key = f"trait_{trait}_conf"
                if conf_key in attrs:
                    confidences.append(float(attrs[conf_key]))
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)

        # Build rich tooltip with personality traits and Big Five visualization
        title = f"""
        <div style='font-family: Inter, sans-serif; max-width: 350px;'>
            <div style='font-size: 18px; font-weight: 600; margin-bottom: 8px; color: {base_color};'>
                {node}
            </div>
            <div style='font-size: 12px; color: #9aa0a6; margin-bottom: 12px;'>
                Type: {entity_type.upper()}
            </div>
        """

        if entity_type == "person":
            traits_data = []
            for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
                score_key = f"trait_{trait}"
                conf_key = f"{score_key}_conf"
                if score_key in attrs:
                    score = float(attrs[score_key])
                    conf = float(attrs.get(conf_key, 0.0))
                    traits_data.append((trait, score, conf))

            if traits_data:
                title += "<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #3c4043;'>"
                title += "<div style='font-size: 14px; font-weight: 500; margin-bottom: 8px;'>Big Five Personality</div>"

                for trait, score, conf in traits_data:
                    # Color code by score
                    if score >= 0.7:
                        bar_color = "#81c995"  # High - green
                    elif score >= 0.5:
                        bar_color = "#fdd663"  # Medium - yellow
                    else:
                        bar_color = "#f28b82"  # Low - red

                    bar_width = int(score * 100)
                    title += f"""
                    <div style='margin-bottom: 6px;'>
                        <div style='font-size: 11px; color: #e8eaed; margin-bottom: 2px;'>
                            {trait.capitalize()}: {score:.2f} <span style='color: #9aa0a6;'>(conf: {conf:.2f})</span>
                        </div>
                        <div style='background: #3c4043; height: 8px; border-radius: 4px; overflow: hidden;'>
                            <div style='background: {bar_color}; width: {bar_width}%; height: 100%;'></div>
                        </div>
                    </div>
                    """
                title += "</div>"

        # Add degree info
        degree = degrees.get(node, 0)
        title += f"""
            <div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #3c4043; font-size: 11px; color: #9aa0a6;'>
                Connections: {degree}
            </div>
        </div>
        """

        # Size by importance (degree centrality)
        size = 15 + (degrees[node] / max_degree) * 40

        # Add border color for high-confidence entities
        border_color = base_color if avg_confidence >= 0.8 else "#5f6368"
        border_width = 3 if avg_confidence >= 0.8 else 2

        # Node styling with confidence-based opacity
        node_color = {
            "background": base_color,
            "border": border_color,
            "highlight": {
                "background": base_color,
                "border": "#ffffff"
            },
            "hover": {
                "background": base_color,
                "border": "#ffffff"
            }
        }

        net.add_node(
            node,
            label=attrs.get("label", node),
            color=node_color,
            size=size,
            title=title,
            borderWidth=border_width,
            opacity=0.5 + (avg_confidence * 0.5),  # 0.5-1.0 based on confidence
        )

    # Add edges with relationship-based color coding
    for u, v, data in G.edges(data=True):
        relation = data.get("relation", "")
        confidence = float(data.get("confidence", 0.5))
        evidence = data.get("evidence", "")

        # Color code by relationship type
        positive_relations = {"LOVES", "FRIENDS_WITH", "FAMILY_OF"}
        negative_relations = {"ENEMY_OF", "HATES"}
        leadership_relations = {"LEADS", "OWNS", "CREATED"}

        if relation in positive_relations:
            edge_color = "#81c995"  # Green - positive
        elif relation in negative_relations:
            edge_color = "#f28b82"  # Red - negative
        elif relation in leadership_relations:
            edge_color = "#fdd663"  # Gold - leadership
        else:
            edge_color = "#8ab4f8"  # Blue - neutral

        # Edge width and style by confidence
        width = 0.5 + confidence * 3.5
        dashes = False if confidence >= 0.7 else [5, 5]  # Dashed for low confidence

        # Opacity by confidence
        opacity = 0.4 + (confidence * 0.6)  # 0.4-1.0

        # Rich tooltip
        title = f"""
        <div style='font-family: Inter, sans-serif; max-width: 300px;'>
            <div style='font-size: 16px; font-weight: 600; margin-bottom: 4px; color: {edge_color};'>
                {relation}
            </div>
            <div style='font-size: 12px; color: #9aa0a6; margin-bottom: 8px;'>
                {u} → {v}
            </div>
            <div style='font-size: 11px; color: #e8eaed; margin-bottom: 8px;'>
                Confidence: <span style='color: {edge_color};'>{confidence:.2f}</span>
            </div>
        """

        if evidence:
            title += f"""
            <div style='padding-top: 8px; border-top: 1px solid #3c4043;'>
                <div style='font-size: 10px; color: #9aa0a6; margin-bottom: 4px;'>Evidence:</div>
                <div style='font-size: 11px; color: #e8eaed; font-style: italic;'>
                    "{evidence[:150]}{'...' if len(evidence) > 150 else ''}"
                </div>
            </div>
            """

        title += "</div>"

        net.add_edge(
            u,
            v,
            label=relation if confidence >= 0.7 else "",  # Hide labels for low confidence
            title=title,
            width=width,
            color={"color": edge_color, "opacity": opacity},
            arrows={"to": {"enabled": True, "scaleFactor": 0.5}},
            dashes=dashes,
            smooth={"type": "cubicBezier"},
        )

    return net


def run_viz(config: PipelineConfig, logger: PipelineLogger) -> Path:
    """
    Create interactive HTML visualization of the graph with custom enhancements.

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

        # Save base HTML
        html_path = config.output_root / "graph.html"
        net.save_graph(str(html_path))

        # Enhance HTML with custom header, legend, and styling
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Inject custom CSS and header
        custom_header = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    body {
        margin: 0;
        padding: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #0f1419;
        color: #e8eaed;
    }

    #header {
        background: linear-gradient(135deg, #1a73e8 0%, #8ab4f8 100%);
        padding: 24px 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        position: sticky;
        top: 0;
        z-index: 1000;
    }

    #header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
    }

    #header p {
        margin: 8px 0 0 0;
        font-size: 14px;
        color: rgba(255,255,255,0.9);
    }

    #stats {
        display: flex;
        gap: 24px;
        margin-top: 12px;
    }

    .stat-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: rgba(255,255,255,0.95);
    }

    .stat-value {
        font-weight: 600;
        font-size: 16px;
    }

    #legend {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(15, 20, 25, 0.95);
        border: 1px solid #3c4043;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        z-index: 100;
        max-width: 280px;
    }

    #legend h3 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: #e8eaed;
    }

    .legend-section {
        margin-bottom: 12px;
    }

    .legend-section:last-child {
        margin-bottom: 0;
    }

    .legend-title {
        font-size: 11px;
        font-weight: 500;
        color: #9aa0a6;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
        font-size: 12px;
    }

    .legend-color {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2px solid #3c4043;
    }

    .legend-line {
        width: 24px;
        height: 3px;
        border-radius: 2px;
    }

    .legend-dashed {
        border: 1.5px dashed;
        height: 0;
    }

    #toggle-legend {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #1a73e8;
        color: white;
        border: none;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 99;
        display: none;
    }

    #toggle-legend:hover {
        background: #1557b0;
    }
</style>

<div id="header">
    <h1>🌌 Dune Personality Knowledge Graph</h1>
    <p>Interactive visualization of character relationships and Big Five personality traits</p>
    <div id="stats">
        <div class="stat-item">
            <span>Nodes:</span>
            <span class="stat-value" id="node-count">""" + str(G.number_of_nodes()) + """</span>
        </div>
        <div class="stat-item">
            <span>Relationships:</span>
            <span class="stat-value" id="edge-count">""" + str(G.number_of_edges()) + """</span>
        </div>
        <div class="stat-item">
            <span>Mode:</span>
            <span class="stat-value">Character-Centric Analysis</span>
        </div>
    </div>
</div>

<div id="legend">
    <h3>📖 Legend</h3>

    <div class="legend-section">
        <div class="legend-title">Entity Types</div>
        <div class="legend-item">
            <div class="legend-color" style="background: #8ab4f8;"></div>
            <span>Person</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #81c995;"></div>
            <span>Location</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #f28b82;"></div>
            <span>Organization</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #fdd663;"></div>
            <span>Event</span>
        </div>
    </div>

    <div class="legend-section">
        <div class="legend-title">Relationships</div>
        <div class="legend-item">
            <div class="legend-line" style="background: #81c995;"></div>
            <span>Positive (Love, Friends)</span>
        </div>
        <div class="legend-item">
            <div class="legend-line" style="background: #f28b82;"></div>
            <span>Negative (Enemy, Hates)</span>
        </div>
        <div class="legend-item">
            <div class="legend-line" style="background: #fdd663;"></div>
            <span>Leadership</span>
        </div>
        <div class="legend-item">
            <div class="legend-line" style="background: #8ab4f8;"></div>
            <span>Neutral</span>
        </div>
    </div>

    <div class="legend-section">
        <div class="legend-title">Confidence</div>
        <div class="legend-item">
            <div class="legend-line" style="background: #8ab4f8;"></div>
            <span>High (≥0.7) - Solid</span>
        </div>
        <div class="legend-item">
            <div class="legend-dashed" style="border-color: #8ab4f8;"></div>
            <span>Low (<0.7) - Dashed</span>
        </div>
    </div>

    <div class="legend-section">
        <div class="legend-title">Interactions</div>
        <div class="legend-item" style="font-size: 11px; color: #9aa0a6;">
            • Hover over nodes for personality traits<br>
            • Click and drag to move nodes<br>
            • Scroll to zoom in/out<br>
            • Use built-in filters (top-right)
        </div>
    </div>
</div>

<button id="toggle-legend" onclick="toggleLegend()">?</button>

<script>
function toggleLegend() {
    const legend = document.getElementById('legend');
    legend.style.display = legend.style.display === 'none' ? 'block' : 'none';
}
</script>
"""

        # Insert header before the network container
        html_content = html_content.replace('<body>', '<body>\n' + custom_header)

        # Write enhanced HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info("viz", f"Saved enhanced visualization to {html_path}")

        return html_path
