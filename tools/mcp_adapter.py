#!/usr/bin/env python3
"""
MCP Tool Adapter — Wraps skill tools as MCP-compatible tool definitions.

MCP (Model Context Protocol) is the standard for exposing tools to AI agents.
This adapter converts ToolRegistry tools into MCP-compatible schemas that
OpenCode agents can discover and invoke.

Usage:
    from tools.mcp_adapter import MCPToolAdapter
    
    adapter = MCPToolAdapter(registry)
    mcp_tools = adapter.get_tools()  # List of MCP tool definitions
    result = adapter.call_tool("analyze_pipeline", {"lead_ids": [1]})
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)


class MCPToolAdapter:
    """Wraps skill tools as MCP-compatible definitions."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def get_tools(self, skill_filter: Optional[str] = None) -> List[dict]:
        """Get all tools as MCP-compatible tool definitions."""
        tools = self.registry.list_tools(skill_filter)
        mcp_tools = []
        for t in tools:
            mcp_tools.append({
                "name": t["name"],
                "description": t["description"],
                "inputSchema": {
                    "type": "object",
                    "properties": t.get("parameters", {}).get("properties", {}),
                    "required": t.get("parameters", {}).get("required", []),
                },
            })
        return mcp_tools

    def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> dict:
        """Execute a tool with MCP-compatible response format."""
        result = self.registry.execute(name, arguments or {})
        return {
            "tool": name,
            "success": result.success,
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result.to_dict(), indent=2)
                    if not isinstance(result.data, str)
                    else result.data,
                }
            ],
            "isError": not result.success,
        }

    def get_mcp_manifest(self) -> dict:
        """Return an MCP server manifest for tool discovery."""
        return {
            "schemaVersion": "1.0",
            "name": "odoo-skill-platform",
            "description": "Odoo AI Skill Platform — Executable Implementation Tools",
            "tools": self.get_tools(),
            "capabilities": {
                "tools": {
                    "listChanged": True,
                }
            },
        }

    def get_required_mcp_tools(self, skill_id: str) -> List[str]:
        """Return the MCP tools required by a skill (from skill.json)."""
        from agents.opencode.skill_loader import get_loader
        loader = get_loader()
        skill = loader.load(skill_id)
        if skill:
            return skill.skill_data.get("required_tools", [])
        return []
