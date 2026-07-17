#!/usr/bin/env python3
"""
Multi-Agent Coordinator — Orchestrates specialist agents for complex projects.

Each specialist agent has defined capabilities, and the coordinator assigns
work based on those capabilities, tracks progress, and merges outputs.

Supported specialists:
- Functional Consultant, Business Analyst, Solution Architect
- Technical Architect, Backend Developer, Frontend Developer
- Security Specialist, Migration Specialist, QA Engineer
- Performance Engineer, Documentation Engineer, DevOps Engineer
- Database Specialist, Trainer

Usage:
    from coordinator.coordinator import MultiAgentCoordinator
    
    coordinator = MultiAgentCoordinator()
    coordinator.initialize()
    plan = coordinator.create_coordination_plan(reasoning_result)
    results = coordinator.execute_plan(plan)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from reasoning.engine import ReasoningResult

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class SpecialistProfile:
    """Profile of a specialist agent."""
    role: str
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    compatible_skills: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "name": self.name,
            "capabilities": self.capabilities,
            "skills": self.compatible_skills,
        }


@dataclass
class AgentAssignment:
    """A task assigned to a specialist agent."""
    assignment_id: str
    agent_role: str
    task_description: str
    phase_id: str = ""
    skills_required: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    output: Optional[dict] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "assignment_id": self.assignment_id,
            "agent_role": self.agent_role,
            "task": self.task_description,
            "phase_id": self.phase_id,
            "status": self.status,
        }


@dataclass
class CoordinationPlan:
    """A plan for coordinating multiple specialist agents."""
    plan_id: str
    assignments: List[AgentAssignment]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def completed_count(self) -> int:
        return sum(1 for a in self.assignments if a.status == "completed")

    @property
    def failed_count(self) -> int:
        return sum(1 for a in self.assignments if a.status == "failed")

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "total_assignments": len(self.assignments),
            "completed": self.completed_count,
            "failed": self.failed_count,
            "assignments": [a.to_dict() for a in self.assignments],
        }


class MultiAgentCoordinator:
    """Orchestrates multiple specialist agents for complex projects."""

    SPECIALISTS = [
        SpecialistProfile(
            role="functional_consultant", name="Functional Consultant",
            description="Analyzes business requirements and maps to Odoo features",
            capabilities=["requirements_analysis", "gap_analysis", "business_mapping",
                         "configuration_design", "user_stories"],
            compatible_skills=["skill_base", "skill_crm", "skill_marketing"],
        ),
        SpecialistProfile(
            role="business_analyst", name="Business Analyst",
            description="Analyzes business processes and recommends improvements",
            capabilities=["process_mapping", "workflow_analysis", "stakeholder_interviews",
                         "requirements_documentation"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="solution_architect", name="Solution Architect",
            description="Designs end-to-end Odoo solutions and evaluates trade-offs",
            capabilities=["solution_design", "architecture_review", "technology_selection",
                         "integration_design", "scalability_planning"],
            compatible_skills=["skill_base", "skill_crm", "skill_marketing"],
        ),
        SpecialistProfile(
            role="technical_architect", name="Technical Architect",
            description="Designs technical architecture, data models, and system integration",
            capabilities=["technical_design", "data_modeling", "api_design",
                         "security_architecture", "performance_design"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="backend_developer", name="Backend Developer",
            description="Develops Python models, business logic, and API endpoints",
            capabilities=["python_development", "model_creation", "business_logic",
                         "api_development", "orm_programming"],
            compatible_skills=["skill_base", "skill_crm", "skill_marketing"],
        ),
        SpecialistProfile(
            role="frontend_developer", name="Frontend Developer",
            description="Develops OWL components, JavaScript, and UI extensions",
            capabilities=["owl_components", "javascript", "ui_development",
                         "widget_creation", "view_customization"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="security_specialist", name="Security Specialist",
            description="Audits security configuration, access rights, and data protection",
            capabilities=["security_audit", "access_control_design", "vulnerability_assessment",
                         "compliance_check", "data_privacy"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="migration_specialist", name="Migration Specialist",
            description="Plans and executes version migrations and data migration",
            capabilities=["version_migration", "data_migration", "upgrade_planning",
                         "compatibility_assessment", "rollback_planning"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="qa_engineer", name="QA Engineer",
            description="Designs test plans, executes testing, and validates outputs",
            capabilities=["test_planning", "test_execution", "automated_testing",
                         "regression_testing", "performance_testing"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="performance_engineer", name="Performance Engineer",
            description="Analyzes and optimizes Odoo performance",
            capabilities=["performance_analysis", "query_optimization", "cache_strategy",
                         "bottleneck_identification", "scalability_testing"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="documentation_engineer", name="Documentation Engineer",
            description="Creates technical and user documentation",
            capabilities=["technical_writing", "user_documentation", "api_documentation",
                         "training_materials", "diagrams"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="devops_engineer", name="DevOps Engineer",
            description="Manages deployment, CI/CD, containers, and infrastructure",
            capabilities=["deployment_automation", "ci_cd", "docker_management",
                         "infrastructure_as_code", "monitoring_setup"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="database_specialist", name="Database Specialist",
            description="Manages database schema, migrations, and performance",
            capabilities=["schema_design", "query_optimization", "data_migration",
                         "database_performance", "backup_strategy"],
            compatible_skills=["skill_base"],
        ),
        SpecialistProfile(
            role="trainer", name="Trainer",
            description="Develops and delivers user training",
            capabilities=["training_delivery", "material_development", "user_onboarding",
                         "workshop_facilitation", "knowledge_transfer"],
            compatible_skills=["skill_base"],
        ),
    ]

    def __init__(self):
        self._profiles: Dict[str, SpecialistProfile] = {
            s.role: s for s in self.SPECIALISTS
        }
        self._active_assignments: Dict[str, AgentAssignment] = {}
        self._initialized = False

    def initialize(self):
        self._initialized = True

    def get_profile(self, role: str) -> Optional[SpecialistProfile]:
        return self._profiles.get(role)

    def find_specialist(self, capability: str) -> List[SpecialistProfile]:
        """Find specialists with a specific capability."""
        return [
            s for s in self.SPECIALISTS
            if capability in s.capabilities
        ]

    def create_coordination_plan(self, reasoning_result: ReasoningResult) -> CoordinationPlan:
        """Create a coordination plan from a reasoning result."""
        from datetime import datetime
        plan_id = f"coord_{datetime.now():%Y%m%d_%H%M%S}"
        assignments = []

        for phase_assignment in reasoning_result.specialist_assignments:
            phase_id = phase_assignment["phase_id"]
            phase_name = phase_assignment["phase_name"]

            for agent_info in phase_assignment.get("agents", []):
                role = agent_info["role"]
                profile = self._profiles.get(role)
                if not profile:
                    continue

                assignment = AgentAssignment(
                    assignment_id=f"task_{phase_id}_{role}",
                    agent_role=role,
                    task_description=f"{phase_name}: {profile.description}",
                    phase_id=phase_id,
                    skills_required=profile.compatible_skills,
                )
                assignments.append(assignment)
                self._active_assignments[assignment.assignment_id] = assignment

        return CoordinationPlan(plan_id=plan_id, assignments=assignments)

    def get_assignments_for_role(self, role: str) -> List[AgentAssignment]:
        return [a for a in self._active_assignments.values() if a.agent_role == role]

    def update_assignment(self, assignment_id: str, status: str,
                          output: Optional[dict] = None, error: Optional[str] = None):
        assignment = self._active_assignments.get(assignment_id)
        if assignment:
            assignment.status = status
            if output:
                assignment.output = output
            if error:
                assignment.error = error

    def get_plan_summary(self, plan: CoordinationPlan) -> dict:
        roles = set(a.agent_role for a in plan.assignments)
        return {
            "plan_id": plan.plan_id,
            "total_assignments": len(plan.assignments),
            "unique_roles": len(roles),
            "specialists": sorted(roles),
            "status_counts": {
                "pending": sum(1 for a in plan.assignments if a.status == "pending"),
                "in_progress": sum(1 for a in plan.assignments if a.status == "in_progress"),
                "completed": sum(1 for a in plan.assignments if a.status == "completed"),
                "failed": sum(1 for a in plan.assignments if a.status == "failed"),
            },
        }
