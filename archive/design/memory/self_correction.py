#!/usr/bin/env python3
"""
Self-Correction Engine — After every execution, compares expected and actual results,
identifies failures, diagnoses root causes, selects corrective actions, retries safely,
and records lessons learned.

Usage:
    from memory.self_correction import SelfCorrectionEngine
    
    corrector = SelfCorrectionEngine(memory)
    result = corrector.correct(
        action="analyze_pipeline",
        expected={"stages_count": 3},
        actual={"stages_count": 0},
        error="No data found"
    )
    print(result.corrective_action)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable

from memory.memory import ExperienceMemory, Lesson

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@dataclass
class CorrectionResult:
    """Result of a self-correction cycle."""
    original_action: str
    success: bool
    corrective_action: str = ""
    retry_count: int = 0
    root_cause: str = ""
    lesson_recorded: bool = False
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "action": self.original_action,
            "success": self.success,
            "corrective_action": self.corrective_action,
            "retry_count": self.retry_count,
            "root_cause": self.root_cause,
            "lesson_recorded": self.lesson_recorded,
        }


class SelfCorrectionEngine:
    """Detects failures, diagnoses root causes, and retries with corrections."""

    # Pre-built failure patterns with corrective actions
    FAILURE_PATTERNS = {
        "no_data_found": {
            "patterns": ["no data", "empty", "not found", "no results", "0 results"],
            "root_cause": "Input parameters or filters too restrictive",
            "corrective_action": "broaden_parameters",
            "advice": "Relax filter criteria or verify data exists",
        },
        "invalid_parameters": {
            "patterns": ["invalid", "bad request", "validation error", "type error",
                        "valueerror", "keyerror"],
            "root_cause": "Invalid or missing parameters in tool call",
            "corrective_action": "fix_parameters",
            "advice": "Check required parameters and their types",
        },
        "permission_denied": {
            "patterns": ["permission", "access denied", "forbidden", "unauthorized",
                        "not allowed"],
            "root_cause": "Insufficient permissions for the operation",
            "corrective_action": "escalate_permissions",
            "advice": "Verify access rights or use sudo context",
        },
        "timeout": {
            "patterns": ["timeout", "timed out", "too slow", "no response"],
            "root_cause": "Operation exceeded time limit",
            "corrective_action": "increase_timeout_or_batch",
            "advice": "Increase timeout or process in smaller batches",
        },
        "not_implemented": {
            "patterns": ["not implemented", "not supported", "unavailable",
                        "not found", "does not exist", "not available"],
            "root_cause": "Requested feature or tool is not available",
            "corrective_action": "use_alternative",
            "advice": "Use a different tool or approach",
        },
    }

    def __init__(self, memory: ExperienceMemory, max_retries: int = MAX_RETRIES):
        self.memory = memory
        self.max_retries = max_retries
        self._retry_counts: Dict[str, int] = {}

    def correct(self, action: str, expected: Any, actual: Any,
                error: Optional[str] = None,
                retry_fn: Optional[Callable] = None) -> CorrectionResult:
        """Analyze a failure and apply corrections."""
        error_str = str(error or "").lower()
        actual_str = str(actual).lower()

        # Find matching failure pattern
        pattern = self._match_pattern(error_str, actual_str)

        if not pattern:
            # Unknown error — record lesson and report
            self._record_lesson(action, error_str)
            return CorrectionResult(
                original_action=action,
                success=False,
                root_cause="Unknown failure",
                corrective_action="review_manually",
                details=f"No matching correction pattern found: {error}",
            )

        root_cause = pattern["root_cause"]
        corrective_action = pattern["corrective_action"]

        # Check retry limit
        retry_count = self._retry_counts.get(action, 0)
        if retry_count >= self.max_retries:
            self._record_lesson(action, f"Exceeded max retries ({self.max_retries}): {error}")
            return CorrectionResult(
                original_action=action,
                success=False,
                retry_count=retry_count,
                root_cause=root_cause,
                corrective_action="give_up",
                details=f"Max retries ({self.max_retries}) exceeded for: {action}",
            )

        # Apply corrective action
        retry_count += 1
        self._retry_counts[action] = retry_count

        logger.info(f"Correction for {action} (attempt {retry_count}): "
                     f"{corrective_action} — {root_cause}")

        # If retry function provided, attempt re-execution
        if retry_fn:
            try:
                new_actual = retry_fn(corrective_action=corrective_action)
                success = new_actual == expected if not callable(expected) else True
            except Exception as e:
                logger.warning(f"Retry {retry_count} failed: {e}")
                return self.correct(action, expected, None, str(e), retry_fn)

            if success:
                self._retry_counts.pop(action, None)
                self._record_lesson(action, f"Corrected via {corrective_action}: {error}")
                return CorrectionResult(
                    original_action=action,
                    success=True,
                    corrective_action=corrective_action,
                    retry_count=retry_count,
                    root_cause=root_cause,
                    lesson_recorded=True,
                )

        return CorrectionResult(
            original_action=action,
            success=False,
            retry_count=retry_count,
            root_cause=root_cause,
            corrective_action=corrective_action,
            details=pattern.get("advice", ""),
        )

    def _match_pattern(self, error_str: str, actual_str: str) -> Optional[dict]:
        """Match error/actual against known failure patterns."""
        for pattern_id, pattern_info in self.FAILURE_PATTERNS.items():
            for p in pattern_info["patterns"]:
                if p in error_str or p in actual_str:
                    return pattern_info
        return None

    def _record_lesson(self, action: str, error: str):
        """Record a lesson learned from this failure."""
        lesson = Lesson(
            category="execution_error",
            title=f"Correction applied for: {action}",
            description=f"Error: {error}. Correction pattern matched.",
            severity="info",
            tags=["self_correction", action],
        )
        self.memory.record_lesson(lesson)

    def reset_retry_count(self, action: str):
        """Reset retry count for an action."""
        self._retry_counts.pop(action, None)
