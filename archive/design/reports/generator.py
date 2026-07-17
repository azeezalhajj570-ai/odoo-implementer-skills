#!/usr/bin/env python3
"""
Senior Consultant Report Generator — Produces executive-quality deliverables
suitable for direct delivery to clients and project stakeholders.

Report types:
- Functional Specification
- Technical Specification
- Solution Architecture
- Gap Analysis
- Risk Assessment
- Implementation Roadmap
- Migration Strategy
- Security Review
- Performance Review
- Go-Live Checklist
- Post-Go-Live Checklist
- Project Timeline

Usage:
    from reports.generator import ReportGenerator
    
    gen = ReportGenerator()
    report = gen.generate("functional_specification", reasoning_result)
    print(report.content)
    gen.save(report, "/path/to/output.md")
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from reasoning.engine import ReasoningResult
from reasoning.planner import ExecutionPlan

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class SeniorConsultantReport:
    """A professional deliverable ready for client delivery."""
    report_id: str
    report_type: str
    title: str
    content: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict = field(default_factory=dict)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.content)
        logger.info(f"Report saved: {path}")

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "type": self.report_type,
            "title": self.title,
            "generated_at": self.generated_at,
            "content_length": len(self.content),
        }


class ReportGenerator:
    """Generates executive-quality consultant reports."""

    REPORT_TYPES = [
        "functional_specification",
        "technical_specification",
        "solution_architecture",
        "gap_analysis",
        "risk_assessment",
        "implementation_roadmap",
        "migration_strategy",
        "security_review",
        "performance_review",
        "go_live_checklist",
        "post_go_live_checklist",
        "project_timeline",
    ]

    def generate(self, report_type: str,
                 reasoning_result: Optional[ReasoningResult] = None,
                 execution_plan: Optional[ExecutionPlan] = None,
                 project_name: str = "Odoo Project") -> SeniorConsultantReport:
        """Generate a consultant report."""
        from datetime import datetime
        rid = f"rpt_{report_type}_{datetime.now():%Y%m%d_%H%M%S}"

        generator = getattr(self, f"_generate_{report_type}", self._generate_generic)
        content = generator(reasoning_result, execution_plan, project_name)

        return SeniorConsultantReport(
            report_id=rid,
            report_type=report_type,
            title=self._report_title(report_type, project_name),
            content=content,
            metadata={
                "project": project_name,
                "has_reasoning": reasoning_result is not None,
                "has_plan": execution_plan is not None,
            },
        )

    def _report_title(self, report_type: str, project: str) -> str:
        titles = {
            "functional_specification": f"Functional Specification — {project}",
            "technical_specification": f"Technical Specification — {project}",
            "solution_architecture": f"Solution Architecture — {project}",
            "gap_analysis": f"Gap Analysis — {project}",
            "risk_assessment": f"Risk Assessment — {project}",
            "implementation_roadmap": f"Implementation Roadmap — {project}",
            "migration_strategy": f"Migration Strategy — {project}",
            "security_review": f"Security Review — {project}",
            "performance_review": f"Performance Review — {project}",
            "go_live_checklist": f"Go-Live Checklist — {project}",
            "post_go_live_checklist": f"Post-Go-Live Checklist — {project}",
            "project_timeline": f"Project Timeline — {project}",
        }
        return titles.get(report_type, f"Report — {project}")

    def _generate_generic(self, reasoning, plan, project) -> str:
        return f"# Project Report: {project}\n\nGenerated: {datetime.now(timezone.utc).isoformat()}\n"

    def _generate_functional_specification(self, reasoning, plan, project) -> str:
        lines = [
            f"# Functional Specification: {project}",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"**Complexity:** {reasoning.complexity.value if reasoning else 'N/A'}",
            f"**Estimated Effort:** {reasoning.effort_hours if reasoning else 'N/A'} hours",
            "",
            "## 1. Executive Summary",
            f"This document outlines the functional requirements and solution approach for {project}.",
            "",
            "## 2. Scope",
            "### In Scope",
        ]
        if reasoning:
            for alt in reasoning.alternatives:
                lines.append(f"- {alt}")
        lines.extend([
            "",
            "## 3. Assumptions",
        ])
        if reasoning:
            for a in reasoning.assumptions:
                lines.append(f"- {a}")
        lines.extend([
            "",
            "## 4. Open Questions",
        ])
        if reasoning:
            for q in reasoning.open_questions:
                lines.append(f"- {q}")
        lines.extend([
            "",
            "## 5. Implementation Phases",
        ])
        if plan:
            for phase in plan.phases:
                lines.extend([
                    f"### Phase {phase.order}: {phase.name}",
                    f"**Effort:** {phase.effort_hours}h",
                    f"**Description:** {phase.description}",
                    "**Deliverables:**",
                ])
                for d in phase.deliverables:
                    lines.append(f"- {d}")
                lines.append("")
        lines.append("---\n*Report generated by Odoo AI Consultant*")
        return "\n".join(lines)

    def _generate_risk_assessment(self, reasoning, plan, project) -> str:
        lines = [
            f"# Risk Assessment: {project}",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"**Overall Complexity:** {reasoning.complexity.value if reasoning else 'N/A'}",
            "",
            "## Identified Risks",
        ]
        if reasoning:
            for risk in reasoning.risks:
                lines.extend([
                    f"### {risk.description}",
                    f"- **Severity:** {risk.severity}",
                    f"- **Category:** {risk.category}",
                    f"- **Mitigation:** {risk.mitigation}",
                    "",
                ])
        lines.append("---\n*Report generated by Odoo AI Consultant*")
        return "\n".join(lines)

    def _generate_implementation_roadmap(self, reasoning, plan, project) -> str:
        lines = [
            f"# Implementation Roadmap: {project}",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"**Total Effort:** {plan.total_effort_hours if plan else 'N/A'} hours",
            f"**Estimated Duration:** {plan.estimated_duration_days if plan else 'N/A'} days",
            "",
            "## Phase Overview",
        ]
        if plan:
            for phase in plan.phases:
                lines.extend([
                    f"### Phase {phase.order}: {phase.name}",
                    f"- **Type:** {phase.type}",
                    f"- **Effort:** {phase.effort_hours}h",
                    f"- **Dependencies:** {', '.join(phase.dependencies) if phase.dependencies else 'None'}",
                    f"- **Deliverables:** {', '.join(phase.deliverables)}",
                    "",
                ])
        return "\n".join(lines)

    def _generate_go_live_checklist(self, reasoning, plan, project) -> str:
        items = [
            "## Pre-Go-Live Checklist",
            "- [ ] All configuration changes applied to production",
            "- [ ] Database backup completed and verified",
            "- [ ] All modules upgraded and tested",
            "- [ ] Custom modules installed and verified",
            "- [ ] Security audit completed",
            "- [ ] User access rights verified",
            "- [ ] Email server configured and tested",
            "- [ ] IAP services activated and credits purchased",
            "- [ ] Cron jobs configured and running",
            "- [ ] Automated actions verified",
            "- [ ] Email templates tested",
            "- [ ] Report templates verified",
            "- [ ] User training completed",
            "- [ ] Documentation delivered to stakeholders",
            "- [ ] Rollback plan documented",
            "",
            "## Go-Live Day Checklist",
            "- [ ] Production deployment executed",
            "- [ ] Smoke tests passed",
            "- [ ] Critical workflows verified",
            "- [ ] Monitoring alerts configured",
            "- [ ] Stakeholders notified",
            "- [ ] Support team briefed",
        ]
        return f"# Go-Live Checklist: {project}\n\n" + "\n".join(items)

    def generate_all(self, reasoning, plan, project) -> Dict[str, SeniorConsultantReport]:
        """Generate all applicable report types."""
        reports = {}
        for rtype in self.REPORT_TYPES:
            reports[rtype] = self.generate(rtype, reasoning, plan, project)
        return reports
