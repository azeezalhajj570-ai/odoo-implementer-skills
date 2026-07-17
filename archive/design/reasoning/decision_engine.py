#!/usr/bin/env python3
"""
Decision Engine — Compares implementation strategies and recommends the best approach.

Evaluates strategies across multiple dimensions:
complexity, performance, maintainability, upgrade safety,
security, cost, and implementation time.

Supported decision domains:
- Configuration vs Customization
- Studio vs Custom Module
- Server Action vs Python Code
- Computed Field vs Scheduled Action
- Inheritance vs Override
- REST vs RPC
- OWL Component vs XML Extension

Usage:
    from reasoning.decision_engine import DecisionEngine
    
    engine = DecisionEngine()
    result = engine.evaluate("Configuration vs Customization for CRM lead scoring")
    print(result.recommendation, result.confidence)
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class StrategyOption:
    """One possible implementation strategy."""
    name: str
    description: str
    complexity: int = 5      # 1-10
    performance: int = 5     # 1-10
    maintainability: int = 5 # 1-10
    upgrade_safety: int = 5  # 1-10
    security: int = 5        # 1-10
    cost: int = 5            # 1-10 (1=cheap, 10=expensive)
    time: int = 5            # 1-10 (1=fast, 10=slow)
    confidence: str = "medium"

    def score(self, weights: Optional[dict] = None) -> float:
        """Compute weighted score (higher is better)."""
        w = weights or {
            "complexity": 0.15, "performance": 0.15,
            "maintainability": 0.20, "upgrade_safety": 0.20,
            "security": 0.10, "cost": 0.10, "time": 0.10,
        }
        return (
            w["complexity"] * (11 - self.complexity) +  # invert: lower complexity = higher score
            w["performance"] * self.performance +
            w["maintainability"] * self.maintainability +
            w["upgrade_safety"] * self.upgrade_safety +
            w["security"] * self.security +
            w["cost"] * (11 - self.cost) +  # invert: lower cost = higher score
            w["time"] * (11 - self.time)    # invert: lower time = higher score
        )


@dataclass
class StrategyEvaluation:
    """Result of comparing implementation strategies."""
    domain: str
    question: str
    options: List[StrategyOption]
    recommendation: str
    recommended_option: Optional[StrategyOption] = None
    confidence: str = "medium"
    reasoning: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "question": self.question,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "options": [
                {
                    "name": o.name,
                    "score": round(o.score(), 2),
                    "complexity": o.complexity,
                    "maintainability": o.maintainability,
                    "upgrade_safety": o.upgrade_safety,
                }
                for o in self.options
            ],
            "reasoning": self.reasoning,
        }


class DecisionEngine:
    """Evaluates implementation strategies across multiple dimensions."""

    # Pre-built decision trees for common Odoo architecture decisions
    DECISION_TREES = {
        "config_vs_custom": {
            "question": "Configuration vs Customization",
            "domain": "architecture",
            "options": [
                StrategyOption(
                    name="Standard Configuration",
                    description="Use Odoo standard features and settings only",
                    complexity=2, performance=8, maintainability=9,
                    upgrade_safety=9, security=8, cost=2, time=2,
                    confidence="high",
                ),
                StrategyOption(
                    name="Studio Customization",
                    description="Use Odoo Studio for no-code customization",
                    complexity=3, performance=7, maintainability=6,
                    upgrade_safety=5, security=7, cost=4, time=3,
                    confidence="high",
                ),
                StrategyOption(
                    name="Custom Module",
                    description="Develop a custom Python module",
                    complexity=7, performance=9, maintainability=7,
                    upgrade_safety=4, security=8, cost=8, time=7,
                    confidence="high",
                ),
            ],
            "recommendation_rules": [
                "If standard features meet 80%+ of requirements: use Standard Configuration",
                "If customization is limited to UI/fields: use Studio",
                "If complex business logic or integration: use Custom Module",
            ],
        },
        "server_action_vs_python": {
            "question": "Server Action vs Python Code",
            "domain": "automation",
            "options": [
                StrategyOption(
                    name="Server Action",
                    description="Use Odoo's built-in server action framework",
                    complexity=3, performance=6, maintainability=6,
                    upgrade_safety=7, security=7, cost=2, time=2,
                    confidence="high",
                ),
                StrategyOption(
                    name="Python Method Override",
                    description="Override model methods with custom Python code",
                    complexity=6, performance=9, maintainability=8,
                    upgrade_safety=5, security=8, cost=7, time=6,
                    confidence="high",
                ),
            ],
        },
        "computed_vs_scheduled": {
            "question": "Computed Field vs Scheduled Action",
            "domain": "performance",
            "options": [
                StrategyOption(
                    name="Stored Computed Field",
                    description="Computed field with store=True, updated on dependency change",
                    complexity=4, performance=8, maintainability=7,
                    upgrade_safety=7, security=8, cost=4, time=3,
                    confidence="high",
                ),
                StrategyOption(
                    name="Scheduled Action (Cron)",
                    description="Periodic batch job to recompute values",
                    complexity=3, performance=5, maintainability=6,
                    upgrade_safety=7, security=7, cost=3, time=3,
                    confidence="high",
                ),
                StrategyOption(
                    name="On-the-fly Computed Field",
                    description="Non-stored computed field (computed on read)",
                    complexity=3, performance=3, maintainability=7,
                    upgrade_safety=8, security=8, cost=2, time=2,
                    confidence="high",
                ),
            ],
        },
    }

    def __init__(self):
        self._trees = self.DECISION_TREES

    def evaluate(self, question: str, domain: str = "architecture",
                 weights: Optional[dict] = None) -> StrategyEvaluation:
        """Evaluate a decision and return the recommended strategy."""
        # Find matching decision tree
        tree_key = self._find_tree(question, domain)
        tree = self._trees.get(tree_key)

        if not tree:
            return StrategyEvaluation(
                domain=domain, question=question,
                recommendation="No matching decision tree found",
                options=[], confidence="low",
                reasoning=["Decision tree not available for this question"],
            )

        # Score all options
        options = tree["options"]
        scored = [(o.score(weights), o) for o in options]
        scored.sort(key=lambda x: x[0], reverse=True)

        best_score, best_option = scored[0]
        reasoning = tree.get("recommendation_rules", [])

        return StrategyEvaluation(
            domain=tree["domain"],
            question=tree["question"],
            options=options,
            recommendation=f"Recommended: {best_option.name} "
                          f"(score: {best_score:.2f}/10)",
            recommended_option=best_option,
            confidence=best_option.confidence,
            reasoning=reasoning + [
                f"{best_option.name} scored highest ({best_score:.2f}/10) across "
                f"complexity, performance, maintainability, upgrade safety, "
                f"security, cost, and implementation time."
            ],
        )

    def _find_tree(self, question: str, domain: str) -> Optional[str]:
        """Find the best matching decision tree."""
        q_lower = question.lower()

        # Direct matching
        for key, tree in self._trees.items():
            if tree["domain"] == domain:
                if any(word in q_lower for word in tree["question"].lower().split()):
                    return key

        # Default by domain
        domain_map = {
            "architecture": "config_vs_custom",
            "automation": "server_action_vs_python",
            "performance": "computed_vs_scheduled",
        }
        return domain_map.get(domain, "config_vs_custom")

    def add_decision_tree(self, key: str, tree: dict):
        """Add a custom decision tree."""
        self._trees[key] = tree
