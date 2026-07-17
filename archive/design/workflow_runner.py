#!/usr/bin/env python3
"""
Workflow Runner — Executes implementation playbooks as structured workflows.

Workflows are defined as JSON files in skills/<skill>/workflows/*.json.
Each workflow is a sequence of steps that can include tool execution,
branching logic, validation gates, and rollback procedures.

Usage:
    from execution.workflow_runner import WorkflowRunner
    
    runner = WorkflowRunner(engine)
    result = runner.run_workflow("skill_crm", "crm_implementation")
    print(result.summary())
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from execution.engine import SkillExecutionEngine, ExecutionStep, ExecutionResult

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class WorkflowStep:
    """A single step in an implementation workflow."""
    id: str
    name: str
    description: str
    tool: str = ""
    params: dict = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    validation: Optional[dict] = None
    on_failure: str = "stop"  # stop, skip, continue
    rollback_tool: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "WorkflowStep":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            description=d.get("description", ""),
            tool=d.get("tool", ""),
            params=d.get("params", {}),
            depends_on=d.get("depends_on", []),
            validation=d.get("validation"),
            on_failure=d.get("on_failure", "stop"),
            rollback_tool=d.get("rollback_tool", ""),
        )


@dataclass
class WorkflowResult:
    """Result of running a workflow."""
    workflow_id: str
    success: bool
    step_results: Dict[str, Any] = field(default_factory=dict)
    failed_steps: List[str] = field(default_factory=list)
    rolled_back: bool = False
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "success": self.success,
            "steps_completed": len(self.step_results),
            "steps_failed": len(self.failed_steps),
            "rolled_back": self.rolled_back,
            "summary": self.summary,
        }


class WorkflowRunner:
    """Executes implementation workflows (playbooks)."""

    def __init__(self, engine: SkillExecutionEngine):
        self.engine = engine
        self._workflows: Dict[str, dict] = {}

    def discover_workflows(self, skills_base: Optional[Path] = None) -> List[str]:
        """Discover all workflow definitions across skills."""
        base = skills_base or ROOT / "skills"
        discovered = []

        for skill_dir in sorted(base.iterdir()):
            if not skill_dir.is_dir():
                continue
            wf_dir = skill_dir / "workflows"
            if not wf_dir.exists():
                continue

            try:
                with open(skill_dir / "skill.json") as f:
                    sd = json.load(f)
                skill_id = sd.get("skill_id", skill_dir.name)
            except (json.JSONDecodeError, IOError):
                skill_id = skill_dir.name

            for wf_file in sorted(wf_dir.glob("*.json")):
                try:
                    with open(wf_file) as f:
                        workflow_data = json.load(f)
                    wf_id = workflow_data.get("id", wf_file.stem)
                    workflow_data["_skill_id"] = skill_id
                    self._workflows[wf_id] = workflow_data
                    discovered.append(wf_id)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load workflow {wf_file}: {e}")

        logger.info(f"Discovered {len(discovered)} workflows")
        return discovered

    def get_workflow(self, workflow_id: str) -> Optional[dict]:
        return self._workflows.get(workflow_id)

    def get_workflows_for_skill(self, skill_id: str) -> List[dict]:
        return [wf for wf in self._workflows.values()
                if wf.get("_skill_id") == skill_id]

    def run_workflow(self, workflow_id: str,
                     context: Optional[dict] = None) -> WorkflowResult:
        """Execute a workflow by ID."""
        wf = self.get_workflow(workflow_id)
        if not wf:
            return WorkflowResult(
                workflow_id=workflow_id,
                success=False,
                summary=f"Workflow not found: {workflow_id}",
            )

        steps = [WorkflowStep.from_dict(s) for s in wf.get("steps", [])]
        if not steps:
            return WorkflowResult(
                workflow_id=workflow_id,
                success=False,
                summary="Workflow has no steps",
            )

        logger.info(f"Running workflow: {wf.get('name', workflow_id)} "
                     f"({len(steps)} steps)")

        step_results = {}
        failed_steps = []
        rolled_back = False

        for step in steps:
            if not step.tool:
                step_results[step.id] = {"status": "skipped", "reason": "no tool"}
                continue

            logger.info(f"  Step: {step.name} ({step.tool})")

            # Build params with context
            params = dict(step.params)
            if context:
                # Merge context into params where not already set
                for k, v in context.items():
                    params.setdefault(k, v)

            # Execute
            result = self.engine.tool_registry.execute(step.tool, params)
            step_results[step.id] = {
                "tool": step.tool,
                "success": result.success,
                "data": result.data,
                "error": result.error,
            }

            if result.success:
                # Run validation if defined
                if step.validation:
                    valid = self._run_validation(step.validation, result.data)
                    if not valid:
                        step_results[step.id]["validation_failed"] = True
                        failed_steps.append(step.id)
                        step_results[step.id]["status"] = "validation_failed"
                        if step.on_failure == "stop":
                            break
                        continue

                step_results[step.id]["status"] = "completed"
            else:
                failed_steps.append(step.id)
                step_results[step.id]["status"] = "failed"

                # Rollback if configured
                if step.rollback_tool:
                    rollback_result = self.engine.tool_registry.execute(
                        step.rollback_tool, params
                    )
                    step_results[f"{step.id}_rollback"] = {
                        "tool": step.rollback_tool,
                        "success": rollback_result.success,
                    }
                    rolled_back = True

                if step.on_failure == "stop":
                    break

        success = len(failed_steps) == 0
        wf_name = wf.get("name", workflow_id)

        return WorkflowResult(
            workflow_id=workflow_id,
            success=success,
            step_results=step_results,
            failed_steps=failed_steps,
            rolled_back=rolled_back,
            summary=f"Workflow '{wf_name}': {len(step_results)} steps, "
                    f"{len(failed_steps)} failed, rolled_back={rolled_back}",
        )

    def _run_validation(self, validation: dict, data: Any) -> bool:
        """Run a validation check against step output."""
        vtype = validation.get("type", "")
        if vtype == "not_empty" and data is None:
            return False
        if vtype == "has_fields" and isinstance(data, dict):
            required = validation.get("fields", [])
            return all(f in data for f in required)
        if vtype == "length_gt" and isinstance(data, (list, str)):
            return len(data) > validation.get("min", 0)
        return True
