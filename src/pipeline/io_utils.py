"""
I/O utilities for loading and saving pipeline data.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Iterator


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load JSONL file into a list of dictionaries.

    Args:
        file_path: Path to JSONL file

    Returns:
        List of JSON objects
    """
    records = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def iter_jsonl(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Iterate over JSONL file yielding one record at a time.

    Args:
        file_path: Path to JSONL file

    Yields:
        JSON objects one at a time
    """
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def save_jsonl(records: List[Dict[str, Any]], file_path: Path) -> None:
    """
    Save list of dictionaries to JSONL file.

    Args:
        records: List of JSON-serializable dictionaries
        file_path: Output path
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_json(data: Any, file_path: Path, indent: int = 2) -> None:
    """
    Save data to JSON file with pretty printing.

    Args:
        data: JSON-serializable data
        file_path: Output path
        indent: Indentation level
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json(file_path: Path) -> Any:
    """
    Load JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_jsonl_files(root_dir: Path, pattern: str = "*.jsonl") -> List[Path]:
    """
    Discover all JSONL files in a directory.

    Args:
        root_dir: Root directory to search
        pattern: Glob pattern for matching files

    Returns:
        Sorted list of JSONL file paths
    """
    return sorted(root_dir.glob(pattern))


def save_graphml(graph, file_path: Path) -> None:
    """
    Save NetworkX graph to GraphML format.

    Args:
        graph: NetworkX graph object
        file_path: Output path for GraphML file
    """
    import networkx as nx

    file_path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, file_path)


def load_graphml(file_path: Path):
    """
    Load NetworkX graph from GraphML file.

    Args:
        file_path: Path to GraphML file

    Returns:
        NetworkX graph object
    """
    import networkx as nx

    return nx.read_graphml(file_path)
