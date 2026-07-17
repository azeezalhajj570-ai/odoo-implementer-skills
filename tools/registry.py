#!/usr/bin/env python3
"""
Tool Registry — Discovers, loads, and executes executable tools from skill packages.

Every skill can expose Python-based tools that perform actions:
analyzing databases, generating code, validating artifacts, etc.

Tools are Python modules in skills/<skill>/tools/*.py,
each exporting a `tools` list and/or `register(registry)` function.

Usage:
    from tools.registry import ToolRegistry, get_registry
    
    registry = get_registry()
    registry.discover_all()
    result = registry.execute("crm", "analyze_pipeline", {"lead_ids": [1,2,3]})
"""

import importlib
import importlib.util
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ToolDefinition:
    """Schema for an executable tool within a skill."""
    name: str
    description: str
    parameters: dict = field(default_factory=dict)  # JSON Schema
    returns: dict = field(default_factory=dict)     # JSON Schema
    skill_id: str = ""
    category: str = ""  # analyzer, generator, validator, migrator, diagnostic
    fn: Optional[Callable] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "returns": self.returns,
            "skill_id": self.skill_id,
            "category": self.category,
        }


@dataclass
class ToolResult:
    """Result of executing a tool."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "warnings": self.warnings,
        }


class ToolRegistry:
    """Registry of all executable tools across all skills."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._skill_index: Dict[str, List[str]] = {}
        self._category_index: Dict[str, List[str]] = {}

    def discover_all(self, skills_base: Optional[Path] = None) -> int:
        """Scan all skills for tool modules and register them."""
        base = skills_base or ROOT / "skills"
        count = 0

        for skill_dir in sorted(base.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "skill.json"
            if not skill_file.exists():
                continue

            tools_dir = skill_dir / "tools"
            if not tools_dir.exists():
                continue

            # Discover skill_id
            import json
            try:
                with open(skill_file) as f:
                    skill_data = json.load(f)
                skill_id = skill_data.get("skill_id", skill_dir.name)
            except (json.JSONDecodeError, IOError):
                skill_id = skill_dir.name

            # Load each tool module
            for tool_file in sorted(tools_dir.glob("*.py")):
                if tool_file.name.startswith("_"):
                    continue
                module_count = self._load_tool_module(tool_file, skill_id)
                count += module_count

        logger.info(f"Discovered {count} tools across {len(self._skill_index)} skills")
        return count

    def _load_tool_module(self, tool_file: Path, skill_id: str) -> int:
        """Load a single tool module and register its tools."""
        count = 0
        try:
            module_name = f"skills.{skill_id.replace('skill_', '')}.tools.{tool_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, tool_file)

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check for register function
                if hasattr(module, "register"):
                    module.register(self)

                # Check for tools list
                if hasattr(module, "tools"):
                    for tool_def in module.tools:
                        if isinstance(tool_def, dict):
                            t = ToolDefinition(
                                name=tool_def["name"],
                                description=tool_def.get("description", ""),
                                parameters=tool_def.get("parameters", {}),
                                returns=tool_def.get("returns", {}),
                                skill_id=skill_id,
                                category=tool_def.get("category", ""),
                                fn=tool_def.get("fn"),
                            )
                            self._register_tool(t)
                            count += 1
                        elif isinstance(tool_def, ToolDefinition):
                            tool_def.skill_id = tool_def.skill_id or skill_id
                            self._register_tool(tool_def)
                            count += 1

        except Exception as e:
            logger.warning(f"Failed to load tool module {tool_file}: {e}")

        return count

    def _register_tool(self, tool: ToolDefinition):
        """Register a single tool."""
        if not tool.name:
            return
        self._tools[tool.name] = tool
        self._skill_index.setdefault(tool.skill_id, []).append(tool.name)
        if tool.category:
            self._category_index.setdefault(tool.category, []).append(tool.name)

    def register(self, tool: ToolDefinition):
        """Public registration API for tool modules."""
        self._register_tool(tool)

    def get(self, tool_name: str) -> Optional[ToolDefinition]:
        return self._tools.get(tool_name)

    def get_by_skill(self, skill_id: str) -> List[ToolDefinition]:
        return [self._tools[n] for n in self._skill_index.get(skill_id, []) if n in self._tools]

    def get_by_category(self, category: str) -> List[ToolDefinition]:
        return [self._tools[n] for n in self._category_index.get(category, []) if n in self._tools]

    def execute(self, tool_name: str, params: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool by name with parameters."""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(success=False, error=f"Tool not found: {tool_name}")
        if not tool.fn:
            return ToolResult(success=False, error=f"Tool {tool_name} has no executable function")

        try:
            result = tool.fn(**(params or {}))
            if isinstance(result, ToolResult):
                return result
            return ToolResult(success=True, data=result)
        except Exception as e:
            logger.exception(f"Tool {tool_name} execution failed")
            return ToolResult(success=False, error=str(e))

    def list_tools(self, skill_id: Optional[str] = None) -> List[dict]:
        """List all tools (optionally filtered by skill)."""
        if skill_id:
            return [t.to_dict() for t in self.get_by_skill(skill_id)]
        return [t.to_dict() for t in self._tools.values()]

    def get_stats(self) -> dict:
        return {
            "total_tools": len(self._tools),
            "skills_with_tools": len(self._skill_index),
            "categories": list(self._category_index.keys()),
        }


# Global singleton
_global_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
        _global_registry.discover_all()
    return _global_registry
