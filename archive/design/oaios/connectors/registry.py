#!/usr/bin/env python3
"""
Connector Registry — Discovers, manages, and executes runtime connectors.

Connectors are the bridge between the Digital Twin and real infrastructure:
- PostgreSQL databases
- Odoo ORM/Shell
- Docker containers
- Git repositories
- System monitoring

Usage:
    from oaios.connectors.registry import ConnectorRegistry
    
    registry = ConnectorRegistry()
    registry.discover()
    registry.register("postgres", PostgresConnector(config))
    data = registry.execute("postgres", "fetch")
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class ConnectorInfo:
    """Metadata for a registered connector."""
    name: str
    type: str  # database, git, docker, monitoring, odoo
    description: str = ""
    status: str = "registered"
    last_call: str = ""
    error_count: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "last_call": self.last_call,
        }


class ConnectorRegistry:
    """Registry of runtime connectors for Digital Twin synchronization."""

    BUILTIN_CONNECTORS = {
        "postgres": {
            "type": "database",
            "description": "PostgreSQL database connector for schema inspection and query analysis",
            "sample_data": {
                "nodes": [
                    {"id": "db_main", "type": "database", "name": "Main Database",
                     "version": "16.4", "health": "healthy", "properties": {"size_mb": 2048}},
                    {"id": "table_res_partner", "type": "model", "name": "res_partner",
                     "version": "19.0", "properties": {"row_count": 15230, "field_count": 42}},
                ],
                "edges": [
                    {"source": "table_res_partner", "target": "db_main", "type": "contained_in"},
                ],
            },
        },
        "odoo_orm": {
            "type": "odoo",
            "description": "Odoo ORM connector for live model introspection",
            "sample_data": {
                "nodes": [
                    {"id": "model_crm_lead", "type": "model", "name": "crm.lead",
                     "version": "19.0", "health": "healthy",
                     "properties": {"fields_count": 85, "record_count": 12450}},
                    {"id": "module_crm", "type": "module", "name": "CRM",
                     "version": "1.9", "health": "healthy", "properties": {"installable": True}},
                ],
                "edges": [
                    {"source": "model_crm_lead", "target": "module_crm", "type": "defined_in"},
                ],
            },
        },
        "git": {
            "type": "git",
            "description": "Git repository connector for source code analysis",
            "sample_data": {
                "nodes": [
                    {"id": "repo_main", "type": "service", "name": "Main Repository",
                     "version": "main", "health": "healthy",
                     "properties": {"branch": "main", "last_commit": "2026-07-17"}},
                ],
                "edges": [],
            },
        },
        "docker": {
            "type": "docker",
            "description": "Docker connector for container and service discovery",
            "sample_data": {
                "nodes": [
                    {"id": "container_odoo", "type": "container", "name": "odoo-app",
                     "version": "19.0", "health": "healthy",
                     "properties": {"image": "odoo:19.0", "status": "running"}},
                    {"id": "container_db", "type": "container", "name": "odoo-db",
                     "version": "16", "health": "healthy",
                     "properties": {"image": "postgres:16", "status": "running"}},
                ],
                "edges": [
                    {"source": "container_odoo", "target": "container_db", "type": "depends_on"},
                ],
            },
        },
    }

    def __init__(self):
        self._connectors: Dict[str, ConnectorInfo] = {}
        self._handlers: Dict[str, Callable] = {}

    def discover(self) -> List[str]:
        """Discover available built-in connectors."""
        discovered = []
        for name, info in self.BUILTIN_CONNECTORS.items():
            self._connectors[name] = ConnectorInfo(
                name=name, type=info["type"], description=info["description"]
            )
            discovered.append(name)
        return discovered

    def register(self, name: str, connector_type: str,
                 handler: Optional[Callable] = None,
                 description: str = ""):
        """Register a custom connector."""
        self._connectors[name] = ConnectorInfo(
            name=name, type=connector_type, description=description
        )
        if handler:
            self._handlers[name] = handler

    def execute(self, name: str, action: str = "fetch",
                params: dict = None) -> dict:
        """Execute a connector action."""
        connector = self._connectors.get(name)
        if not connector:
            return {"error": f"Connector not found: {name}"}

        # Use registered handler or sample data
        handler = self._handlers.get(name)
        if handler:
            try:
                result = handler(action=action, params=params or {})
                connector.last_call = __import__('datetime').datetime.now().isoformat()
                return result
            except Exception as e:
                connector.error_count += 1
                return {"error": str(e)}

        # Fall back to sample data for built-in connectors
        builtin = self.BUILTIN_CONNECTORS.get(name)
        if builtin:
            return builtin["sample_data"]

        return {"error": f"No handler for connector: {name}"}

    def get(self, name: str) -> Optional[ConnectorInfo]:
        return self._connectors.get(name)

    def list(self) -> Dict[str, ConnectorInfo]:
        return dict(self._connectors)

    def list_available_types(self) -> List[str]:
        return list(set(c.type for c in self._connectors.values()))
