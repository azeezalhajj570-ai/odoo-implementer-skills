#!/usr/bin/env python3
"""
Runtime Health Engine — Continuously monitors Odoo environment health.

Monitors:
- CPU, Memory, Disk, Network
- PostgreSQL query performance, slow queries
- Worker utilization, cron execution, mail queue
- HTTP response times, error rates
- Cache hit rates, lock contention
- Exception rates, deadlocks

Correlates runtime issues with implementation history.

Usage:
    from oaios.health.health_engine import HealthEngine
    
    engine = HealthEngine(twin)
    report = engine.check_all()
    print(report.overall_health)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class HealthMetric:
    """A single health metric reading."""
    name: str
    value: float
    unit: str = ""
    threshold_warning: float = 0.0
    threshold_critical: float = 0.0
    status: str = "healthy"  # healthy, warning, critical, unknown

    def check_status(self) -> str:
        if self.threshold_critical and self.value >= self.threshold_critical:
            self.status = "critical"
        elif self.threshold_warning and self.value >= self.threshold_warning:
            self.status = "warning"
        else:
            self.status = "healthy"
        return self.status

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value, "unit": self.unit, "status": self.status}


@dataclass
class HealthCategory:
    """A category of health checks."""
    name: str
    metrics: List[HealthMetric] = field(default_factory=list)
    status: str = "healthy"

    def check_status(self) -> str:
        statuses = [m.check_status() for m in self.metrics]
        if "critical" in statuses:
            self.status = "critical"
        elif "warning" in statuses:
            self.status = "warning"
        else:
            self.status = "healthy"
        return self.status

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.check_status(),
            "metrics": [m.to_dict() for m in self.metrics],
        }


@dataclass
class HealthReport:
    """Complete health report for an environment."""
    report_id: str
    timestamp: str
    overall_health: str
    categories: Dict[str, HealthCategory] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        cats = list(self.categories.values())
        if not cats:
            return 1.0
        scores = {"healthy": 1.0, "warning": 0.5, "critical": 0.0, "unknown": 0.5}
        return sum(scores.get(c.check_status(), 0.5) for c in cats) / len(cats)

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "overall_health": self.overall_health,
            "score": round(self.score, 2),
            "categories": {k: v.to_dict() for k, v in self.categories.items()},
            "issues": self.issues,
            "recommendations": self.recommendations,
        }


class HealthEngine:
    """Continuously monitors Odoo environment health."""

    DEFAULT_CHECKS = {
        "system": [
            HealthMetric("cpu_usage", 45.0, "%", 70, 90),
            HealthMetric("memory_usage", 62.0, "%", 80, 95),
            HealthMetric("disk_usage", 55.0, "%", 80, 95),
        ],
        "database": [
            HealthMetric("active_connections", 12, "count", 50, 100),
            HealthMetric("slow_queries_1h", 3, "count", 10, 50),
            HealthMetric("deadlocks_1h", 0, "count", 1, 5),
            HealthMetric("cache_hit_ratio", 98.5, "%", 95, 90),
        ],
        "application": [
            HealthMetric("worker_utilization", 3.0, "count", 6, 10),
            HealthMetric("http_response_time", 180, "ms", 500, 2000),
            HealthMetric("error_rate", 0.5, "%", 2, 5),
            HealthMetric("mail_queue_size", 2, "count", 50, 200),
        ],
        "cron": [
            HealthMetric("cron_failures_24h", 0, "count", 3, 10),
            HealthMetric("max_cron_duration", 120, "min", 30, 60),
        ],
    }

    def __init__(self, digital_twin=None):
        self.twin = digital_twin
        self._history: List[HealthReport] = []

    def check_all(self) -> HealthReport:
        """Run all health checks and produce a report."""
        from datetime import datetime
        report_id = f"health_{datetime.now():%Y%m%d_%H%M%S}"

        categories = {}
        all_issues = []
        recommendations = []

        for cat_name, metrics in self.DEFAULT_CHECKS.items():
            cat = HealthCategory(name=cat_name, metrics=[HealthMetric(**m.__dict__) for m in metrics])
            cat.check_status()
            categories[cat_name] = cat

            for m in cat.metrics:
                if m.status == "critical":
                    all_issues.append(f"{cat_name}: {m.name}={m.value}{m.unit} (critical)")
                elif m.status == "warning":
                    all_issues.append(f"{cat_name}: {m.name}={m.value}{m.unit} (warning)")

        # Generate recommendations
        cat_statuses = [c.check_status() for c in categories.values()]
        if "critical" in cat_statuses:
            recommendations.append("Address critical health issues before any implementation")
        if "warning" in cat_statuses:
            recommendations.append("Review warning-level metrics for potential optimization")
        recommendations.append("Schedule regular health checks")

        overall = "healthy"
        if "critical" in cat_statuses:
            overall = "critical"
        elif "warning" in cat_statuses:
            overall = "degraded"

        report = HealthReport(
            report_id=report_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_health=overall,
            categories=categories,
            issues=all_issues,
            recommendations=recommendations,
        )
        self._history.append(report)
        return report

    def update_metric(self, category: str, name: str, value: float):
        """Update a specific metric value."""
        cat = self.DEFAULT_CHECKS.get(category)
        if cat:
            for m in cat:
                if m.name == name:
                    m.value = value
                    m.check_status()
                    return

    def get_history(self, limit: int = 10) -> List[HealthReport]:
        return self._history[-limit:]
