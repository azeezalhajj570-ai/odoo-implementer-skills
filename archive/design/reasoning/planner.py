#!/usr/bin/env python3
"""
Planner — Intelligent project planner that decomposes requirements into
execution phases, estimates effort, identifies risks, and generates milestones.

The Planner is project-aware: it considers the existing project context,
available skills, and previous experience when building plans.

Usage:
    from reasoning.planner import Planner
    
    planner = Planner()
    planner.initialize()
    plan = planner.create_plan(
        task_description="Implement CRM with lead scoring",
        domain="crm",
        task_type="implement",
        complexity=complexity,
        effort_hours=24,
        project_context={...}
    )
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProjectPhase:
    """A single phase in an implementation project."""
    id: str
    name: str
    description: str
    type: str  # analysis, design, implementation, testing, deployment, etc.
    order: int
    effort_hours: float
    dependencies: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "order": self.order,
            "effort_hours": self.effort_hours,
            "dependencies": self.dependencies,
            "deliverables": self.deliverables,
        }


@dataclass
class ExecutionPlan:
    """A complete project execution plan with phases, milestones, and assignments."""
    plan_id: str
    created_at: str
    summary: str
    phases: List[ProjectPhase]
    total_effort_hours: float = 0.0
    estimated_duration_days: int = 0
    milestones: List[dict] = field(default_factory=list)

    def __post_init__(self):
        self.total_effort_hours = sum(p.effort_hours for p in self.phases)

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "summary": self.summary,
            "phases": [p.to_dict() for p in self.phases],
            "total_effort_hours": self.total_effort_hours,
            "estimated_duration_days": self.estimated_duration_days,
            "milestones": self.milestones,
        }


class Planner:
    """Intelligent project planner for Odoo implementations."""

    # Phase templates for common task types
    PHASE_TEMPLATES = {
        "implement_crm": [
            ("requirements", "Requirements Analysis", "analysis", 4),
            ("architecture", "Solution Architecture", "design", 3),
            ("configuration", "CRM Configuration", "implementation", 6),
            ("pipeline", "Pipeline Design", "implementation", 3),
            ("scoring", "Lead Scoring Setup", "implementation", 4),
            ("security", "Security Configuration", "implementation", 2),
            ("testing", "Testing & Validation", "testing", 4),
            ("training", "User Training", "training", 2),
            ("deployment", "Go-Live", "deployment", 2),
        ],
        "implement_marketing": [
            ("requirements", "Campaign Requirements", "analysis", 3),
            ("config", "Email Marketing Setup", "configuration", 4),
            ("automation", "Marketing Automation", "implementation", 6),
            ("templates", "Email Templates", "implementation", 4),
            ("integration", "CRM Integration", "implementation", 3),
            ("testing", "Campaign Testing", "testing", 3),
            ("deployment", "Go-Live", "deployment", 2),
        ],
        "migrate": [
            ("audit", "Pre-Migration Audit", "analysis", 8),
            ("planning", "Migration Planning", "design", 4),
            ("testing", "Migration Dry Run", "testing", 8),
            ("execution", "Migration Execution", "migration", 16),
            ("validation", "Post-Migration Validation", "testing", 8),
            ("documentation", "Migration Documentation", "documentation", 4),
        ],
        "analyze": [
            ("discovery", "Project Discovery", "analysis", 3),
            ("modules", "Module Analysis", "analysis", 4),
            ("architecture", "Architecture Review", "design", 3),
            ("security", "Security Review", "security", 3),
            ("performance", "Performance Analysis", "analysis", 3),
            ("recommendations", "Recommendations", "design", 2),
        ],
    }

    def __init__(self):
        self._initialized = False

    def initialize(self):
        self._initialized = True

    def create_plan(self, task_description: str, domain: str,
                    task_type: str, complexity: str,
                    effort_hours: float,
                    project_context: Optional[dict] = None) -> ExecutionPlan:
        """Create a complete execution plan from task parameters."""
        from datetime import datetime

        plan_id = f"plan_{datetime.now():%Y%m%d_%H%M%S}"

        # Select phase template
        template_key = self._select_template(task_type, domain)
        template = self.PHASE_TEMPLATES.get(template_key, [])

        if not template:
            template = self.PHASE_TEMPLATES.get("analyze", [])

        # Build phases with effort distribution
        total_template_effort = sum(p[3] for p in template)
        phases = []
        prev_id = None

        for i, (pid, pname, ptype, base_effort) in enumerate(template):
            effort = round((base_effort / max(total_template_effort, 1)) * effort_hours, 1)
            deps = [prev_id] if prev_id else []

            phase = ProjectPhase(
                id=f"{pid}_{i}",
                name=pname,
                description=f"{pname} for {domain} implementation",
                type=ptype,
                order=i + 1,
                effort_hours=max(effort, 0.5),
                dependencies=deps,
                deliverables=self._default_deliverables(ptype),
                validation_criteria=self._default_validation(ptype),
            )
            phases.append(phase)
            prev_id = phase.id

        # Generate milestones
        milestones = self._generate_milestones(phases)

        # Build plan
        plan = ExecutionPlan(
            plan_id=plan_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            summary=f"{task_type.capitalize()} {domain}: "
                    f"{len(phases)} phases, ~{effort_hours}h total",
            phases=phases,
            total_effort_hours=round(effort_hours, 1),
            estimated_duration_days=self._estimate_duration(phases),
            milestones=milestones,
        )

        # Inject project context if available
        if project_context:
            plan.summary += f" — for project: {project_context.get('project_name', 'unknown')}"

        return plan

    def _select_template(self, task_type: str, domain: str) -> str:
        """Select the best phase template."""
        if "migrate" in task_type or "upgrade" in task_type:
            return "migrate"
        if "analyze" in task_type or "review" in task_type or "audit" in task_type:
            return "analyze"
        if domain == "crm":
            return "implement_crm"
        if domain == "marketing":
            return "implement_marketing"
        return task_type

    def _default_deliverables(self, phase_type: str) -> List[str]:
        """Default deliverables per phase type."""
        return {
            "analysis": ["Requirements document", "Gap analysis", "Impact assessment"],
            "design": ["Solution architecture document", "Technical specification"],
            "implementation": ["Configured modules", "Custom module (if needed)"],
            "configuration": ["Configured settings", "Module configuration"],
            "customization": ["Custom Python code", "XML views", "Security rules"],
            "testing": ["Test plan", "Test results", "Bug report"],
            "migration": ["Migration script", "Migrated database"],
            "security": ["Security audit report", "Access control matrix"],
            "deployment": ["Deployment package", "Go-live checklist"],
            "training": ["Training materials", "User documentation"],
            "documentation": ["Technical documentation", "User guide"],
        }.get(phase_type, ["Completed deliverables"])

    def _default_validation(self, phase_type: str) -> List[str]:
        """Default validation criteria per phase type."""
        return {
            "analysis": ["Requirements approved by stakeholder"],
            "design": ["Architecture reviewed and approved"],
            "implementation": ["All tests pass", "Code review completed"],
            "configuration": ["Configuration verified in staging"],
            "testing": ["All test cases pass", "No critical bugs"],
            "migration": ["Data integrity verified", "Application works"],
            "security": ["No critical vulnerabilities"],
            "deployment": ["Production verified working"],
        }.get(phase_type, ["Validation complete"])

    def _generate_milestones(self, phases: List[ProjectPhase]) -> List[dict]:
        """Generate project milestones from phases."""
        milestones = []
        for phase in phases:
            if phase.type in ("deployment", "testing"):
                milestones.append({
                    "phase_id": phase.id,
                    "name": f"{phase.name} Complete",
                    "description": f"Milestone: {phase.name}",
                    "order": phase.order,
                    "critical": phase.type == "deployment",
                })
        return milestones

    def _estimate_duration(self, phases: List[ProjectPhase]) -> int:
        """Estimate project duration in calendar days (assumes 6h productive/day)."""
        total_hours = sum(p.effort_hours for p in phases)
        parallelizable = self._estimate_parallelism(phases)
        return max(1, round((total_hours / 6) * (1 - parallelizable * 0.3)))

    def _estimate_parallelism(self, phases: List[ProjectPhase]) -> float:
        """Estimate how much work can be parallelized (0.0 to 1.0)."""
        independent = sum(1 for p in phases if not p.dependencies)
        return independent / max(len(phases), 1)

    def get_phase(self, plan: ExecutionPlan, phase_id: str) -> Optional[ProjectPhase]:
        for p in plan.phases:
            if p.id == phase_id:
                return p
        return None
