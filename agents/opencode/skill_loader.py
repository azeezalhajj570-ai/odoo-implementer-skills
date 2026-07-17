#!/usr/bin/env python3
"""
OpenCode Skill Loader — Dynamic Skill Discovery, Loading, Caching, and Unloading

The Skill Loader is the core of the OpenCode AI Skill Platform.
It discovers installed skills, loads them on demand, caches them for
performance, and unloads them when no longer needed.

Usage:
    from agents.opencode.skill_loader import SkillLoader
    
    loader = SkillLoader()
    loader.discover()
    skill = loader.load("skill_crm")
    capabilities = skill.get_capabilities()
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


class SkillPackage:
    """A loaded skill package with all its components accessible."""

    def __init__(self, path: Path):
        self.path = path
        self.skill_data = {}
        self.knowledge = {}
        self.capabilities = []
        self.evaluation_prompts = []
        self._load()

    def _load(self):
        """Load all components of the skill package."""
        self._load_skill_json()
        self._load_knowledge()
        self._load_capabilities()
        self._load_evaluation()

    def _load_skill_json(self):
        skill_file = self.path / "skill.json"
        if skill_file.exists():
            with open(skill_file) as f:
                self.skill_data = json.load(f)
            logger.info(f"Loaded skill: {self.skill_data.get('name', self.path.name)}")
        else:
            logger.warning(f"No skill.json found in {self.path}")

    def _load_knowledge(self):
        knowledge_file = self.path / "knowledge.json"
        if knowledge_file.exists():
            with open(knowledge_file) as f:
                self.knowledge = json.load(f)

    def _load_capabilities(self):
        cap_file = self.path / "capability.json"
        if cap_file.exists():
            with open(cap_file) as f:
                self.capabilities = json.load(f).get("capabilities", [])
        # Also get from skill.json
        if self.skill_data.get("capabilities"):
            if not self.capabilities:
                self.capabilities = self.skill_data["capabilities"]

    def _load_evaluation(self):
        eval_dir = self.path / "evaluation"
        if eval_dir.exists():
            for eval_file in sorted(eval_dir.glob("*.json")):
                with open(eval_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.evaluation_prompts.extend(data)
                    else:
                        self.evaluation_prompts.append(data)

    @property
    def skill_id(self) -> Optional[str]:
        return self.skill_data.get("skill_id")

    @property
    def name(self) -> Optional[str]:
        return self.skill_data.get("name")

    @property
    def domain(self) -> Optional[str]:
        return self.skill_data.get("domain")

    @property
    def version(self) -> Optional[str]:
        return self.skill_data.get("version")

    def get_capabilities(self) -> List[dict]:
        return self.capabilities

    def has_capability(self, cap_id: str) -> bool:
        return any(c.get("id") == cap_id for c in self.capabilities)

    def get_dependencies(self) -> List[dict]:
        return self.skill_data.get("dependencies", {}).get("skills", [])

    def get_compatible_agents(self) -> List[str]:
        return self.skill_data.get("compatible_agents", [])

    def get_rag_chunks(self) -> List[dict]:
        rag_dir = self.path / "rag"
        chunks = []
        if rag_dir.exists():
            for chunk_file in rag_dir.glob("*.json"):
                with open(chunk_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        chunks.extend(data)
                    else:
                        chunks.append(data)
        return chunks

    def get_playbooks(self) -> List[Path]:
        playbook_dir = self.path / "playbooks"
        if playbook_dir.exists():
            return sorted(playbook_dir.glob("*.md"))
        return []

    def get_prompt(self) -> Optional[str]:
        prompt_file = self.path / "prompt.md"
        if prompt_file.exists():
            return prompt_file.read_text()
        return None

    def get_knowledge_value(self, key: str, default=None):
        return self.knowledge.get(key, default)

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "domain": self.domain,
            "version": self.version,
            "capabilities": [c.get("id") for c in self.capabilities],
            "dependencies": [d.get("skill_id") for d in self.get_dependencies()],
            "compatible_agents": self.get_compatible_agents(),
            "path": str(self.path),
            "evaluation_count": len(self.evaluation_prompts),
        }

    def __repr__(self):
        return f"<SkillPackage {self.skill_id} v{self.version}>"


class SkillLoader:
    """Discovers, loads, caches, and unloads skill packages."""

    def __init__(self, skill_paths: Optional[List[Path]] = None):
        self.skill_paths = skill_paths or [ROOT / "skills"]
        self._cache: Dict[str, SkillPackage] = {}
        self._discovered: Dict[str, Path] = {}
        self._load_order: List[str] = []

    def discover(self) -> Dict[str, Path]:
        """Scan all skill paths and discover available skills."""
        self._discovered = {}
        for base_path in self.skill_paths:
            if not base_path.exists():
                continue
            for skill_dir in base_path.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill_file = skill_dir / "skill.json"
                if skill_file.exists():
                    try:
                        with open(skill_file) as f:
                            skill_data = json.load(f)
                        skill_id = skill_data.get("skill_id")
                        if skill_id:
                            self._discovered[skill_id] = skill_dir
                            logger.info(f"Discovered skill: {skill_id} at {skill_dir}")
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Invalid skill.json in {skill_dir}: {e}")

        logger.info(f"Discovered {len(self._discovered)} skills")
        return self._discovered

    def load(self, skill_id: str) -> Optional[SkillPackage]:
        """Load a skill by ID (with caching)."""
        if skill_id in self._cache:
            logger.debug(f"Cache hit: {skill_id}")
            return self._cache[skill_id]

        skill_path = self._discovered.get(skill_id)
        if not skill_path:
            logger.error(f"Skill not found: {skill_id}")
            return None

        skill = SkillPackage(skill_path)
        self._cache[skill_id] = skill
        self._load_order.append(skill_id)
        logger.info(f"Loaded skill: {skill_id} v{skill.version}")
        return skill

    def load_all(self) -> List[SkillPackage]:
        """Load all discovered skills."""
        skills = []
        for skill_id in self._discovered:
            skill = self.load(skill_id)
            if skill:
                skills.append(skill)
        return skills

    def preload(self, skill_ids: List[str]) -> List[SkillPackage]:
        """Preload a specific set of skills into cache."""
        return [s for sid in skill_ids if (s := self.load(sid))]

    def unload(self, skill_id: str) -> bool:
        """Remove a skill from the cache."""
        if skill_id in self._cache:
            del self._cache[skill_id]
            if skill_id in self._load_order:
                self._load_order.remove(skill_id)
            logger.info(f"Unloaded skill: {skill_id}")
            return True
        return False

    def unload_all(self):
        """Clear the entire skill cache."""
        self._cache.clear()
        self._load_order.clear()
        logger.info("All skills unloaded")

    def reload(self, skill_id: str) -> Optional[SkillPackage]:
        """Force reload a skill (clear cache and re-load)."""
        self.unload(skill_id)
        return self.load(skill_id)

    def is_loaded(self, skill_id: str) -> bool:
        return skill_id in self._cache

    def get_loaded(self) -> List[SkillPackage]:
        """Get all currently loaded skills in load order."""
        return [self._cache[sid] for sid in self._load_order if sid in self._cache]

    def find_by_capability(self, cap_id: str) -> List[SkillPackage]:
        """Find all loaded skills that have a specific capability."""
        return [s for s in self.get_loaded() if s.has_capability(cap_id)]

    def find_by_domain(self, domain: str) -> List[SkillPackage]:
        """Find all loaded skills for a domain."""
        return [s for s in self.get_loaded() if s.domain and s.domain.lower() == domain.lower()]

    def find_by_agent(self, agent_type: str) -> List[SkillPackage]:
        """Find all loaded skills compatible with an agent type."""
        return [s for s in self.get_loaded() if agent_type in s.get_compatible_agents()]

    def status(self) -> dict:
        """Return the current loader status."""
        return {
            "discovered_count": len(self._discovered),
            "loaded_count": len(self._cache),
            "loaded_skills": [s.to_dict() for s in self.get_loaded()],
            "discovered_skills": list(self._discovered.keys()),
        }

    def get_cache_stats(self) -> dict:
        """Return cache performance statistics."""
        return {
            "cache_size": len(self._cache),
            "load_order": self._load_order,
            "skills": {sid: str(p) for sid, p in self._discovered.items()},
        }


# Singleton instance for application-wide use
_global_loader: Optional[SkillLoader] = None


def get_loader() -> SkillLoader:
    """Get or create the global SkillLoader singleton."""
    global _global_loader
    if _global_loader is None:
        _global_loader = SkillLoader()
        _global_loader.discover()
    return _global_loader
