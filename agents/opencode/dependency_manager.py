#!/usr/bin/env python3
"""
OpenCode Dependency Manager — Skill Dependency Resolution, Compatibility, and Versioning

Handles:
- Resolving transitive skill dependencies
- Checking Odoo version compatibility
- Detecting circular dependencies
- Computing optimal load order (topological sort)
- Validating dependency constraints

Usage:
    from agents.opencode.dependency_manager import DependencyManager
    
    mgr = DependencyManager(registry)
    load_order = mgr.resolve(["skill_crm", "skill_marketing"])
    issues = mgr.validate(["skill_crm"])
"""

from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class DependencyError(Exception):
    """Raised when dependency resolution fails."""
    pass


class CircularDependencyError(DependencyError):
    """Raised when a circular dependency is detected."""
    pass


class VersionMismatchError(DependencyError):
    """Raised when version requirements cannot be satisfied."""
    pass


class DependencyManager:
    """Manages skill dependencies, versioning, and load order."""

    def __init__(self, registry):
        self.registry = registry

    def resolve(self, skill_ids: List[str]) -> List[str]:
        """Resolve all dependencies and return optimal load order (topological sort).
        
        Raises CircularDependencyError if a cycle is detected.
        """
        # Build adjacency list
        graph = defaultdict(set)
        all_skills = set()

        def add_with_deps(sid: str, visited: Set[str]):
            if sid in visited:
                return
            visited.add(sid)
            data = self.registry.get(sid)
            if not data:
                return
            all_skills.add(sid)
            for dep in data.get("dependencies", {}).get("skills", []):
                dep_id = dep.get("skill_id")
                if dep_id:
                    graph[sid].add(dep_id)
                    add_with_deps(dep_id, visited)

        visited = set()
        for sid in skill_ids:
            add_with_deps(sid, visited)

        # Topological sort (Kahn's algorithm) with cycle detection
        in_degree = {s: 0 for s in all_skills}
        for s in all_skills:
            for dep in graph.get(s, set()):
                if dep in in_degree:
                    in_degree[dep] += 1

        queue = deque([s for s in all_skills if in_degree.get(s, 0) == 0])
        load_order = []

        while queue:
            s = queue.popleft()
            load_order.append(s)
            for dep in graph.get(s, set()):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

        if len(load_order) != len(all_skills):
            remaining = all_skills - set(load_order)
            raise CircularDependencyError(
                f"Circular dependency detected involving: {remaining}"
            )

        return load_order

    def verify_compatibility(self, skill_ids: List[str], odoo_version: str = "19.0") -> List[str]:
        """Verify skill-Odoo version compatibility. Returns list of issues."""
        issues = []
        for sid in skill_ids:
            data = self.registry.get(sid)
            if not data:
                issues.append(f"Skill not found: {sid}")
                continue
            supported = data.get("supported_odoo_versions", [])
            if odoo_version not in supported:
                issues.append(
                    f"{sid}: requires Odoo {supported}, target is {odoo_version}"
                )
        return issues

    def check_transitive_deps(self, skill_ids: List[str]) -> Set[str]:
        """Get the full transitive closure of dependencies for skill_ids."""
        result = set()

        def traverse(sid: str, visited: Set[str]):
            if sid in visited:
                return
            visited.add(sid)
            data = self.registry.get(sid)
            if not data:
                return
            for dep in data.get("dependencies", {}).get("skills", []):
                dep_id = dep.get("skill_id")
                if dep_id:
                    result.add(dep_id)
                    traverse(dep_id, visited)

        visited = set()
        for sid in skill_ids:
            traverse(sid, visited)

        return result

    def find_optimal_set(self, desired_capabilities: List[str]) -> List[str]:
        """Find the minimal set of skills that provides all desired capabilities."""
        candidates = set()
        for cap_id in desired_capabilities:
            skills = self.registry.find_by_capability(cap_id)
            candidates.update(skills)

        # Add transitive dependencies
        full_set = self.check_transitive_deps(list(candidates))
        full_set.update(candidates)

        return self.resolve(list(full_set))

    def validate(self, skill_ids: List[str], odoo_version: str = "19.0") -> List[dict]:
        """Full validation of a set of skills. Returns list of issue dicts."""
        issues = []

        # 1. Check skills exist
        for sid in skill_ids:
            if not self.registry.exists(sid):
                issues.append({
                    "type": "error",
                    "skill": sid,
                    "message": f"Skill not found in registry",
                })

        # 2. Check version compatibility
        try:
            compat_issues = self.verify_compatibility(skill_ids, odoo_version)
            for msg in compat_issues:
                issues.append({"type": "warning", "skill": "all", "message": msg})
        except Exception as e:
            issues.append({"type": "error", "skill": "all", "message": str(e)})

        # 3. Check dependency resolution
        try:
            order = self.resolve(skill_ids)
            issues.append({
                "type": "info",
                "skill": "all",
                "message": f"Load order ({len(order)} skills): {' → '.join(order)}",
            })
        except CircularDependencyError as e:
            issues.append({"type": "error", "skill": "all", "message": str(e)})

        # 4. Check for missing prerequisites
        for sid in skill_ids:
            data = self.registry.get(sid)
            if data:
                for prereq in data.get("prerequisites", []):
                    if prereq.get("required", False):
                        prereq_skill = prereq.get("skill")
                        if prereq_skill and prereq_skill not in skill_ids:
                            if self.registry.exists(prereq_skill):
                                issues.append({
                                    "type": "warning",
                                    "skill": sid,
                                    "message": f"Recommended prerequisite not loaded: {prereq_skill}",
                                })

        return issues

    def describe_graph(self, skill_ids: List[str]) -> dict:
        """Describe the dependency graph for a set of skills."""
        nodes = set()
        edges = []

        def traverse(sid: str, visited: Set[str]):
            if sid in visited:
                return
            visited.add(sid)
            nodes.add(sid)
            data = self.registry.get(sid)
            if not data:
                return
            for dep in data.get("dependencies", {}).get("skills", []):
                dep_id = dep.get("skill_id")
                if dep_id:
                    edges.append({
                        "from": sid,
                        "to": dep_id,
                        "type": dep.get("relationship", "depends_on"),
                    })
                    traverse(dep_id, visited)

        visited = set()
        for sid in skill_ids:
            traverse(sid, visited)

        return {
            "root_skills": skill_ids,
            "total_skills": len(nodes),
            "nodes": sorted(nodes),
            "edges": edges,
        }
