#!/usr/bin/env python3
"""
Experience Memory — Long-term operational memory for the Autonomous Odoo Consultant.

Stores successful/ failed implementations, common migration issues,
performance optimizations, security findings, configuration patterns,
and implementation templates.

The system improves future planning by consulting prior outcomes.

Usage:
    from memory.memory import ExperienceMemory
    
    memory = ExperienceMemory()
    memory.record_project(project_record)
    similar = memory.find_similar("CRM implementation with lead scoring")
    lessons = memory.get_lessons_for_domain("crm")
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Lesson:
    """A lesson learned from a project or task."""
    category: str  # implementation, migration, performance, security, configuration
    title: str
    description: str
    domain: str = ""
    severity: str = "info"  # info, warning, critical
    source_project: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "domain": self.domain,
            "severity": self.severity,
            "tags": self.tags,
        }


@dataclass
class ProjectRecord:
    """Record of a completed project."""
    project_id: str
    name: str
    domain: str
    task_type: str
    completed_at: str
    success: bool
    effort_hours: float
    phases_completed: int = 0
    phases_failed: int = 0
    lessons: List[Lesson] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "domain": self.domain,
            "success": self.success,
            "effort_hours": self.effort_hours,
            "lessons_count": len(self.lessons),
        }


class ExperienceMemory:
    """Long-term operational memory for improving future planning."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or ROOT / "output" / "experience_memory.json"
        self._projects: Dict[str, ProjectRecord] = {}
        self._lessons: List[Lesson] = []
        self._patterns: Dict[str, List[dict]] = {}
        self._load()

    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                for p in data.get("projects", []):
                    record = ProjectRecord(**p)
                    self._projects[record.project_id] = record
                for l in data.get("lessons", []):
                    self._lessons.append(Lesson(**l))
                self._patterns = data.get("patterns", {})
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load experience memory: {e}")

    def _save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump({
                "projects": [p.to_dict() for p in self._projects.values()],
                "lessons": [l.to_dict() for l in self._lessons],
                "patterns": self._patterns,
            }, f, indent=2)

    def record_project(self, record: ProjectRecord):
        """Record a completed project."""
        self._projects[record.project_id] = record
        self._lessons.extend(record.lessons)
        self._extract_patterns(record)
        self._save()
        logger.info(f"Recorded project: {record.name} ({record.domain})")

    def record_lesson(self, lesson: Lesson):
        """Record a single lesson."""
        self._lessons.append(lesson)
        self._save()

    def find_similar(self, description: str, domain: str = "",
                     top_n: int = 5) -> List[ProjectRecord]:
        """Find similar projects by keyword matching."""
        desc_lower = description.lower()
        scored = []

        for record in self._projects.values():
            score = 0
            if domain and record.domain == domain:
                score += 3
            # Simple keyword matching
            match_words = set(desc_lower.split()) & set(record.name.lower().split())
            score += len(match_words)
            if score > 0:
                scored.append((score, record))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:top_n]]

    def get_lessons_for_domain(self, domain: str) -> List[Lesson]:
        """Get all lessons for a specific domain."""
        return [l for l in self._lessons if l.domain == domain]

    def get_lessons_by_category(self, category: str) -> List[Lesson]:
        return [l for l in self._lessons if l.category == category]

    def get_pattern(self, key: str) -> Optional[dict]:
        return self._patterns.get(key)

    def store_pattern(self, key: str, pattern: dict):
        self._patterns[key] = pattern
        self._save()

    def _extract_patterns(self, record: ProjectRecord):
        """Extract reusable patterns from a project record."""
        if record.success:
            pattern_key = f"successful_{record.domain}_{record.task_type}"
            self._patterns[pattern_key] = {
                "domain": record.domain,
                "task_type": record.task_type,
                "effort_hours": record.effort_hours,
                "phases": record.phases_completed,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }

    def get_statistics(self) -> dict:
        """Get memory statistics."""
        domains = set(r.domain for r in self._projects.values())
        categories = set(l.category for l in self._lessons)
        return {
            "total_projects": len(self._projects),
            "successful_projects": sum(1 for r in self._projects.values() if r.success),
            "failed_projects": sum(1 for r in self._projects.values() if not r.success),
            "total_lessons": len(self._lessons),
            "domains": sorted(domains),
            "lesson_categories": sorted(categories),
            "stored_patterns": len(self._patterns),
        }
