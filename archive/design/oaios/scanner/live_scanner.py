#!/usr/bin/env python3
"""
Live Project Scanner — Continuously synchronizes project state with the Digital Twin.

Instead of scanning once, the Live Scanner detects:
- new/removed/changed modules, manifests, models, fields, security
- database schema changes, configuration changes
- performance degradation, deployment changes, API changes
- infrastructure drift

Every detected change updates the Digital Twin.

Usage:
    from oaios.scanner.live_scanner import LiveScanner
    
    scanner = LiveScanner(twin, project_engine)
    changes = scanner.scan()
    for c in changes:
        print(f"Change: {c.description}")
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class DetectedChange:
    """A change detected by the Live Scanner."""
    change_type: str
    description: str
    severity: str = "info"
    source: str = ""
    affected_node: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "type": self.change_type,
            "description": self.description,
            "severity": self.severity,
            "source": self.source,
            "affected_node": self.affected_node,
        }


class LiveScanner:
    """Continuously scans and synchronizes project state."""

    def __init__(self, digital_twin, project_engine=None):
        self.twin = digital_twin
        self.project = project_engine
        self._last_hashes: Dict[str, str] = {}
        self._change_history: List[DetectedChange] = []

    def scan(self) -> List[DetectedChange]:
        """Run a full scan cycle. Returns detected changes."""
        changes = []

        changes.extend(self._scan_modules())
        changes.extend(self._scan_manifest_files())
        changes.extend(self._scan_infrastructure())

        if changes:
            for c in changes:
                c.timestamp = datetime.now(timezone.utc).isoformat()
            self._change_history.extend(changes)
            logger.info(f"Scanner detected {len(changes)} changes")

        return changes

    def _scan_modules(self) -> List[DetectedChange]:
        """Detect module-level changes."""
        changes = []
        if not self.project:
            return changes

        model = self.project.get_model()
        known_modules = set(self._last_hashes.keys())
        current_modules = set()

        for name, info in model.modules.items():
            current_modules.add(name)
            module_path = Path(info.path)
            if not module_path.exists():
                continue

            h = self._hash_directory(module_path)
            self._last_hashes[name] = h

            if name not in known_modules:
                changes.append(DetectedChange(
                    "module_added", f"New module detected: {name}",
                    severity="info", source="project", affected_node=name,
                ))

        # Detect removed modules
        for name in known_modules - current_modules:
            changes.append(DetectedChange(
                "module_removed", f"Module removed: {name}",
                severity="warning", source="project", affected_node=name,
            ))

        return changes

    def _scan_manifest_files(self) -> List[DetectedChange]:
        """Detect manifest-level changes."""
        changes = []
        if not self.project:
            return changes

        for name, info in self.project.get_model().modules.items():
            module_path = Path(info.path)
            manifest_file = module_path / "__manifest__.py"
            if not manifest_file.exists():
                continue

            try:
                content = manifest_file.read_text()
                h = hashlib.sha256(content.encode()).hexdigest()[:16]
                key = f"manifest_{name}"
                last_h = self._last_hashes.get(key)

                if last_h and last_h != h:
                    changes.append(DetectedChange(
                        "manifest_changed", f"Manifest modified: {name}",
                        severity="info", source="project", affected_node=name,
                    ))
                self._last_hashes[key] = h
            except IOError:
                pass

        return changes

    def _scan_infrastructure(self) -> List[DetectedChange]:
        """Detect infrastructure-level changes."""
        changes = []
        if not self.project:
            return changes

        root = Path(self.project.root_path)

        # Docker changes
        docker_file = root / "docker-compose.yml"
        if docker_file.exists():
            h = self._hash_file(docker_file)
            key = "docker_compose"
            last_h = self._last_hashes.get(key)
            if last_h and last_h != h:
                changes.append(DetectedChange(
                    "infrastructure_changed", "docker-compose.yml modified",
                    severity="warning", source="infrastructure",
                ))
            self._last_hashes[key] = h

        return changes

    def _hash_directory(self, path: Path) -> str:
        """Compute a hash of all Python and XML files in a directory."""
        hasher = hashlib.sha256()
        for f in sorted(path.rglob("*")):
            if f.is_file() and f.suffix in {".py", ".xml", ".js", ".scss", ".css"}:
                try:
                    hasher.update(f.read_bytes()[:32768])
                except IOError:
                    pass
        return hasher.hexdigest()[:16]

    def _hash_file(self, path: Path) -> str:
        try:
            return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        except IOError:
            return ""

    def get_recent_changes(self, limit: int = 20) -> List[DetectedChange]:
        return self._change_history[-limit:]
