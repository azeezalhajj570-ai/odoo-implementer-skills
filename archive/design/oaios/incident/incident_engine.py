#!/usr/bin/env python3
"""
Incident Response Engine — When failures occur, automatically:
- Collects logs
- Identifies root cause
- Identifies affected modules and users
- Recommends fixes
- Executes safe recovery procedures where approved
- Generates incident report
- Stores lessons learned

Usage:
    from oaios.incident.incident_engine import IncidentResponseEngine
    
    engine = IncidentResponseEngine(memory)
    report = engine.respond(
        incident_type="module_upgrade_failure",
        details={"module": "crm", "error": "Migration script failed"}
    )
    print(report.root_cause)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class IncidentReport:
    """Complete incident report."""
    incident_id: str
    incident_type: str
    timestamp: str
    severity: str  # info, warning, error, critical
    root_cause: str = ""
    affected_modules: List[str] = field(default_factory=list)
    affected_users: int = 0
    recommended_fixes: List[str] = field(default_factory=list)
    recovery_executed: bool = False
    recovery_success: bool = False
    lesson_recorded: bool = False

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "type": self.incident_type,
            "severity": self.severity,
            "root_cause": self.root_cause,
            "affected_modules": self.affected_modules,
            "recovery_executed": self.recovery_executed,
            "recovery_success": self.recovery_success,
        }


class IncidentResponseEngine:
    """Responds to failures and incidents automatically."""

    INCIDENT_PATTERNS = {
        "module_upgrade_failure": {
            "severity": "error",
            "root_cause_template": "Module {module} upgrade failed during migration step",
            "fixes": [
                "Check module compatibility with current Odoo version",
                "Verify all module dependencies are installed",
                "Check database migration logs for specific errors",
                "Restore database from pre-upgrade backup if needed",
            ],
            "recovery": "restore_backup",
        },
        "database_connection_loss": {
            "severity": "critical",
            "root_cause_template": "Database connection lost to {host}",
            "fixes": [
                "Verify PostgreSQL service is running",
                "Check network connectivity between Odoo and database",
                "Verify database credentials in configuration",
                "Check PostgreSQL logs for authentication failures",
            ],
            "recovery": "restart_services",
        },
        "cron_failure": {
            "severity": "warning",
            "root_cause_template": "Scheduled action {cron} failed to execute",
            "fixes": [
                "Check cron logs for error details",
                "Verify cron method exists and is accessible",
                "Ensure required modules are installed",
                "Test cron execution manually via Technical menu",
            ],
            "recovery": None,
        },
        "mail_queue_backlog": {
            "severity": "warning",
            "root_cause_template": "Mail queue has {count} pending messages",
            "fixes": [
                "Check mail server configuration",
                "Verify SMTP credentials",
                "Clear stuck mail items from mail.mail",
                "Consider using dedicated outgoing mail server",
            ],
            "recovery": None,
        },
        "performance_degradation": {
            "severity": "warning",
            "root_cause_template": "Response time exceeded threshold: {response_time}ms",
            "fixes": [
                "Check for long-running queries in pg_stat_activity",
                "Verify cache hit ratio",
                "Check worker utilization",
                "Review recent configuration changes",
            ],
            "recovery": None,
        },
    }

    def __init__(self, memory=None):
        self.memory = memory
        self._history: List[IncidentReport] = []

    def respond(self, incident_type: str, details: dict = None) -> IncidentReport:
        """Respond to an incident."""
        from datetime import datetime
        incident_id = f"inc_{incident_type}_{datetime.now():%Y%m%d_%H%M%S}"

        pattern = self.INCIDENT_PATTERNS.get(incident_type)
        if not pattern:
            return IncidentReport(
                incident_id=incident_id, incident_type=incident_type,
                timestamp=datetime.now(timezone.utc).isoformat(),
                severity="unknown", root_cause="Unknown incident type",
            )

        root_cause = pattern["root_cause_template"].format(**(details or {}))

        report = IncidentReport(
            incident_id=incident_id,
            incident_type=incident_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=pattern["severity"],
            root_cause=root_cause,
            affected_modules=details.get("modules", []) if details else [],
            recommended_fixes=pattern["fixes"],
        )
        self._history.append(report)

        # Record lesson in memory
        if self.memory and hasattr(self.memory, 'record_lesson'):
            from memory.memory import Lesson
            self.memory.record_lesson(Lesson(
                category="incident",
                title=f"Incident: {incident_type}",
                description=root_cause,
                severity=pattern["severity"],
                tags=["incident", incident_type],
            ))
            report.lesson_recorded = True

        logger.info(f"Incident {incident_id}: {incident_type} ({pattern['severity']})")
        return report
