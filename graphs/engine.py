#!/usr/bin/env python3
"""
Knowledge Graph Engine — Builds and queries the Skill Relationship Graph.

Maintains a directed graph of skill relationships including:
- depends_on (required dependency)
- extends (adds capabilities to another skill)
- implements (implements a specification)
- requires (must be co-loaded)
- related_to (referential relationship)
- recommended_with (optional but beneficial)

Usage:
    from graphs.engine import KnowledgeGraphEngine
    
    engine = KnowledgeGraphEngine()
    engine.build_from_registry(registry)
    related = engine.find_related("skill_crm")
    path = engine.shortest_path("skill_crm", "skill_accounting")
    mermaid = engine.to_mermaid()
"""

import json
import logging
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


class KnowledgeGraphEngine:
    """Builds, queries, and serializes the skill knowledge graph."""

    RELATIONSHIP_TYPES = ["depends_on", "extends", "implements", "requires", "related_to", "recommended_with"]

    def __init__(self):
        self._nodes: Dict[str, dict] = {}
        self._edges: List[dict] = []
        self._adjacency: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    def build_from_registry(self, registry) -> int:
        """Build the graph from a SkillRegistry."""
        graph_data = registry.get_skill_graph()
        self._nodes = {}
        self._edges = graph_data.get("edges", [])
        self._adjacency = defaultdict(list)

        for node in graph_data.get("nodes", []):
            self._nodes[node["id"]] = node

        for edge in self._edges:
            source = edge["source"]
            target = edge["target"]
            rel = edge.get("relationship", "depends_on")
            self._adjacency[source].append((target, rel))
            # Also build reverse adjacency for upstream queries
            if hasattr(self, '_reverse_adj'):
                pass

        logger.info(f"Built knowledge graph: {len(self._nodes)} nodes, {len(self._edges)} edges")
        return len(self._edges)

    def add_skill(self, skill_id: str, name: str = "", domain: str = "", version: str = ""):
        """Add or update a node in the graph."""
        self._nodes[skill_id] = {
            "id": skill_id,
            "name": name,
            "domain": domain,
            "version": version,
        }

    def add_relationship(self, source: str, target: str, relationship: str = "depends_on"):
        """Add a directed edge between two skills."""
        if source not in self._nodes or target not in self._nodes:
            logger.warning(f"Cannot add edge: {source} or {target} not in graph")
            return
        self._edges.append({"source": source, "target": target, "relationship": relationship})
        self._adjacency[source].append((target, relationship))

    def find_dependencies(self, skill_id: str, transitive: bool = True) -> List[str]:
        """Find all skills that skill_id depends on (direct or transitive)."""
        result = []
        visited = set()

        def dfs(sid: str):
            if sid in visited:
                return
            visited.add(sid)
            for target, rel in self._adjacency.get(sid, []):
                if rel == "depends_on" or rel == "requires":
                    if target not in result:
                        result.append(target)
                    dfs(target)

        if transitive:
            dfs(skill_id)
        else:
            for target, rel in self._adjacency.get(skill_id, []):
                if rel == "depends_on" or rel == "requires":
                    result.append(target)

        return result

    def find_dependents(self, skill_id: str) -> List[str]:
        """Find all skills that depend on skill_id."""
        result = []
        for node_id in self._nodes:
            deps = self.find_dependencies(node_id, transitive=False)
            if skill_id in deps:
                result.append(node_id)
        return result

    def find_related(self, skill_id: str) -> List[dict]:
        """Find all directly related skills with relationship types."""
        related = []
        seen = set()
        for target, rel in self._adjacency.get(skill_id, []):
            if target not in seen:
                seen.add(target)
                node = self._nodes.get(target, {})
                related.append({
                    "skill_id": target,
                    "name": node.get("name"),
                    "relationship": rel,
                    "direction": "outgoing",
                })

        # Also find incoming relationships
        for source_id in self._nodes:
            for target, rel in self._adjacency.get(source_id, []):
                if target == skill_id and source_id not in seen:
                    seen.add(source_id)
                    node = self._nodes.get(source_id, {})
                    related.append({
                        "skill_id": source_id,
                        "name": node.get("name"),
                        "relationship": rel,
                        "direction": "incoming",
                    })

        return related

    def shortest_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """BFS shortest path between two skills."""
        if from_id not in self._nodes or to_id not in self._nodes:
            return None

        queue = deque([(from_id, [from_id])])
        visited = {from_id}

        while queue:
            current, path = queue.popleft()
            for target, _ in self._adjacency.get(current, []):
                if target == to_id:
                    return path + [to_id]
                if target not in visited:
                    visited.add(target)
                    queue.append((target, path + [target]))

        return None

    def find_common_ancestors(self, skill_ids: List[str]) -> List[str]:
        """Find common dependency ancestors shared by all listed skills."""
        common = None
        for sid in skill_ids:
            deps = set(self.find_dependencies(sid))
            if common is None:
                common = deps
            else:
                common &= deps
        return sorted(common) if common else []

    def find_communities(self) -> List[List[str]]:
        """Find clusters of highly-connected skills (simple community detection)."""
        visited = set()
        communities = []

        for node_id in self._nodes:
            if node_id in visited:
                continue
            # BFS to find connected component
            component = []
            queue = deque([node_id])
            while queue:
                current = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                for target, _ in self._adjacency.get(current, []):
                    if target not in visited:
                        queue.append(target)
                # Also traverse incoming
                for source_id in self._nodes:
                    for t, _ in self._adjacency.get(source_id, []):
                        if t == current and source_id not in visited:
                            queue.append(source_id)

            if component:
                communities.append(component)

        return communities

    def to_mermaid(self, highlight: Optional[List[str]] = None) -> str:
        """Generate Mermaid.js graph markup."""
        lines = ["graph TD"]
        highlight_set = set(highlight or [])

        for node_id, node in self._nodes.items():
            label = node.get("name", node_id)
            node_label = node_id.replace("skill_", "")
            if node_id in highlight_set:
                lines.append(f"    {node_label}([{label}]):::highlight")
            else:
                lines.append(f"    {node_label}[{label}]")

        for edge in self._edges:
            src = edge["source"].replace("skill_", "")
            tgt = edge["target"].replace("skill_", "")
            rel = edge.get("relationship", "depends_on")
            if rel == "depends_on":
                lines.append(f"    {src}-->{tgt}")
            elif rel == "extends":
                lines.append(f"    {src}-.->{tgt}")
            elif rel == "recommended_with":
                lines.append(f"    {src}-.-{tgt}")
            else:
                lines.append(f"    {src}==={rel}==>{tgt}")

        if highlight_set:
            lines.append("")
            lines.append("classDef highlight fill:#f96,stroke:#333,stroke-width:2px;")

        return "\n".join(lines)

    def to_json(self) -> dict:
        """Export the graph as JSON."""
        return {
            "nodes": list(self._nodes.values()),
            "edges": self._edges,
            "statistics": {
                "node_count": len(self._nodes),
                "edge_count": len(self._edges),
                "communities": len(self.find_communities()),
            },
        }

    def to_cytoscape(self) -> dict:
        """Export for Cytoscape.js visualization."""
        elements = []
        for node_id, node in self._nodes.items():
            elements.append({
                "data": {
                    "id": node_id,
                    "label": node.get("name", node_id),
                    "domain": node.get("domain", ""),
                }
            })
        for edge in self._edges:
            elements.append({
                "data": {
                    "source": edge["source"],
                    "target": edge["target"],
                    "label": edge.get("relationship", "depends_on"),
                }
            })
        return {"elements": elements}

    def stats(self) -> dict:
        """Return graph statistics."""
        communities = self.find_communities()
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "density": (2 * len(self._edges)) / (len(self._nodes) * (len(self._nodes) - 1)) if len(self._nodes) > 1 else 0,
            "community_count": len(communities),
            "community_sizes": [len(c) for c in communities],
            "isolated_nodes": len([n for n in self._nodes if not self._adjacency.get(n)]),
        }
