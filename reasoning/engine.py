#!/usr/bin/env python3
"""
Reasoning Engine — The strategic brain above the Execution Engine.

Responsibilities:
- Understand user intent and infer missing requirements
- Decompose large projects into manageable phases
- Identify risks and recommend alternatives
- Estimate effort and complexity
- Prioritize tasks and build implementation strategies
- Produce execution plans rather than immediately executing tools

Usage:
    from reasoning.engine import ReasoningEngine
    
    engine = ReasoningEngine()
    result = engine.reason("Implement CRM for this company", context={...})
    plan = result.execution_plan
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from reasoning.planner import Planner, ExecutionPlan, ProjectPhase
from reasoning.decision_engine import DecisionEngine, StrategyOption

logger = logging.getLogger(__name__)


class ComplexityLevel(str, Enum):
    TRIVIAL = "trivial"       # < 1 hour
    SIMPLE = "simple"         # 1-4 hours
    MODERATE = "moderate"     # 4-16 hours
    COMPLEX = "complex"       # 16-40 hours
    VERY_COMPLEX = "very_complex"  # 40-80 hours
    MAJOR = "major"           # 80+ hours


@dataclass
class Risk:
    description: str
    severity: str = "medium"  # low, medium, high, critical
    category: str = ""        # technical, functional, timeline, resource
    mitigation: str = ""

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "severity": self.severity,
            "category": self.category,
            "mitigation": self.mitigation,
        }


@dataclass
class ReasoningResult:
    """Result of a reasoning pass — the plan + analysis."""
    task_description: str
    execution_plan: ExecutionPlan
    complexity: ComplexityLevel
    effort_hours: float
    risks: List[Risk] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    recommended_skills: List[str] = field(default_factory=list)
    recommended_tools: List[str] = field(default_factory=list)
    specialist_assignments: List[dict] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "task": self.task_description,
            "plan": self.execution_plan.to_dict(),
            "complexity": self.complexity.value,
            "effort_hours": self.effort_hours,
            "risks": [r.to_dict() for r in self.risks],
            "alternatives": self.alternatives,
            "recommended_skills": self.recommended_skills,
            "recommended_tools": self.recommended_tools,
            "specialist_assignments": self.specialist_assignments,
            "assumptions": self.assumptions,
            "open_questions": self.open_questions,
        }


class ReasoningEngine:
    """Strategic reasoning layer — plans, evaluates, and delegates."""

    TASK_PATTERNS = {
        "implement": {
            "keywords": ["implement", "set up", "configure", "install", "build", "create"],
            "complexity_base": 8,
        },
        "migrate": {
            "keywords": ["migrate", "upgrade", "update", "port", "move"],
            "complexity_base": 16,
        },
        "analyze": {
            "keywords": ["analyze", "review", "audit", "inspect", "assess", "evaluate"],
            "complexity_base": 4,
        },
        "optimize": {
            "keywords": ["optimize", "improve", "enhance", "speed up", "fix"],
            "complexity_base": 6,
        },
        "customize": {
            "keywords": ["customize", "modify", "extend", "add", "change"],
            "complexity_base": 10,
        },
    }

    DOMAIN_SKILL_MAP = {
        "crm": "skill_crm",
        "marketing": "skill_marketing",
        "sales": "skill_crm",
        "email": "skill_mail",
        "mail": "skill_mail",
    }

    def __init__(self):
        self.planner = Planner()
        self.decision_engine = DecisionEngine()
        self._initialized = False

    def initialize(self) -> dict:
        """Initialize the reasoning engine and its sub-engines."""
        self.planner.initialize()
        self._initialized = True
        return {"status": "initialized", "planner": True, "decision_engine": True}

    def reason(self, task_description: str,
               project_context: Optional[dict] = None,
               constraints: Optional[dict] = None) -> ReasoningResult:
        """
        Analyze a task description and produce a complete reasoning result.

        1. Classify the task type and domain
        2. Infer complexity and effort
        3. Identify risks
        4. Recommend skills and tools
        5. Decompose into phases
        6. Assign specialist agents
        7. Produce execution plan
        """
        if not self._initialized:
            self.initialize()

        # 1. Classify task
        task_type = self._classify_task(task_description)
        domain = self._infer_domain(task_description)

        # 2. Estimate complexity/effort
        complexity, effort = self._estimate_effort(
            task_description, task_type, constraints
        )

        # 3. Identify risks
        risks = self._identify_risks(task_description, task_type, complexity)

        # 4. Recommend skills
        recommended_skills = self._recommend_skills(domain, task_type)
        recommended_tools = self._recommend_tools(task_type, domain)

        # 5. Generate alternatives
        alternatives = self._generate_alternatives(task_type, domain)

        # 6. Identify assumptions and open questions
        assumptions = self._generate_assumptions(task_description)
        open_questions = self._generate_open_questions(task_description, complexity)

        # 7. Build execution plan via Planner
        execution_plan = self.planner.create_plan(
            task_description=task_description,
            domain=domain,
            task_type=task_type,
            complexity=complexity,
            effort_hours=effort,
            project_context=project_context,
        )

        # 8. Assign specialists
        specialist_assignments = self._assign_specialists(
            execution_plan, domain, task_type
        )

        logger.info(
            f"Reasoning complete: {task_type}/{domain}, "
            f"{complexity.value}, ~{effort}h, "
            f"{len(execution_plan.phases)} phases"
        )

        return ReasoningResult(
            task_description=task_description,
            execution_plan=execution_plan,
            complexity=complexity,
            effort_hours=effort,
            risks=risks,
            alternatives=alternatives,
            recommended_skills=list(recommended_skills),
            recommended_tools=list(recommended_tools),
            specialist_assignments=specialist_assignments,
            assumptions=assumptions,
            open_questions=open_questions,
        )

    def _classify_task(self, description: str) -> str:
        """Classify the task type from keywords."""
        desc_lower = description.lower()
        for task_type, pattern in self.TASK_PATTERNS.items():
            if any(kw in desc_lower for kw in pattern["keywords"]):
                return task_type
        return "implement"  # default

    def _infer_domain(self, description: str) -> str:
        """Infer the Odoo domain from the description."""
        desc_lower = description.lower()
        domain_keywords = [
            ("crm", ["crm", "lead", "opportunity", "pipeline", "sales team"]),
            ("marketing", ["marketing", "campaign", "email", "sms", "newsletter"]),
            ("accounting", ["accounting", "invoice", "tax", "payment", "journal"]),
            ("inventory", ["inventory", "warehouse", "stock", "route", "reorder"]),
            ("manufacturing", ["manufacturing", "production", "bom", "work order"]),
            ("hr", ["hr", "employee", "payroll", "attendance", "recruitment"]),
            ("website", ["website", "ecommerce", "shop", "blog", "seo"]),
            ("purchase", ["purchase", "vendor", "rfq", "procurement"]),
        ]
        for domain, keywords in domain_keywords:
            if any(kw in desc_lower for kw in keywords):
                return domain
        return "base"

    def _estimate_effort(self, description: str, task_type: str,
                          constraints: Optional[dict]) -> tuple:
        """Estimate complexity and effort hours."""
        base = self.TASK_PATTERNS.get(task_type, {}).get("complexity_base", 8)
        desc_lower = description.lower()

        modifiers = {
            "complex": 2.0, "multi": 1.5, "large": 2.0,
            "full": 1.5, "complete": 1.5, "custom": 1.5,
            "simple": 0.5, "basic": 0.5, "quick": 0.3,
            "migration": 2.0, "upgrade": 2.0,
        }

        modifier = 1.0
        for word, mod in modifiers.items():
            if word in desc_lower:
                modifier = max(modifier, mod)

        if constraints and constraints.get("scope"):
            if "full" in constraints["scope"].lower():
                modifier *= 1.5

        effort = base * modifier

        if effort <= 1:
            complexity = ComplexityLevel.TRIVIAL
        elif effort <= 4:
            complexity = ComplexityLevel.SIMPLE
        elif effort <= 16:
            complexity = ComplexityLevel.MODERATE
        elif effort <= 40:
            complexity = ComplexityLevel.COMPLEX
        elif effort <= 80:
            complexity = ComplexityLevel.VERY_COMPLEX
        else:
            complexity = ComplexityLevel.MAJOR

        return complexity, round(effort, 1)

    def _identify_risks(self, description: str, task_type: str,
                         complexity: ComplexityLevel) -> List[Risk]:
        """Identify potential risks."""
        risks = []

        if complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX, ComplexityLevel.MAJOR):
            risks.append(Risk(
                "Project scope requires careful phasing and milestone tracking",
                severity="high", category="project_management",
                mitigation="Break into smaller phases with clear deliverables"
            ))

        if "migration" in description.lower() or "upgrade" in description.lower():
            risks.append(Risk(
                "Version migration may require third-party module updates",
                severity="high", category="technical",
                mitigation="Audit all third-party module compatibility first"
            ))
            risks.append(Risk(
                "Database schema changes may require data migration scripts",
                severity="medium", category="technical",
                mitigation="Generate migration scripts and test on staging"
            ))

        if "custom" in description.lower():
            risks.append(Risk(
                "Customizations increase upgrade complexity for future versions",
                severity="medium", category="maintainability",
                mitigation="Prefer configuration over customization where possible"
            ))

        return risks

    def _recommend_skills(self, domain: str, task_type: str) -> Set[str]:
        """Recommend AI skills for the task."""
        skills = {"skill_base"}

        domain_skill = self.DOMAIN_SKILL_MAP.get(domain)
        if domain_skill:
            skills.add(domain_skill)

        if task_type in ("implement", "customize"):
            skills.add("skill_mail")

        if task_type == "migrate":
            pass  # Migration skill would be added here

        return skills

    def _recommend_tools(self, task_type: str, domain: str) -> Set[str]:
        """Recommend MCP tools for the task."""
        tools = {"python", "filesystem", "git"}
        if task_type in ("implement", "customize"):
            tools.update({"terminal", "ripgrep"})
        if task_type == "migrate":
            tools.add("postgres")
        return tools

    def _generate_alternatives(self, task_type: str, domain: str) -> List[str]:
        """Generate alternative implementation strategies."""
        alts = []

        if task_type == "implement":
            alts.extend([
                "Use Odoo Studio for rapid configuration",
                "Develop custom module for maximum flexibility",
                "Use server actions for simple automations",
                "Configure standard features first, then customize gaps",
            ])

        if task_type == "migrate":
            alts.extend([
                "In-place upgrade with Odoo's upgrade script",
                "Fresh install + data migration for clean start",
                "Phased migration module by module",
            ])

        return alts

    def _generate_assumptions(self, description: str) -> List[str]:
        """Generate explicit assumptions."""
        assumptions = [
            "Odoo Enterprise 19.0 is installed and accessible",
            "Database access is available for schema inspection",
            "Source code is accessible for analysis",
            "Standard Odoo modules are installed where needed",
        ]
        if "migrate" in description.lower() or "upgrade" in description.lower():
            assumptions.append("Source database backup is available")
        return assumptions

    def _generate_open_questions(self, description: str,
                                  complexity: ComplexityLevel) -> List[str]:
        """Generate questions to clarify requirements."""
        questions = []
        if complexity in (ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX, ComplexityLevel.MAJOR):
            questions.append("What is the target timeline for completion?")
            questions.append("What is the priority: speed, quality, or cost?")
        questions.append("Are there specific compliance or regulatory requirements?")
        return questions

    def _assign_specialists(self, plan: ExecutionPlan, domain: str,
                            task_type: str) -> List[dict]:
        """Assign specialist agents to plan phases."""
        assignments = []

        for phase in plan.phases:
            agents = []

            if phase.type in ("analysis", "requirements"):
                agents.append({"role": "functional_consultant", "priority": 1})
                agents.append({"role": "business_analyst", "priority": 2})

            if phase.type in ("design", "architecture"):
                agents.append({"role": "solution_architect", "priority": 1})
                agents.append({"role": "technical_architect", "priority": 2})

            if phase.type in ("implementation", "configuration", "customization"):
                agents.append({"role": "backend_developer", "priority": 1})
                if domain == "website":
                    agents.append({"role": "frontend_developer", "priority": 2})

            if phase.type == "testing":
                agents.append({"role": "qa_engineer", "priority": 1})

            if phase.type == "security":
                agents.append({"role": "security_specialist", "priority": 1})

            if phase.type in ("migration", "upgrade"):
                agents.append({"role": "migration_specialist", "priority": 1})
                agents.append({"role": "database_specialist", "priority": 2})

            if phase.type == "deployment":
                agents.append({"role": "devops_engineer", "priority": 1})

            if phase.type == "documentation":
                agents.append({"role": "documentation_engineer", "priority": 1})

            if phase.type == "training":
                agents.append({"role": "trainer", "priority": 1})

            assignments.append({
                "phase_id": phase.id,
                "phase_name": phase.name,
                "agents": agents,
            })

        return assignments
