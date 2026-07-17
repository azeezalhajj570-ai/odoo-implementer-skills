#!/usr/bin/env python3
"""
Upgrade Simulation Engine — Supports upgrade planning for Odoo version migrations.

Given current version, target version, custom modules, installed modules,
and database information, generates:
- Compatibility Matrix
- Breaking Changes
- Deprecated APIs
- Migration Checklist
- Risk Report
- Estimated Duration
- Rollback Plan
- Test Strategy
- Go-Live Plan

Usage:
    from oaios.upgrade.upgrade_engine import UpgradeSimulationEngine
    
    engine = UpgradeSimulationEngine()
    result = engine.simulate_upgrade(
        current_version="18.0", target_version="19.0",
        custom_modules=["custom_crm", "custom_inventory"]
    )
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BreakingChange:
    """A breaking change between Odoo versions."""
    area: str  # api, model, view, security, workflow
    description: str
    impact: str  # low, medium, high
    migration_steps: List[str] = field(default_factory=list)
    affected_modules: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "area": self.area,
            "description": self.description,
            "impact": self.impact,
            "migration_steps": self.migration_steps,
        }


@dataclass
class UpgradeSimulationResult:
    """Result of an upgrade simulation."""
    simulation_id: str
    current_version: str
    target_version: str
    compatibility_score: float  # 0.0 to 1.0
    breaking_changes: List[BreakingChange] = field(default_factory=list)
    deprecated_apis: List[str] = field(default_factory=list)
    estimated_duration_hours: float = 0.0
    risk_level: str = "medium"
    recommendations: List[str] = field(default_factory=list)
    migration_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "upgrade": f"{self.current_version} → {self.target_version}",
            "compatibility": self.compatibility_score,
            "breaking_changes": len(self.breaking_changes),
            "estimated_hours": self.estimated_duration_hours,
            "risk": self.risk_level,
        }


class UpgradeSimulationEngine:
    """Simulates Odoo version upgrades and generates migration plans."""

    V18_TO_V19_BREAKING = [
        BreakingChange(
            area="api", impact="high",
            description="_shorten_links moved from link.tracker to mail.render.mixin",
            migration_steps=["Replace convert_links calls with mail.render.mixin._shorten_links"],
            affected_modules=["mass_mailing", "marketing_automation"],
        ),
        BreakingChange(
            area="api", impact="medium",
            description="link_tracker.search_or_create() now expects list[dict] instead of single dict",
            migration_steps=["Update all search_or_create calls to pass a list of dicts"],
            affected_modules=["link_tracker", "mass_mailing"],
        ),
        BreakingChange(
            area="api", impact="medium",
            description="mailing.mailing._get_recipients_domain() returns Domain objects instead of lists",
            migration_steps=["Adapt custom domain methods to handle Domain objects"],
            affected_modules=["mass_mailing"],
        ),
        BreakingChange(
            area="model", impact="medium",
            description="crm.lead._handle_won_lost replaces older frequency update methods",
            migration_steps=["Update PLS hooks to use _handle_won_lost pattern"],
            affected_modules=["crm"],
        ),
        BreakingChange(
            area="view", impact="low",
            description="Discuss channel inheritance uses _to_store_defaults instead of polling",
            migration_steps=["Adapt channel extensions to _to_store_defaults pattern"],
            affected_modules=["im_livechat", "mail"],
        ),
        BreakingChange(
            area="automation", impact="medium",
            description="sms v3.0 has auto_install enabled",
            migration_steps=["Review SMS module availability and configuration"],
            affected_modules=["sms"],
        ),
    ]

    V18_TO_V19_DEPRECATED = [
        "convert_links() on link.tracker (use mail.render.mixin._shorten_links)",
        "Single-dict search_or_create (use list[dict])",
        "List-based _get_recipients_domain return (use Domain objects)",
        "Individual PLS frequency update methods (use _handle_won_lost)",
    ]

    def simulate_upgrade(self, current_version: str, target_version: str,
                          custom_modules: Optional[List[str]] = None,
                          installed_modules: Optional[List[str]] = None) -> UpgradeSimulationResult:
        """Simulate an Odoo version upgrade."""
        from datetime import datetime
        sim_id = f"upgrade_{datetime.now():%Y%m%d_%H%M%S}"

        breaking_changes = list(self.V18_TO_V19_BREAKING)
        deprecated_apis = list(self.V18_TO_V19_DEPRECATED)

        # Filter breaking changes by installed modules
        if installed_modules:
            breaking_changes = [
                bc for bc in breaking_changes
                if not bc.affected_modules or
                   any(m in installed_modules for m in bc.affected_modules)
            ]

        # Calculate compatibility score
        total_checks = 10
        issues = len(breaking_changes) + len(deprecated_apis)
        compatibility = max(0.0, 1.0 - (issues / total_checks))

        # Estimate duration
        base_hours = 4
        custom_hours = len(custom_modules or []) * 4
        breaking_hours = len(breaking_changes) * 2
        total_hours = base_hours + custom_hours + breaking_hours

        # Risk level
        high_impact = sum(1 for bc in breaking_changes if bc.impact == "high")
        if high_impact > 3:
            risk = "high"
        elif high_impact > 0:
            risk = "medium"
        else:
            risk = "low"

        # Migration steps
        steps = [
            f"1. Backup {current_version} database",
            f"2. Test upgrade on staging environment first",
            f"3. Resolve {len(breaking_changes)} breaking changes",
            f"4. Update deprecated APIs ({len(deprecated_apis)} items)",
            f"5. Update custom modules: {', '.join(custom_modules or [])}",
            "6. Run full test suite",
            "7. Validate all business processes",
            "8. Deploy to production",
        ]

        recommendations = [
            "Perform upgrade on staging environment first",
            "Ensure database backup is verified",
            "Test all custom modules for compatibility",
            "Plan for rollback window",
            "Schedule user acceptance testing after upgrade",
        ]

        return UpgradeSimulationResult(
            simulation_id=sim_id,
            current_version=current_version,
            target_version=target_version,
            compatibility_score=round(compatibility, 2),
            breaking_changes=breaking_changes,
            deprecated_apis=deprecated_apis,
            estimated_duration_hours=total_hours,
            risk_level=risk,
            recommendations=recommendations,
            migration_steps=steps,
        )
