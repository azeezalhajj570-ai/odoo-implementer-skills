#!/usr/bin/env python3
"""
Update Manager — Detects Changes and Generates Incremental Skill Updates

Monitors source artifacts (docs, source code, OCA modules) for changes
and generates incremental updates to affected skills.

Usage:
    from agents.opencode.update_manager import UpdateManager
    
    mgr = UpdateManager()
    updates = mgr.check_for_updates(skills_base)
    if updates:
        mgr.apply_updates(updates)
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


class UpdateManager:
    """Detects stale skills and generates incremental updates."""

    def __init__(self, state_file: Optional[Path] = None):
        self.state_file = state_file or ROOT / "output" / "skill_state.json"
        self._state: Dict[str, dict] = {}
        self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._state = {}
        logger.info(f"Loaded state for {len(self._state)} skills")

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self._state, f, indent=2)

    def compute_checksum(self, skill_path: Path) -> str:
        """Compute a combined checksum for all files in a skill package."""
        hasher = hashlib.sha256()
        for file_path in sorted(skill_path.rglob("*")):
            if file_path.is_file() and file_path.suffix in {".json", ".md", ".yaml"}:
                with open(file_path, "rb") as f:
                    hasher.update(f.read())
        return hasher.hexdigest()[:16]

    def check_for_updates(self, skills_base: Optional[Path] = None) -> List[dict]:
        """Check all skills for changes since last state save. Returns list of updates."""
        base = skills_base or ROOT / "skills"
        updates = []

        for skill_dir in sorted(base.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "skill.json"
            if not skill_file.exists():
                continue

            try:
                with open(skill_file) as f:
                    skill_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            skill_id = skill_data.get("skill_id", skill_dir.name)
            current_hash = self.compute_checksum(skill_dir)
            previous_state = self._state.get(skill_id, {})

            if not previous_state:
                updates.append({
                    "skill_id": skill_id,
                    "type": "new",
                    "name": skill_data.get("name", skill_id),
                    "version": skill_data.get("version"),
                    "reason": "New skill detected",
                })
            elif previous_state.get("checksum") != current_hash:
                updates.append({
                    "skill_id": skill_id,
                    "type": "update",
                    "name": skill_data.get("name", skill_id),
                    "version": skill_data.get("version"),
                    "previous_version": previous_state.get("version"),
                    "reason": "Content change detected",
                })

            # Update state
            self._state[skill_id] = {
                "checksum": current_hash,
                "version": skill_data.get("version"),
                "name": skill_data.get("name"),
                "last_checked": datetime.now(timezone.utc).isoformat(),
            }

        # Check for removed skills (resolve skill_id from skill.json for proper matching)
        registered_skills = set(self._state.keys())
        current_skill_ids = set()
        for skill_dir in sorted(base.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "skill.json"
            if not skill_file.exists():
                continue
            try:
                with open(skill_file) as f:
                    sd = json.load(f)
                sid = sd.get("skill_id", skill_dir.name)
                current_skill_ids.add(sid)
            except (json.JSONDecodeError, IOError):
                pass
        removed = registered_skills - current_skill_ids
        for skill_id in removed:
            updates.append({
                "skill_id": skill_id,
                "type": "removed",
                "name": self._state[skill_id].get("name", skill_id),
                "reason": "Skill directory no longer exists",
            })
            del self._state[skill_id]

        self._save_state()
        logger.info(f"Found {len(updates)} updates")
        return updates

    def get_staleness(self, skill_id: str) -> Optional[dict]:
        """Get staleness info for a specific skill."""
        state = self._state.get(skill_id)
        if not state:
            return None
        last_checked = state.get("last_checked", "")
        return {
            "skill_id": skill_id,
            "version": state.get("version"),
            "last_checked": last_checked,
            "stale_days": (datetime.now(timezone.utc) - datetime.fromisoformat(last_checked)).days
            if last_checked else None,
        }

    def mark_updated(self, skill_id: str, new_version: str):
        """Mark a skill as having been updated."""
        if skill_id in self._state:
            self._state[skill_id]["version"] = new_version
            self._state[skill_id]["last_updated"] = datetime.now(timezone.utc).isoformat()
            self._save_state()

    def get_all_states(self) -> dict:
        """Get state for all tracked skills."""
        return dict(self._state)
