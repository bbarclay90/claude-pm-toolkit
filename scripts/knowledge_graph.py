"""
Knowledge graph engine for the PM toolkit.

Handles reading/writing graph.json, creating node markdown files,
updating _index.md and _log.md, and generating Graphviz DOT visualization.

The knowledge graph is scoped per product:
  {vault}/{product}/Knowledge Graph/

The vault path and active product come from pdm.config.yaml (see config.py).

Usage:
  python scripts/knowledge_graph.py --visualize
  python scripts/knowledge_graph.py --visualize --product Acme
  python scripts/knowledge_graph.py --query stakeholder-jane
  python scripts/knowledge_graph.py --neighbors stakeholder-jane
  python scripts/knowledge_graph.py --stats
"""
import json
import argparse
import sys
from datetime import date
from pathlib import Path

import config


def get_active_product(override: str = "") -> str:
    return override or config.active_product()


def get_kg_dir(product: str) -> Path:
    return config.product_path(product) / "Knowledge Graph"


def get_paths(product: str) -> tuple[Path, Path, Path, Path, Path]:
    kg_dir = get_kg_dir(product)
    return (
        kg_dir,
        kg_dir / "graph.json",
        kg_dir / "_index.md",
        kg_dir / "_log.md",
        kg_dir / "graph-view.md",
    )

NODE_COLORS = {
    "Product":     "lightblue",
    "Stakeholder": "lightyellow",
    "Team":        "lightgreen",
    "Feature":     "lightsalmon",
    "Decision":    "plum",
    "Commitment":  "orange",
    "Constraint":  "lightcoral",
    "Metric":      "lightcyan",
    "Milestone":   "lightskyblue",
}

NODE_TYPE_DIRS = {
    "Product":     "products",
    "Stakeholder": "stakeholders",
    "Team":        "teams",
    "Feature":     "features",
    "Decision":    "decisions",
    "Commitment":  "commitments",
    "Constraint":  "constraints",
    "Metric":      "metrics",
    "Milestone":   "milestones",
}


# ---------------------------------------------------------------------------
# Graph I/O
# ---------------------------------------------------------------------------

def load_graph(graph_file: Path) -> dict:
    if not graph_file.exists():
        return {"nodes": [], "edges": []}
    return json.loads(graph_file.read_text(encoding="utf-8"))


def save_graph(graph: dict, graph_file: Path) -> None:
    graph_file.write_text(
        json.dumps(graph, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Node operations
# ---------------------------------------------------------------------------

def get_node(graph: dict, node_id: str) -> dict | None:
    return next((n for n in graph["nodes"] if n["id"] == node_id), None)


def upsert_node(graph: dict, node: dict) -> bool:
    """Add or update a node. Returns True if new, False if updated."""
    existing = get_node(graph, node["id"])
    if existing:
        existing.update(node)
        existing["updated"] = str(date.today())
        return False
    node.setdefault("created", str(date.today()))
    node.setdefault("updated", str(date.today()))
    node.setdefault("sources", [])
    node.setdefault("properties", {})
    graph["nodes"].append(node)
    return True


def upsert_edge(graph: dict, edge: dict) -> bool:
    """Add or update an edge. Returns True if new."""
    existing = next((e for e in graph["edges"] if e["id"] == edge["id"]), None)
    if existing:
        existing.update(edge)
        return False
    edge.setdefault("created", str(date.today()))
    graph["edges"].append(edge)
    return True


def get_neighbors(graph: dict, node_id: str) -> list[dict]:
    """Return all nodes directly connected to node_id."""
    connected_ids = set()
    for edge in graph["edges"]:
        if edge["from"] == node_id:
            connected_ids.add(edge["to"])
        elif edge["to"] == node_id:
            connected_ids.add(edge["from"])
    return [n for n in graph["nodes"] if n["id"] in connected_ids]


# ---------------------------------------------------------------------------
# Node markdown files
# ---------------------------------------------------------------------------

def node_md_path(node: dict, kg_dir: Path) -> Path:
    type_dir = NODE_TYPE_DIRS.get(node["type"], "other")
    return kg_dir / "nodes" / type_dir / f"{node['id']}.md"


def write_node_file(node: dict, edges: list[dict], kg_dir: Path) -> None:
    path = node_md_path(node, kg_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    outgoing = [e for e in edges if e["from"] == node["id"]]
    incoming = [e for e in edges if e["to"] == node["id"]]

    lines = [
        "---",
        f"id: {node['id']}",
        f"type: {node['type']}",
        f"name: {node.get('name', node['id'])}",
        f"created: {node.get('created', '')}",
        f"updated: {node.get('updated', '')}",
        f"sources: {json.dumps(node.get('sources', []))}",
        "---",
        "",
        f"# {node.get('name', node['id'])}",
        "",
        f"**Type**: {node['type']}",
        "",
        node.get("description", ""),
        "",
    ]

    if outgoing:
        lines.append("## Relationships (outgoing)")
        for e in outgoing:
            lines.append(f"- **{e['type']}** -> [[{e['to']}]] - {e.get('label', '')}")
        lines.append("")

    if incoming:
        lines.append("## Relationships (incoming)")
        for e in incoming:
            lines.append(f"- [[{e['from']}]] **{e['type']}** this node - {e.get('label', '')}")
        lines.append("")

    if node.get("sources"):
        lines.append("## Sources")
        for s in node["sources"]:
            lines.append(f"- {s}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Index and log
# ---------------------------------------------------------------------------

def rebuild_index(graph: dict, index_file: Path) -> None:
    by_type: dict[str, list] = {}
    for node in graph["nodes"]:
        by_type.setdefault(node["type"], []).append(node)

    lines = [
        "# Knowledge Graph Index",
        "",
        "This file is auto-updated by /approve-context. Do not edit manually.",
        "",
    ]
    for node_type in [
        "Product", "Stakeholder", "Team", "Feature",
        "Decision", "Commitment", "Constraint", "Metric", "Milestone"
    ]:
        lines.append(f"## {node_type}s")
        nodes = by_type.get(node_type, [])
        if nodes:
            for n in nodes:
                type_dir = NODE_TYPE_DIRS.get(n["type"], "other")
                lines.append(f"- [[nodes/{type_dir}/{n['id']}|{n.get('name', n['id'])}]] - {n.get('description', '')[:80]}")
        else:
            lines.append("(none yet)")
        lines.append("")

    index_file.write_text("\n".join(lines), encoding="utf-8")


def append_log(operation: str, details: str, log_file: Path) -> None:
    entry = f"## [{date.today()}] {operation} | {details}\n\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


# ---------------------------------------------------------------------------
# Graphviz DOT visualization
# ---------------------------------------------------------------------------

def generate_dot(graph: dict) -> str:
    lines = [
        "digraph KnowledgeGraph {",
        '  rankdir=LR;',
        '  node [shape=box, style=filled, fontname="Helvetica", fontsize=10];',
        '  edge [fontname="Helvetica", fontsize=9];',
        "",
    ]

    for node in graph["nodes"]:
        color = NODE_COLORS.get(node["type"], "white")
        label = node.get("name", node["id"]).replace('"', '\\"')
        node_id = node["id"].replace("-", "_")
        lines.append(f'  {node_id} [label="{label}\\n({node["type"]})", fillcolor="{color}"];')

    lines.append("")

    for edge in graph["edges"]:
        from_id = edge["from"].replace("-", "_")
        to_id = edge["to"].replace("-", "_")
        label = edge.get("type", "").replace('"', '\\"')
        lines.append(f'  {from_id} -> {to_id} [label="{label}"];')

    lines.append("}")
    return "\n".join(lines)


def update_graph_view(graph: dict, graph_view: Path) -> None:
    dot = generate_dot(graph)
    content = "\n".join([
        "# Knowledge Graph Visualization",
        "",
        "Auto-regenerated by `scripts/knowledge_graph.py --visualize`.",
        "Open in Obsidian preview mode to render (requires obsidian-graphviz plugin).",
        "",
        "```dot",
        dot,
        "```",
    ])
    graph_view.write_text(content, encoding="utf-8")
    print(f"Graph view updated: {graph_view}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="PDM Knowledge Graph Engine")
    parser.add_argument("--product", metavar="PRODUCT", help="Product name (overrides active_product in pdm.config.yaml)")
    parser.add_argument("--visualize", action="store_true", help="Regenerate graph-view.md DOT visualization")
    parser.add_argument("--query", metavar="NODE_ID", help="Print a node and its edges")
    parser.add_argument("--neighbors", metavar="NODE_ID", help="List all directly connected nodes")
    parser.add_argument("--stats", action="store_true", help="Print graph statistics")
    args = parser.parse_args()

    try:
        product = get_active_product(args.product or "")
        kg_dir, graph_file, index_file, log_file, graph_view = get_paths(product)
    except config.ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    graph = load_graph(graph_file)

    print(f"Product: {product} | Graph: {kg_dir}")

    if args.visualize:
        update_graph_view(graph, graph_view)

    elif args.query:
        node = get_node(graph, args.query)
        if node:
            print(json.dumps(node, indent=2))
            edges = [e for e in graph["edges"] if args.query in (e["from"], e["to"])]
            print(f"\nEdges ({len(edges)}):")
            for e in edges:
                print(f"  {e['from']} -[{e['type']}]-> {e['to']}")
        else:
            print(f"Node not found: {args.query}")

    elif args.neighbors:
        neighbors = get_neighbors(graph, args.neighbors)
        print(f"Neighbors of {args.neighbors}:")
        for n in neighbors:
            print(f"  [{n['type']}] {n['id']} - {n.get('name', '')}")

    elif args.stats:
        by_type: dict[str, int] = {}
        for n in graph["nodes"]:
            by_type[n["type"]] = by_type.get(n["type"], 0) + 1
        print(f"Nodes: {len(graph['nodes'])}")
        for t, count in sorted(by_type.items()):
            print(f"  {t}: {count}")
        print(f"Edges: {len(graph['edges'])}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
