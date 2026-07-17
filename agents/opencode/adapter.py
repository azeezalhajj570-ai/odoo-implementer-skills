#!/usr/bin/env python3
"""
OpenCode Agent Adapter — Main Integration Layer for OpenCode Agents

The Agent Adapter is the primary interface between OpenCode agents and the
Odoo AI Skill Platform. It handles:
- Skill discovery, loading, and dependency resolution
- Agent-to-skill matching based on capabilities
- Context building for loaded skills
- Prompt assembly from loaded skills
- Execution orchestration across multiple skills

Usage:
    from agents.opencode.adapter import OpenCodeAdapter
    
    adapter = OpenCodeAdapter()
    adapter.initialize()
    
    # Load skills for a task
    session = adapter.create_session(
        agent_type="developer",
        required_capabilities=["lead_scoring", "email_marketing"],
        odoo_version="19.0"
    )
    
    # Get assembled prompts for the loaded skills
    prompts = session.get_prompts()
    
    # Get all context for RAG
    context = session.get_context()
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

from agents.opencode.skill_loader import SkillLoader, SkillPackage
from agents.opencode.skill_registry import SkillRegistry
from agents.opencode.dependency_manager import DependencyManager

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


class AgentType(str, Enum):
    PLANNER = "planner"
    MANAGER = "manager"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    FUNCTIONAL = "functional"
    QA = "qa"
    DOCUMENTATION = "documentation"
    REVIEWER = "reviewer"
    CODING = "coding"
    WORKER = "worker"


AGENT_CAPABILITY_MAP = {
    AgentType.PLANNER: ["solution_design", "gap_analysis", "project_planning"],
    AgentType.MANAGER: ["coordination", "progress_tracking"],
    AgentType.DEVELOPER: ["python", "xml", "javascript", "owl", "security", "orm", "api"],
    AgentType.RESEARCHER: ["knowledge_retrieval", "source_analysis"],
    AgentType.FUNCTIONAL: ["business_process", "configuration", "best_practices"],
    AgentType.QA: ["testing", "validation", "quality_assurance"],
    AgentType.DOCUMENTATION: ["documentation", "diagram_generation"],
    AgentType.REVIEWER: ["code_review", "architecture_review"],
    AgentType.CODING: ["implementation", "refactoring", "debugging"],
    AgentType.WORKER: ["execution", "automation"],
}


@dataclass
class SkillSession:
    """A session holding a set of loaded skills for a specific task."""

    session_id: str
    agent_type: AgentType
    odoo_version: str
    skill_ids: List[str]
    skills: Dict[str, SkillPackage] = field(default_factory=dict)
    context: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def get_prompts(self) -> Dict[str, str]:
        """Get assembled prompt texts from all loaded skills."""
        prompts = {}
        for sid, skill in self.skills.items():
            prompt = skill.get_prompt()
            if prompt:
                prompts[sid] = prompt
        return prompts

    def get_capabilities(self) -> List[dict]:
        """Get all capabilities from loaded skills."""
        caps = []
        for skill in self.skills.values():
            caps.extend(skill.get_capabilities())
        return caps

    def get_knowledge(self) -> dict:
        """Aggregate knowledge from all loaded skills."""
        knowledge = {}
        for skill in self.skills.values():
            for key, value in skill.knowledge.items():
                if key not in knowledge:
                    knowledge[key] = []
                if isinstance(value, list):
                    knowledge[key].extend(value)
                else:
                    knowledge[key].append(value)
        return knowledge

    def get_context(self) -> dict:
        """Build full context dict for AI agent consumption."""
        context = {
            "session_id": self.session_id,
            "agent_type": self.agent_type.value,
            "odoo_version": self.odoo_version,
            "skills": {
                sid: {
                    "name": skill.name,
                    "domain": skill.domain,
                    "capabilities": [c.get("id") for c in skill.get_capabilities()],
                }
                for sid, skill in self.skills.items()
            },
            "capabilities": self.get_capabilities(),
            "rag_chunks": self._get_all_rag_chunks(),
            "evaluation_count": sum(len(s.evaluation_prompts) for s in self.skills.values()),
        }
        return context

    def _get_all_rag_chunks(self) -> List[dict]:
        chunks = []
        for skill in self.skills.values():
            chunks.extend(skill.get_rag_chunks())
        return chunks

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "agent_type": self.agent_type.value,
            "odoo_version": self.odoo_version,
            "skills_loaded": list(self.skills.keys()),
            "created_at": self.created_at,
        }


class OpenCodeAdapter:
    """Main integration layer between OpenCode agents and the Skill Platform."""

    def __init__(self):
        self.loader = SkillLoader()
        self.registry = SkillRegistry()
        self.dependency_manager = None
        self._initialized = False
        self._sessions: Dict[str, SkillSession] = {}

    def initialize(self) -> dict:
        """Initialize the adapter: discover skills, build registry, prepare dependency manager."""
        logger.info("Initializing OpenCode Skill Platform Adapter...")

        # Step 1: Discover skills
        discovered = self.loader.discover()
        logger.info(f"Discovered {len(discovered)} skills")

        # Step 2: Build registry index
        indexed = self.registry.index_all()
        logger.info(f"Indexed {indexed} skills")

        # Step 3: Initialize dependency manager
        self.dependency_manager = DependencyManager(self.registry)

        self._initialized = True

        return {
            "status": "initialized",
            "discovered_skills": len(discovered),
            "indexed_skills": indexed,
            "capabilities": len(self.registry._capability_index),
            "domains": list(self.registry._domain_index.keys()),
        }

    def create_session(self, agent_type: str,
                       required_capabilities: Optional[List[str]] = None,
                       skill_ids: Optional[List[str]] = None,
                       odoo_version: str = "19.0") -> SkillSession:
        """Create a new skill session for an agent."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized. Call initialize() first.")

        agent = AgentType(agent_type)

        # Determine which skills to load
        if not skill_ids and required_capabilities:
            skill_ids = self.dependency_manager.find_optimal_set(required_capabilities)
        elif not skill_ids:
            skill_ids = self.registry.find_by_agent(agent_type)
            if not skill_ids:
                # Fall back to agent capability map
                default_caps = AGENT_CAPABILITY_MAP.get(agent, [])
                skill_ids = self.dependency_manager.find_optimal_set(default_caps)

        if not skill_ids:
            raise ValueError(
                f"No skills found for agent_type={agent_type}, "
                f"capabilities={required_capabilities}"
            )

        # Resolve dependencies
        try:
            load_order = self.dependency_manager.resolve(skill_ids)
        except Exception as e:
            logger.warning(f"Dependency resolution error: {e}")
            load_order = skill_ids  # Best-effort

        # Load skills in order
        loaded_skills = {}
        for sid in load_order:
            skill = self.loader.load(sid)
            if skill:
                loaded_skills[sid] = skill

        # Create session
        session_id = f"session_{agent_type}_{datetime.now():%Y%m%d_%H%M%S}"
        session = SkillSession(
            session_id=session_id,
            agent_type=agent,
            odoo_version=odoo_version,
            skill_ids=list(loaded_skills.keys()),
            skills=loaded_skills,
        )

        self._sessions[session_id] = session
        logger.info(f"Created session {session_id}: {len(loaded_skills)} skills loaded")
        return session

    def get_session(self, session_id: str) -> Optional[SkillSession]:
        return self._sessions.get(session_id)

    def close_session(self, session_id: str) -> bool:
        """Close a session and unload its skills from cache (optional)."""
        session = self._sessions.pop(session_id, None)
        if session:
            logger.info(f"Closed session {session_id}")
            return True
        return False

    def find_skills_for_request(self, request: str) -> List[dict]:
        """Parse a natural language request and find matching skills."""
        # Simple keyword-based matching
        request_lower = request.lower()
        matches = []

        for sid, entry in self.registry._registry.items():
            data = entry["data"]
            score = 0

            # Check name match
            name = data.get("name", "").lower()
            if name in request_lower:
                score += 3

            # Check domain match
            domain = data.get("domain", "").lower()
            if domain in request_lower:
                score += 2

            # Check capability name matches
            for cap in data.get("capabilities", []):
                cap_name = cap.get("name", "").lower()
                if cap_name in request_lower:
                    score += 1

            if score > 0:
                matches.append({
                    "skill_id": sid,
                    "name": data.get("name"),
                    "score": score,
                    "capabilities": [c.get("id") for c in data.get("capabilities", [])],
                })

        return sorted(matches, key=lambda x: x["score"], reverse=True)

    def get_platform_status(self) -> dict:
        """Get full platform status."""
        return {
            "initialized": self._initialized,
            "skills_discovered": len(self.loader._discovered),
            "skills_loaded": len(self.loader._cache),
            "active_sessions": len(self._sessions),
            "registry": {
                "total_skills": len(self.registry._registry),
                "capabilities": len(self.registry._capability_index),
                "domains": list(self.registry._domain_index.keys()),
            },
            "sessions": {sid: s.to_dict() for sid, s in self._sessions.items()},
        }


# Singleton instance
_global_adapter: Optional[OpenCodeAdapter] = None


def get_adapter() -> OpenCodeAdapter:
    """Get or create the global OpenCodeAdapter singleton."""
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = OpenCodeAdapter()
        _global_adapter.initialize()
    return _global_adapter
