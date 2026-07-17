#!/usr/bin/env python3
"""
OpenCode Skill Registry — Persistent Skill Index and Metadata Store

The Skill Registry maintains a persistent index of all installed skills,
their versions, capabilities, dependencies, and metadata. It serves as
the source of truth for the OpenCode integration layer.

Usage:
    from agents.opencode.skill_registry import SkillRegistry
    
    registry = SkillRegistry()
    registry.index_all()
    skill_info = registry.get("skill_crm")
    skills = registry.find_by_capability("cap_lead_scoring")
    graph = registry.resolve_dependencies()
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


class SkillRegistry:
    """Persistent registry of all discovered skills with metadata indexing."""

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or ROOT / "output" / "skill_registry.json"
        self._registry: Dict[str, dict] = {}
        self._capability_index: Dict[str, List[str]] = {}
        self._domain_index: Dict[str, List[str]] = {}
        self._agent_index: Dict[str, List[str]] = {}
        self._tag_index: Dict[str, List[str]] = {}

    def index_all(self, skills_base: Optional[Path] = None) -> int:
        """Scan skills directory and build the registry index."""
        base = skills_base or ROOT / "skills"
        count = 0

        for skill_dir in base.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "skill.json"
            if not skill_file.exists():
                continue

            try:
                with open(skill_file) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Cannot read {skill_file}: {e}")
                continue

            skill_id = data.get("skill_id")
            if not skill_id:
                continue

            self._registry[skill_id] = {
                "path": str(skill_dir),
                "data": data,
                "indexed_at": datetime.now(timezone.utc).isoformat(),
            }

            # Build capability index
            for cap in data.get("capabilities", []):
                cap_id = cap.get("id")
                if cap_id:
                    self._capability_index.setdefault(cap_id, []).append(skill_id)

            # Build domain index
            domain = data.get("domain")
            if domain:
                self._domain_index.setdefault(domain.lower(), []).append(skill_id)

            # Build agent index
            for agent_type in data.get("compatible_agents", []):
                self._agent_index.setdefault(agent_type, []).append(skill_id)

            # Build tag index
            for tag in data.get("tags", []):
                self._tag_index.setdefault(tag.lower(), []).append(skill_id)

            count += 1

        self._persist()
        logger.info(f"Indexed {count} skills")
        return count

    def get(self, skill_id: str) -> Optional[dict]:
        """Get full skill record by ID."""
        entry = self._registry.get(skill_id)
        return entry.get("data") if entry else None

    def exists(self, skill_id: str) -> bool:
        return skill_id in self._registry

    def find_by_capability(self, cap_id: str) -> List[str]:
        """Find skill IDs that have a specific capability."""
        return self._capability_index.get(cap_id, [])

    def find_by_domain(self, domain: str) -> List[str]:
        """Find skill IDs by domain."""
        return self._domain_index.get(domain.lower(), [])

    def find_by_agent(self, agent_type: str) -> List[str]:
        """Find skill IDs compatible with an agent type."""
        return self._agent_index.get(agent_type, [])

    def find_by_tag(self, tag: str) -> List[str]:
        """Find skill IDs by tag."""
        return self._tag_index.get(tag.lower(), [])

    def search(self, query: str) -> List[dict]:
        """Full-text search across skill names, descriptions, and tags."""
        query = query.lower()
        results = []
        for skill_id, entry in self._registry.items():
            data = entry["data"]
            searchable = [
                data.get("name", ""),
                data.get("description", ""),
                data.get("domain", ""),
                " ".join(data.get("tags", [])),
                " ".join(c.get("name", "") for c in data.get("capabilities", [])),
            ]
            if query in " ".join(searchable).lower():
                results.append({"skill_id": skill_id, **data})
        return results

    def get_skill_graph(self) -> dict:
        """Build a dependency graph of all registered skills."""
        nodes = []
        edges = []

        for skill_id, entry in self._registry.items():
            data = entry["data"]
            nodes.append({
                "id": skill_id,
                "name": data.get("name"),
                "domain": data.get("domain"),
                "version": data.get("version"),
            })

            for dep in data.get("dependencies", {}).get("skills", []):
                dep_id = dep.get("skill_id")
                if dep_id and dep_id in self._registry:
                    edges.append({
                        "source": skill_id,
                        "target": dep_id,
                        "relationship": dep.get("relationship", "depends_on"),
                    })

        return {"nodes": nodes, "edges": edges}

    def get_skill_graph_mermaid(self) -> str:
        """Generate Mermaid.js dependency graph."""
        graph = self.get_skill_graph()
        lines = ["graph TD"]
        for edge in graph["edges"]:
            src = edge["source"].replace("skill_", "")
            tgt = edge["target"].replace("skill_", "")
            rel = edge["relationship"]
            if rel == "depends_on":
                lines.append(f"    {src}-->{tgt}")
            elif rel == "extends":
                lines.append(f"    {src}-.->{tgt}")
            elif rel == "recommended_with":
                lines.append(f"    {src}-.-{tgt}")
            else:
                lines.append(f"    {src}===>{tgt}")
        return "\n".join(lines)

    def resolve_dependencies(self, skill_ids: List[str]) -> Tuple[List[str], List[str]]:
        """Resolve skill dependencies and return (load_order, missing)."""
        resolved = []
        seen = set()
        missing = []

        def resolve(sid: str):
            if sid in seen:
                return
            seen.add(sid)
            entry = self._registry.get(sid)
            if not entry:
                missing.append(sid)
                return
            data = entry["data"]
            for dep in data.get("dependencies", {}).get("skills", []):
                dep_id = dep.get("skill_id")
                if dep_id and dep_id not in seen:
                    resolve(dep_id)
            resolved.append(sid)

        for sid in skill_ids:
            resolve(sid)

        return resolved, missing

    def all_skills(self) -> Dict[str, dict]:
        """Return all registered skills (summary data)."""
        return {
            sid: {
                "name": entry["data"].get("name"),
                "version": entry["data"].get("version"),
                "domain": entry["data"].get("domain"),
                "capabilities": [c.get("id") for c in entry["data"].get("capabilities", [])],
                "dependencies": [d.get("skill_id") for d in entry["data"].get("dependencies", {}).get("skills", [])],
            }
            for sid, entry in self._registry.items()
        }

    def _persist(self):
        """Persist the registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump({
                "indexed_at": datetime.now(timezone.utc).isoformat(),
                "skill_count": len(self._registry),
                "capabilities": {k: v for k, v in self._capability_index.items()},
                "domains": {k: v for k, v in self._domain_index.items()},
                "skills": self.all_skills(),
            }, f, indent=2)
        logger.info(f"Registry persisted to {self.registry_path}")
