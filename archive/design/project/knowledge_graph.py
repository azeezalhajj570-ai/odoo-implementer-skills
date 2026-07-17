#!/usr/bin/env python3
"""
Project Knowledge Graph — Builds and maintains a comprehensive graph model
of a project's architecture including modules, models, security, workflows,
automation, database, customizations, and integrations.

Usage:
    from project.knowledge_graph import ProjectKnowledgeGraph
    
    kg = ProjectKnowledgeGraph(project_model)
    kg.build()
    architecture = kg.get_architecture_graph()
    print(kg.stats())
"""

import json
import logging
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Any

from project.engine import ProjectModel, ModuleInfo

logger = logging.getLogger(__name__)


class ProjectKnowledgeGraph:
    """Multi-dimensional project knowledge graph."""

    GRAPH_TYPES = [
        "architecture", "modules", "models", "security",
        "workflow", "automation", "database", "customization", "integration",
    ]

    def __init__(self, project_model: ProjectModel):
        self.project = project_model
        self.graphs: Dict[str, dict] = {}
        self.nodes: Dict[str, dict] = {}
        self.edges: List[dict] = []

    def build(self):
        """Build all graph dimensions from the project model."""
        self._build_module_graph()
        self._build_architecture_graph()
        self._build_security_graph()
        logger.info(f"Project knowledge graph built: {len(self.nodes)} nodes, "
                     f"{len(self.edges)} edges across {len(self.graphs)} dimensions")

    def _build_module_graph(self):
        """Build module dependency graph."""
        nodes = []
        edges = []

        for name, info in self.project.modules.items():
            nodes.append({
                "id": name,
                "type": "module",
                "category": info.category,
                "is_custom": info.is_custom,
                "version": info.version,
                "models_count": len(info.models),
            })

        for src, tgt in self.project.dependency_graph:
            edges.append({
                "source": src,
                "target": tgt,
                "type": "depends",
            })

        self.graphs["modules"] = {"nodes": nodes, "edges": edges}
        self.nodes.update({n["id"]: n for n in nodes})
        self.edges.extend(edges)

    def _build_architecture_graph(self):
        """Build high-level architecture overview."""
        nodes = [
            {"id": self.project.project_name, "type": "project"},
        ]
        edges = []

        for name, info in self.project.modules.items():
            nodes.append({
                "id": f"module_{name}",
                "type": "module_instance",
                "module": name,
                "is_custom": info.is_custom,
            })
            edges.append({
                "source": self.project.project_name,
                "target": f"module_{name}",
                "type": "contains",
            })

        if self.project.has_docker:
            nodes.append({"id": "docker", "type": "infrastructure"})
            edges.append({
                "source": self.project.project_name,
                "target": "docker",
                "type": "uses",
            })

        self.graphs["architecture"] = {"nodes": nodes, "edges": edges}

    def _build_security_graph(self):
        """Build security group and rule graph."""
        nodes = []
        edges = []

        for name, info in self.project.modules.items():
            for group in info.security_groups:
                gid = f"group_{group}"
                nodes.append({"id": gid, "type": "security_group", "module": name})
                edges.append({
                    "source": f"module_{name}",
                    "target": gid,
                    "type": "defines",
                })

        self.graphs["security"] = {"nodes": nodes, "edges": edges}

    def get_graph(self, graph_type: str) -> dict:
        return self.graphs.get(graph_type, {"nodes": [], "edges": []})

    def get_architecture_graph(self) -> dict:
        return self.graphs.get("architecture", {"nodes": [], "edges": []})

    def get_module_graph(self) -> dict:
        return self.graphs.get("modules", {"nodes": [], "edges": []})

    def find_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """BFS shortest path between two nodes."""
        adjacency = defaultdict(list)
        for edge in self.edges:
            adjacency[edge["source"]].append(edge["target"])

        queue = deque([(from_id, [from_id])])
        visited = {from_id}

        while queue:
            current, path = queue.popleft()
            for neighbor in adjacency.get(current, []):
                if neighbor == to_id:
                    return path + [to_id]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def find_impacted_modules(self, module_name: str) -> List[str]:
        """Find all modules that would be impacted by changes to a module."""
        impacted = []
        visited = set()

        def dfs(name: str):
            if name in visited:
                return
            visited.add(name)
            for edge in self.edges:
                if edge["source"] == f"module_{name}" and edge["type"] == "depends":
                    target = edge["target"].replace("module_", "")
                    impacted.append(target)
                    dfs(target)

        dfs(module_name)
        return impacted

    def to_mermaid(self, graph_type: str = "modules") -> str:
        """Generate Mermaid.js graph markup."""
        graph = self.get_graph(graph_type)
        lines = ["graph TD"]

        for node in graph.get("nodes", []):
            nid = node["id"].replace("module_", "").replace("group_", "")
            label = node.get("type", "unknown")
            if node.get("is_custom"):
                lines.append(f"    {nid}[{nid}]:::custom")
            else:
                lines.append(f"    {nid}[{nid}]")

        for edge in graph.get("edges", []):
            src = edge["source"].replace("module_", "").replace("group_", "")
            tgt = edge["target"].replace("module_", "").replace("group_", "")
            lines.append(f"    {src}-->{tgt}")

        lines.append("")
        lines.append("classDef custom fill:#f96,stroke:#333,stroke-width:2px;")
        return "\n".join(lines)

    def stats(self) -> dict:
        return {
            "graph_dimensions": len(self.graphs),
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "graph_types": list(self.graphs.keys()),
            "module_count": self.project.modules_count,
            "custom_module_count": self.project.custom_modules_count,
        }

    def export_json(self) -> dict:
        return {
            "project": self.project.to_dict(),
            "graphs": self.graphs,
            "stats": self.stats(),
        }
