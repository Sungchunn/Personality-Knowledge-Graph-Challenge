"""
Create a lightweight mini graph with just the main characters and their relationships.
This will load much faster than the full 1,050-node graph.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.io_utils import load_jsonl
from pipeline.config import PipelineConfig
from pipeline.logging_utils import PipelineLogger
from pipeline.build_graph import create_graph_from_triples
from pipeline.viz import create_pyvis_graph
import networkx as nx

def filter_graph_to_main_characters(G, character_names):
    """
    Create a subgraph containing only specified characters and their direct relationships.
    """
    # Create subgraph with only these nodes
    nodes_to_keep = set()

    for char in character_names:
        if char in G:
            nodes_to_keep.add(char)

    # Also include nodes that are directly connected to our characters
    for char in character_names:
        if char in G:
            # Add neighbors
            for neighbor in G.neighbors(char):
                # Only add if it's another character or important entity
                if neighbor in character_names or G.nodes[neighbor].get('entity_type') == 'person':
                    nodes_to_keep.add(neighbor)

    # Create subgraph
    mini_G = G.subgraph(nodes_to_keep).copy()

    return mini_G


def main():
    output_dir = Path("/Users/chromatrical/CAREER/Side Projects/Intellumia shortlist/Project/outputs/run_20251020_010533")

    print("=" * 60)
    print("Creating Mini Graph (Main Characters Only)")
    print("=" * 60)

    # Load data
    print("\n1. Loading data...")
    triples = load_jsonl(output_dir / "triples_canonical.jsonl")
    traits = load_jsonl(output_dir / "traits_final.jsonl")

    print(f"   Full graph: {len(triples)} triples")
    print(f"   Characters with traits: {len(traits)}")

    # Get character names
    character_names = [p["person_name"] for p in traits]
    print(f"\n2. Main characters:")
    for name in character_names:
        print(f"   - {name}")

    # Filter triples to only those involving our characters
    print(f"\n3. Filtering triples...")
    character_set = set(character_names)

    filtered_triples = []
    for triple in triples:
        # Keep triple if both subject and object are main characters
        if triple["subject"] in character_set and triple["object"] in character_set:
            filtered_triples.append(triple)

    print(f"   Filtered from {len(triples)} to {len(filtered_triples)} triples")
    print(f"   (Only relationships between main characters)")

    # Build mini graph
    print(f"\n4. Building mini graph...")
    G = create_graph_from_triples(filtered_triples, traits)

    print(f"   Nodes: {G.number_of_nodes()}")
    print(f"   Edges: {G.number_of_edges()}")

    # Create visualization
    print(f"\n5. Creating visualization...")
    config = PipelineConfig(
        input_jsonl_root=Path("data/jsonl"),
        output_root=output_dir,
    )

    net = create_pyvis_graph(G, config)

    # Save
    mini_html_path = output_dir / "graph_mini.html"
    net.save_graph(str(mini_html_path))

    # Add custom header
    with open(mini_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    custom_header = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    body {{
        margin: 0;
        padding: 0;
        font-family: 'Inter', sans-serif;
        background: #0f1419;
        color: #e8eaed;
    }}
    #header {{
        background: linear-gradient(135deg, #1a73e8 0%, #8ab4f8 100%);
        padding: 24px 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    #header h1 {{
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
    }}
    #header p {{
        margin: 8px 0 0 0;
        font-size: 14px;
        color: rgba(255,255,255,0.9);
    }}
    .stat {{
        display: inline-block;
        margin-right: 20px;
        margin-top: 8px;
    }}
    .stat-label {{
        font-size: 11px;
        color: rgba(255,255,255,0.7);
        text-transform: uppercase;
    }}
    .stat-value {{
        font-size: 18px;
        font-weight: 600;
        color: white;
    }}
</style>

<div id="header">
    <h1>🌌 Dune Mini Graph - Main Characters</h1>
    <p>Focused view of the 12 main characters and their relationships</p>
    <div class="stat">
        <div class="stat-label">Characters</div>
        <div class="stat-value">{G.number_of_nodes()}</div>
    </div>
    <div class="stat">
        <div class="stat-label">Relationships</div>
        <div class="stat-value">{G.number_of_edges()}</div>
    </div>
    <div class="stat">
        <div class="stat-label">Mode</div>
        <div class="stat-value">⚡ Fast Loading</div>
    </div>
</div>
"""

    html_content = html_content.replace('<body>', '<body>\n' + custom_header)

    with open(mini_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n{'=' * 60}")
    print(f"✓ Mini graph created successfully!")
    print(f"{'=' * 60}")
    print(f"\nOpen this file (loads instantly):")
    print(f"  {mini_html_path}")
    print(f"\nThis lightweight version includes:")
    print(f"  - All 12 characters with personality traits")
    print(f"  - {G.number_of_edges()} direct relationships between them")
    print(f"  - Much faster rendering than the full graph")
    print(f"\nFor the full {len(triples)}-triple graph, open:")
    print(f"  {output_dir / 'graph.html'}")
    print(f"  (may take 30-60 seconds to stabilize)")


if __name__ == "__main__":
    main()
