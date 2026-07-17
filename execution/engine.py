#!/usr/bin/env python3
"""
Skill Execution Engine — The runtime that loads skills, resolves dependencies,
discovers tools, plans execution, executes tools, collects outputs, and
builds implementation reports.

Supports multiple cooperating agents via sessions.

Usage:
    from execution.engine import SkillExecutionEngine
    
    engine = SkillExecutionEngine()
    engine.initialize()
    
    plan = engine.create_plan("skill_crm", "analyze_pipeline", {"lead_ids": [1,2]})
    result = engine.execute_plan(plan)
    print(result.success, result.outputs)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from tools.registry import ToolRegistry, ToolResult, get_registry
from agents.opencode.skill_registry import SkillRegistry
from agents.opencode.dependency_manager import DependencyManager

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ExecutionStep:
    """A single step in an execution plan."""
    tool_name: str
    params: dict = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "params": self.params,
            "depends_on": self.depends_on,
            "description": self.description,
        }


@dataclass
class ExecutionPlan:
    """A planned sequence of tool executions."""
    plan_id: str
    skill_ids: List[str]
    steps: List[ExecutionStep]
    context: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "skill_ids": self.skill_ids,
            "steps": [s.to_dict() for s in self.steps],
            "step_count": len(self.steps),
            "created_at": self.created_at,
        }


@dataclass
class ExecutionResult:
    """Result of executing an ExecutionPlan."""
    plan_id: str
    success: bool
    outputs: Dict[str, ToolResult] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "success": self.success,
            "outputs": {k: v.to_dict() for k, v in self.outputs.items()},
            "errors": self.errors,
            "execution_time": self.execution_time,
        }


class SkillExecutionEngine:
    """The core execution runtime for the Odoo AI Implementer."""

    def __init__(self):
        self.tool_registry: Optional[ToolRegistry] = None
        self.skill_registry = SkillRegistry()
        self.dep_manager: Optional[DependencyManager] = None
        self._initialized = False
        self._plans: Dict[str, ExecutionPlan] = {}

    def initialize(self) -> dict:
        """Initialize the execution engine."""
        logger.info("Initializing Skill Execution Engine...")

        # Initialize tool registry
        self.tool_registry = get_registry()

        # Initialize skill registry
        self.skill_registry.index_all()

        # Initialize dependency manager
        self.dep_manager = DependencyManager(self.skill_registry)

        self._initialized = True

        return {
            "status": "initialized",
            "tools": self.tool_registry.get_stats(),
            "skills": len(self.skill_registry._registry),
        }

    def create_plan(self, skill_ids: List[str], 
                    tool_sequence: List[Dict[str, Any]]) -> ExecutionPlan:
        """Create an execution plan from a sequence of tool calls."""
        if not self._initialized:
            self.initialize()

        from datetime import datetime
        plan_id = f"plan_{datetime.now():%Y%m%d_%H%M%S}"
        steps = []

        for i, step_def in enumerate(tool_sequence):
            step = ExecutionStep(
                tool_name=step_def.get("tool", ""),
                params=step_def.get("params", {}),
                depends_on=step_def.get("depends_on", []),
                description=step_def.get("description", f"Step {i+1}"),
            )
            steps.append(step)

        plan = ExecutionPlan(
            plan_id=plan_id,
            skill_ids=skill_ids,
            steps=steps,
        )
        self._plans[plan_id] = plan
        return plan

    def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        """Execute an execution plan."""
        import time
        start_time = time.time()

        outputs = {}
        errors = []
        completed = set()

        for step in plan.steps:
            # Check dependencies
            deps_met = all(d in completed for d in step.depends_on)
            if not deps_met:
                errors.append(f"Step '{step.tool_name}': unmet dependencies {step.depends_on}")
                continue

            # Execute
            logger.info(f"Executing: {step.tool_name} ({step.description})")
            result = self.tool_registry.execute(step.tool_name, step.params)

            step_key = f"{step.tool_name}_{len(outputs)}"
            outputs[step_key] = result

            if result.success:
                completed.add(step.tool_name)
            else:
                errors.append(f"Step '{step.tool_name}' failed: {result.error}")

        execution_time = time.time() - start_time

        return ExecutionResult(
            plan_id=plan.plan_id,
            success=len(errors) == 0,
            outputs=outputs,
            errors=errors,
            execution_time=execution_time,
        )

    def find_tools_for_task(self, task_description: str, 
                            skill_ids: Optional[List[str]] = None) -> List[dict]:
        """Find tools matching a task description."""
        task_lower = task_description.lower()
        matching = []

        tools = self.tool_registry.list_tools()
        for tool in tools:
            score = 0
            if skill_ids and tool.get("skill_id") in skill_ids:
                score += 2
            desc = tool.get("description", "").lower()
            name = tool.get("name", "").lower()
            if any(word in desc for word in task_lower.split()):
                score += 1
            if any(word in name for word in task_lower.split()):
                score += 2
            if score > 0:
                matching.append((score, tool))

        matching.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in matching]

    def get_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        return self._plans.get(plan_id)

    def status(self) -> dict:
        return {
            "initialized": self._initialized,
            "tools_available": self.tool_registry.get_stats() if self.tool_registry else {},
            "active_plans": len(self._plans),
        }
