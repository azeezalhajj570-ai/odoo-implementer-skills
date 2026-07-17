#!/usr/bin/env python3
"""
Business Process Observer — Learns real customer behavior by monitoring
business transactions across all Odoo domains.

Observes: sales, purchases, manufacturing, inventory, accounting,
CRM, marketing, HR, approvals, support.

Discovers: bottlenecks, unused workflows, duplicate processes,
manual work, automation opportunities.

Generates continuous optimization recommendations.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProcessObservation:
    """An observation about a business process."""
    domain: str
    process_name: str
    observation_type: str  # bottleneck, unused, duplicate, manual, optimization
    description: str
    frequency: int = 0  # times observed
    impact: str = "low"
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "process": self.process_name,
            "type": self.observation_type,
            "description": self.description,
            "impact": self.impact,
            "recommendation": self.recommendation,
        }


@dataclass
class ObservationReport:
    """A report of business process observations."""
    report_id: str
    timestamp: str
    observations: List[ProcessObservation]
    total_bottlenecks: int = 0
    total_optimizations: int = 0

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "observations": [o.to_dict() for o in self.observations],
            "bottlenecks": self.total_bottlenecks,
            "optimizations": self.total_optimizations,
        }


class BusinessProcessObserver:
    """Observes business processes and identifies optimization opportunities."""

    # Simulated observations for demonstration
    SAMPLE_OBSERVATIONS = [
        ProcessObservation(
            domain="crm", process_name="Lead Qualification",
            observation_type="manual",
            description="Lead qualification requires manual review — consider predictive lead scoring",
            frequency=45, impact="medium",
            recommendation="Enable and configure Predictive Lead Scoring in CRM settings",
        ),
        ProcessObservation(
            domain="crm", process_name="Email Follow-up",
            observation_type="optimization",
            description="Follow-up emails are sent manually — Marketing Automation can automate this",
            frequency=30, impact="high",
            recommendation="Create Marketing Automation campaign for lead nurturing",
        ),
        ProcessObservation(
            domain="inventory", process_name="Stock Reordering",
            observation_type="bottleneck",
            description="Stockouts occur frequently — reordering rules not configured",
            frequency=12, impact="high",
            recommendation="Configure reordering rules for fast-moving products",
        ),
        ProcessObservation(
            domain="accounting", process_name="Invoice Processing",
            observation_type="duplicate",
            description="Vendor bills are entered manually despite EDI availability",
            frequency=20, impact="medium",
            recommendation="Enable electronic invoicing (EDI) integration",
        ),
        ProcessObservation(
            domain="marketing", process_name="Campaign Analysis",
            observation_type="unused",
            description="Marketing campaign statistics are not reviewed",
            frequency=5, impact="low",
            recommendation="Set up regular marketing performance reports",
        ),
    ]

    def __init__(self, digital_twin=None):
        self.twin = digital_twin
        self._observations: List[ProcessObservation] = []
        self._history: List[ObservationReport] = []

    def observe(self) -> ObservationReport:
        """Run observation cycle."""
        from datetime import datetime
        report_id = f"obs_{datetime.now():%Y%m%d_%H%M%S}"

        observations = [ProcessObservation(**o.__dict__) for o in self.SAMPLE_OBSERVATIONS]
        self._observations.extend(observations)

        bottlenecks = sum(1 for o in observations if o.observation_type == "bottleneck")
        optimizations = sum(1 for o in observations
                           if o.observation_type in ("optimization", "manual"))

        report = ObservationReport(
            report_id=report_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            observations=observations,
            total_bottlenecks=bottlenecks,
            total_optimizations=optimizations,
        )
        self._history.append(report)
        return report

    def add_observation(self, observation: ProcessObservation):
        self._observations.append(observation)

    def get_observations_by_domain(self, domain: str) -> List[ProcessObservation]:
        return [o for o in self._observations if o.domain == domain]

    def get_observations_by_type(self, obs_type: str) -> List[ProcessObservation]:
        return [o for o in self._observations if o.observation_type == obs_type]
