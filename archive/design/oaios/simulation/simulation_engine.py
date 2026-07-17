#!/usr/bin/env python3
"""
Simulation Engine — Before any implementation, simulates proposed changes,
predicts consequences, identifies impacted modules/workflows/security,
estimates downtime/effort/rollback complexity, and generates an
Impact Analysis Report.

Usage:
    from oaios.simulation.simulation_engine import SimulationEngine
    
    engine = SimulationEngine(twin)
    result = engine.simulate_change(
        change_type="module_install",
        target="sale_management",
        context={"version": "19.0"}
    )
    print(result.impact_report)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ImpactItem:
    """A single impact item in the simulation report."""
    category: str  # module, workflow, security, performance, migration
    description: str
    severity: str = "medium"  # low, medium, high, critical
    probability: float = 0.8  # 0.0 to 1.0
    affected_entities: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "probability": self.probability,
        }


@dataclass
class SimulationResult:
    """Result of a simulation."""
    simulation_id: str
    change_type: str
    change_target: str
    success: bool
    impact_items: List[ImpactItem] = field(default_factory=list)
    estimated_downtime_minutes: int = 0
    estimated_effort_hours: float = 0.0
    rollback_complexity: str = "low"
    recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def high_impact_count(self) -> int:
        return sum(1 for i in self.impact_items if i.severity in ("high", "critical"))

    def to_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "change": f"{self.change_type}: {self.change_target}",
            "success": self.success,
            "total_impacts": len(self.impact_items),
            "high_impacts": self.high_impact_count,
            "downtime_minutes": self.estimated_downtime_minutes,
            "effort_hours": self.estimated_effort_hours,
            "rollback_complexity": self.rollback_complexity,
        }

    def impact_report(self) -> str:
        lines = [
            f"# Impact Analysis: {self.change_type} — {self.change_target}",
            f"**Simulation ID:** {self.simulation_id}",
            f"**Estimated Downtime:** {self.estimated_downtime_minutes} min",
            f"**Estimated Effort:** {self.estimated_effort_hours}h",
            f"**Rollback Complexity:** {self.rollback_complexity}",
            f"**Total Impacts:** {len(self.impact_items)} ({self.high_impact_count} high)",
            "",
            "## Impact Items",
        ]
        for item in self.impact_items:
            lines.extend([
                f"### [{item.severity.upper()}] {item.description}",
                f"- Category: {item.category}",
                f"- Probability: {item.probability:.0%}",
            ])
        lines.extend(["", "## Recommendations"])
        for r in self.recommendations:
            lines.append(f"- {r}")
        return "\n".join(lines)


class SimulationEngine:
    """Simulates proposed changes before execution."""

    IMPACT_TEMPLATES = {
        "module_install": {
            "impacts": [
                ("module", "New module installation may require database migration", "medium", 0.9),
                ("module", "May introduce new dependencies", "low", 0.7),
                ("security", "New security groups and access rights created", "medium", 0.6),
                ("workflow", "New automated actions may be installed", "low", 0.5),
            ],
            "downtime_minutes": 5,
            "effort_hours": 2,
            "rollback": "low",
        },
        "module_upgrade": {
            "impacts": [
                ("migration", "Database schema migration required", "high", 0.9),
                ("migration", "Potential breaking changes in API", "high", 0.6),
                ("performance", "Large data migration may impact performance", "medium", 0.5),
                ("module", "Third-party module compatibility issues possible", "medium", 0.4),
            ],
            "downtime_minutes": 30,
            "effort_hours": 8,
            "rollback": "medium",
        },
        "configuration_change": {
            "impacts": [
                ("workflow", "Business process behavior may change", "medium", 0.7),
                ("performance", "Configuration may affect query patterns", "low", 0.3),
            ],
            "downtime_minutes": 1,
            "effort_hours": 1,
            "rollback": "low",
        },
        "customization": {
            "impacts": [
                ("migration", "Custom code creates upgrade complexity", "high", 0.9),
                ("module", "Potential conflicts with standard modules", "medium", 0.5),
                ("performance", "Custom code should be reviewed for performance", "medium", 0.6),
            ],
            "downtime_minutes": 10,
            "effort_hours": 16,
            "rollback": "medium",
        },
        "migration": {
            "impacts": [
                ("migration", "Full schema migration required", "critical", 1.0),
                ("migration", "All custom modules need compatibility check", "high", 0.9),
                ("performance", "Migration may take hours for large databases", "high", 0.8),
                ("workflow", "Business process may change between versions", "medium", 0.7),
                ("security", "Security model may have changed", "medium", 0.6),
            ],
            "downtime_minutes": 120,
            "effort_hours": 40,
            "rollback": "high",
        },
    }

    def __init__(self, digital_twin=None):
        self.twin = digital_twin

    def simulate_change(self, change_type: str, change_target: str,
                        context: Optional[dict] = None) -> SimulationResult:
        """Simulate a proposed change and generate impact analysis."""
        from datetime import datetime

        sim_id = f"sim_{change_type}_{datetime.now():%Y%m%d_%H%M%S}"
        template = self.IMPACT_TEMPLATES.get(change_type)

        if not template:
            return SimulationResult(
                simulation_id=sim_id, change_type=change_type,
                change_target=change_target, success=False,
                error=f"No simulation template for: {change_type}",
            )

        impact_items = []
        for cat, desc, sev, prob in template["impacts"]:
            impact_items.append(ImpactItem(
                category=cat, description=desc, severity=sev, probability=prob,
                affected_entities=[change_target],
            ))

        # Filter/reduce impacts based on context
        if context:
            if context.get("version") == "19.0":
                impact_items = [i for i in impact_items
                                if i.category != "migration" or
                                "version" not in i.description.lower()]

        recommendations = [
            f"Test {change_type} in staging environment first",
            "Ensure database backup is available before execution",
            "Schedule during maintenance window",
            "Prepare rollback procedure",
        ]

        return SimulationResult(
            simulation_id=sim_id,
            change_type=change_type,
            change_target=change_target,
            success=True,
            impact_items=impact_items,
            estimated_downtime_minutes=template["downtime_minutes"],
            estimated_effort_hours=template["effort_hours"],
            rollback_complexity=template["rollback"],
            recommendations=recommendations,
        )

    def simulate_custom(self, change_type: str, change_target: str,
                         custom_impacts: List[ImpactItem]) -> SimulationResult:
        """Simulate with custom impact items."""
        from datetime import datetime
        sim_id = f"sim_custom_{datetime.now():%Y%m%d_%H%M%S}"
        return SimulationResult(
            simulation_id=sim_id, change_type=change_type,
            change_target=change_target, success=True,
            impact_items=custom_impacts,
            estimated_downtime_minutes=15,
            estimated_effort_hours=8,
            rollback_complexity="medium",
            recommendations=["Review all custom impacts before proceeding"],
        )
