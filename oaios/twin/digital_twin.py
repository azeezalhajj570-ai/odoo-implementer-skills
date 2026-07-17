#!/usr/bin/env python3
"""
Digital Twin Engine — Maintains a continuously synchronized Digital Twin
of every managed Odoo deployment across source, database, infrastructure,
and runtime dimensions.

Usage:
    from oaios.twin.digital_twin import DigitalTwin
    
    twin = DigitalTwin(environment_id="prod_customer_a")
    twin.initialize(connectors=connector_registry)
    twin.sync_all()
    model = twin.get_model()
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


class NodeType(str, Enum):
    MODULE = "module"
    MODEL = "model"
    FIELD = "field"
    VIEW = "view"
    SECURITY_GROUP = "security_group"
    USER = "user"
    COMPANY = "company"
    SERVER = "server"
    DATABASE = "database"
    CONTAINER = "container"
    SERVICE = "service"
    CRON = "cron"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    BUSINESS_PROCESS = "business_process"


class SyncStatus(str, Enum):
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    STALE = "stale"
    UNREACHABLE = "unreachable"


@dataclass
class TwinNode:
    """A single node in the Digital Twin graph."""
    id: str
    type: NodeType
    name: str
    properties: dict = field(default_factory=dict)
    state: str = "unknown"
    version: str = ""
    health: str = "unknown"
    risk_score: float = 0.0
    last_updated: str = ""
    confidence: float = 1.0
    synced_at: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "version": self.version,
            "health": self.health,
            "risk_score": self.risk_score,
            "last_updated": self.last_updated,
            "confidence": self.confidence,
            "synced_at": self.synced_at,
        }


@dataclass
class TwinRelation:
    """A relationship between two Digital Twin nodes."""
    source_id: str
    target_id: str
    relation_type: str  # depends_on, contains, implements, runs_on, etc.
    properties: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.relation_type,
        }


@dataclass
class EnvironmentSnapshot:
    """A point-in-time snapshot of the Digital Twin."""
    snapshot_id: str
    timestamp: str
    node_count: int
    edge_count: int
    health_summary: str
    change_count: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.snapshot_id,
            "timestamp": self.timestamp,
            "nodes": self.node_count,
            "edges": self.edge_count,
            "health": self.health_summary,
            "changes": self.change_count,
        }


class DigitalTwin:
    """Continuously synchronized Digital Twin of an Odoo environment."""

    def __init__(self, environment_id: str, storage_path: Optional[Path] = None):
        self.environment_id = environment_id
        self.storage_path = storage_path or ROOT / "output" / "twins" / f"{environment_id}.json"
        self.nodes: Dict[str, TwinNode] = {}
        self.edges: List[TwinRelation] = []
        self.snapshots: List[EnvironmentSnapshot] = []
        self._connectors = None
        self._last_sync: Optional[str] = None

    def initialize(self, connectors) -> dict:
        """Initialize the Digital Twin with connector registry."""
        self._connectors = connectors
        self._load()
        logger.info(f"Digital Twin initialized: {self.environment_id}")
        return {"twin_id": self.environment_id, "node_count": len(self.nodes)}

    def sync_all(self) -> int:
        """Synchronize all dimensions of the Digital Twin."""
        if not self._connectors:
            logger.warning("No connectors initialized")
            return 0

        changes = 0
        before_count = len(self.nodes)

        for connector_name, connector in self._connectors.list().items():
            try:
                data = connector.fetch()
                self._apply_connector_data(connector_name, data)
                changes += 1
            except Exception as e:
                logger.warning(f"Connector {connector_name} failed: {e}")

        self._last_sync = datetime.now(timezone.utc).isoformat()

        # Record snapshot
        snapshot = EnvironmentSnapshot(
            snapshot_id=f"snap_{datetime.now():%Y%m%d_%H%M%S}",
            timestamp=self._last_sync,
            node_count=len(self.nodes),
            edge_count=len(self.edges),
            health_summary=self._compute_health_summary(),
            change_count=len(self.nodes) - before_count,
        )
        self.snapshots.append(snapshot)
        self._save()

        logger.info(f"Sync complete: {len(self.nodes)} nodes, {len(self.edges)} edges")
        return changes

    def _apply_connector_data(self, connector_name: str, data: dict):
        """Apply fetched data from a connector to the Digital Twin."""
        for node_data in data.get("nodes", []):
            nid = node_data.get("id", f"{connector_name}_{len(self.nodes)}")
            node = TwinNode(
                id=nid,
                type=NodeType(node_data.get("type", "service")),
                name=node_data.get("name", nid),
                properties=node_data.get("properties", {}),
                state=node_data.get("state", "unknown"),
                version=node_data.get("version", ""),
                health=node_data.get("health", "unknown"),
                synced_at=datetime.now(timezone.utc).isoformat(),
                confidence=node_data.get("confidence", 0.8),
            )
            self.nodes[nid] = node

        for edge_data in data.get("edges", []):
            edge = TwinRelation(
                source_id=edge_data["source"],
                target_id=edge_data["target"],
                relation_type=edge_data.get("type", "depends_on"),
            )
            # Avoid duplicates
            if not any(e.source_id == edge.source_id and
                      e.target_id == edge.target_id for e in self.edges):
                self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[TwinNode]:
        return self.nodes.get(node_id)

    def get_nodes_by_type(self, node_type: NodeType) -> List[TwinNode]:
        return [n for n in self.nodes.values() if n.type == node_type]

    def find_relations(self, node_id: str) -> List[TwinRelation]:
        return [e for e in self.edges
                if e.source_id == node_id or e.target_id == node_id]

    def search(self, query: str) -> List[TwinNode]:
        q = query.lower()
        return [n for n in self.nodes.values()
                if q in n.name.lower() or q in n.id.lower()]

    def compute_risk_score(self) -> float:
        """Compute overall risk score across all nodes."""
        if not self.nodes:
            return 0.0
        high_risk = sum(1 for n in self.nodes.values() if n.risk_score > 0.5)
        return high_risk / max(len(self.nodes), 1)

    def _compute_health_summary(self) -> str:
        healthy = sum(1 for n in self.nodes.values() if n.health == "healthy")
        total = len(self.nodes)
        if total == 0:
            return "unknown"
        ratio = healthy / total
        if ratio > 0.9:
            return "healthy"
        elif ratio > 0.7:
            return "degraded"
        return "critical"

    def to_model_dict(self) -> dict:
        """Export the full Digital Twin model."""
        return {
            "environment_id": self.environment_id,
            "last_sync": self._last_sync,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
            "snapshots": [s.to_dict() for s in self.snapshots[-10:]],
            "statistics": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": self._count_node_types(),
                "health_summary": self._compute_health_summary(),
                "overall_risk": self.compute_risk_score(),
            },
        }

    def _count_node_types(self) -> dict:
        counts = {}
        for n in self.nodes.values():
            t = n.type.value
            counts[t] = counts.get(t, 0) + 1
        return counts

    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                for nid, ndata in data.get("nodes", {}).items():
                    node = TwinNode(id=nid, type=NodeType(ndata["type"]),
                                    name=ndata["name"], **{k: v for k, v in ndata.items()
                                                           if k not in ("id", "type", "name")})
                    self.nodes[nid] = node
                for edata in data.get("edges", []):
                    self.edges.append(TwinRelation(**edata))
                for sdata in data.get("snapshots", []):
                    self.snapshots.append(EnvironmentSnapshot(**sdata))
            except Exception as e:
                logger.warning(f"Could not load Digital Twin: {e}")

    def _save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump(self.to_model_dict(), f, indent=2)
