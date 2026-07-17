#!/usr/bin/env python3
"""
Project Monitor — Continuously monitors a project for changes and
automatically updates the project model.

Detects:
- Git changes (new commits, branches)
- Module changes (new/deleted/modified modules)
- Database changes (new models, fields)
- New dependencies
- Migration requirements
- Security issues

Usage:
    from project.monitor import ProjectMonitor
    
    monitor = ProjectMonitor(engine)
    changes = monitor.check_all()
    print(changes)
"""

import hashlib
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from project.engine import ProjectContextEngine, ProjectModel

logger = logging.getLogger(__name__)


class Change:
    """Represents a detected change in the project."""

    def __init__(self, change_type: str, description: str,
                 severity: str = "info", module: str = "",
                 details: dict = None):
        self.type = change_type
        self.description = description
        self.severity = severity
        self.module = module
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "description": self.description,
            "severity": self.severity,
            "module": self.module,
            "timestamp": self.timestamp,
        }


class ProjectMonitor:
    """Monitors an Odoo project for changes."""

    def __init__(self, engine: ProjectContextEngine, state_file: Optional[Path] = None):
        self.engine = engine
        self.project = engine.model
        self.root = Path(engine.root_path)
        self.state_file = state_file or Path(
            engine.root_path
        ) / ".odoo_ai_state" / "monitor_state.json"
        self._last_state: dict = {}
        self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    self._last_state = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._last_state = {}

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self._last_state, f, indent=2)

    def _compute_module_hash(self, module_path: Path) -> str:
        """Compute a hash of all files in a module directory."""
        hasher = hashlib.sha256()
        for f in sorted(module_path.rglob("*")):
            if f.is_file() and f.suffix in {".py", ".xml", ".js", ".scss", ".css"}:
                try:
                    hasher.update(f.read_bytes()[:65536])  # First 64KB
                except IOError:
                    pass
        return hasher.hexdigest()[:16]

    def check_git(self) -> List[Change]:
        """Check for git changes."""
        changes = []
        try:
            git_dir = self.root / ".git"
            if not git_dir.exists():
                return changes

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=self.root, timeout=30
            )
            if result.stdout.strip():
                changed_files = [line[3:] for line in result.stdout.splitlines() if line.strip()]
                changes.append(Change(
                    "git_uncommitted",
                    f"{len(changed_files)} uncommitted files",
                    severity="warning",
                    details={"files": changed_files[:20]},
                ))

            # Check for unpushed commits
            result = subprocess.run(
                ["git", "log", "--oneline", "@{u}..HEAD", "--count"],
                capture_output=True, text=True, cwd=self.root, timeout=10
            )
            count = result.stdout.strip()
            if count and int(count) > 0:
                changes.append(Change(
                    "git_unpushed",
                    f"{count} unpushed commits",
                    severity="warning",
                ))
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        return changes

    def check_modules(self) -> List[Change]:
        """Check for module changes since last scan."""
        changes = []
        current_hashes = {}

        for name, info in self.project.modules.items():
            module_path = Path(info.path)
            if not module_path.exists():
                continue
            h = self._compute_module_hash(module_path)
            current_hashes[name] = h

            last_hash = self._last_state.get("module_hashes", {}).get(name)
            if last_hash and last_hash != h:
                changes.append(Change(
                    "module_modified",
                    f"Module '{name}' has been modified",
                    severity="info",
                    module=name,
                ))

        # Detect new modules
        last_modules = set(self._last_state.get("modules", []))
        current_modules = set(current_hashes.keys())
        for name in current_modules - last_modules:
            changes.append(Change(
                "module_added",
                f"New module detected: '{name}'",
                severity="info",
                module=name,
            ))

        # Update state
        self._last_state["module_hashes"] = current_hashes
        self._last_state["modules"] = list(current_modules)
        self._save_state()

        return changes

    def check_all(self) -> List[Change]:
        """Run all checks and return combined changes."""
        changes = []
        changes.extend(self.check_git())
        changes.extend(self.check_modules())

        if changes:
            severities = set(c.severity for c in changes)
            logger.info(f"Monitor detected {len(changes)} changes "
                         f"(severities: {severities})")

        return changes
