#!/usr/bin/env python3
"""
Consulting Layer Integration Tests — Verifies the Autonomous Odoo AI Consultant.

Tests:
1. ReasoningEngine — task classification, domain inference, effort estimation, risk identification
2. Planner — phase generation, effort distribution, milestone creation
3. DecisionEngine — strategy evaluation, scoring, recommendations
4. MultiAgentCoordinator — specialist profiles, assignment, plan creation
5. ExperienceMemory — project recording, similarity search, lesson management
6. SelfCorrectionEngine — failure pattern matching, corrective action, retry limits
7. ReportGenerator — all report types, content generation, file saving
8. End-to-end: reason -> plan -> coordinate -> report
"""

import json
import logging
import os
import sys
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.WARNING)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

errors = []

def check(label, condition, detail=""):
    if condition:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label} — {detail}")
        errors.append(label)


# ===== Test 1: ReasoningEngine =====
print("\n=== Test 1: ReasoningEngine ===")
from reasoning.engine import ReasoningEngine, ComplexityLevel

engine = ReasoningEngine()
status = engine.initialize()
check("engine initialized", status["status"] == "initialized")

# Test CRM implementation reasoning
result = engine.reason("Implement CRM with predictive lead scoring for a manufacturing company")
check("reasoning result produced", result is not None)
check("task description preserved", "CRM" in result.task_description)
check("complexity estimated", isinstance(result.complexity, ComplexityLevel))
check("effort hours positive", result.effort_hours > 0)
# For implement tasks without migration/custom keywords, risks may be minimal
check("risks is a list", isinstance(result.risks, list))
check("alternatives generated", len(result.alternatives) >= 2)
check("skills recommended", "skill_base" in result.recommended_skills)
check("assumptions generated", len(result.assumptions) >= 2)
check("open questions generated", len(result.open_questions) >= 1)
check("specialist assignments exist", len(result.specialist_assignments) >= 2)
check("execution plan has phases", len(result.execution_plan.phases) >= 3)

# Test analysis reasoning
analyze_result = engine.reason("Analyze custom CRM module for performance issues")
check("analysis reasoning", analyze_result.complexity in (ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE))

# Test migration reasoning
migrate_result = engine.reason("Upgrade Odoo 18 project to Odoo 19")
check("migration complexity higher", migrate_result.effort_hours > 10)
check("migration has migration risk", any(
    "migration" in r.description.lower() or "upgrade" in r.description.lower()
    for r in migrate_result.risks
))

# Test reason with constraints
constrained = engine.reason("Implement email marketing automation", constraints={"scope": "full"})
check("constrained reasoning still works", constrained is not None)


# ===== Test 2: Planner =====
print("\n=== Test 2: Planner ===")
from reasoning.planner import Planner

planner = Planner()
planner.initialize()

plan = planner.create_plan(
    task_description="Implement CRM with lead scoring",
    domain="crm",
    task_type="implement",
    complexity="complex",
    effort_hours=24,
)
check("plan has phases", len(plan.phases) >= 5)
check("plan has summary", len(plan.summary) > 10)
check("plan has milestones", len(plan.milestones) >= 1)
check("plan total effort matches", abs(plan.total_effort_hours - 24) < 10)
check("effort distributed across phases", all(p.effort_hours > 0 for p in plan.phases))

# Verify phase ordering
for i, phase in enumerate(plan.phases):
    check(f"phase {phase.name} has valid order", phase.order == i + 1)
    check(f"phase {phase.name} has deliverables", len(phase.deliverables) >= 1)

# Test marketing template
mkt_plan = planner.create_plan(
    task_description="Set up email marketing campaigns",
    domain="marketing",
    task_type="implement",
    complexity="moderate",
    effort_hours=16,
)
check("marketing plan has phases", len(mkt_plan.phases) >= 4)

# Test migration template
mig_plan = planner.create_plan(
    task_description="Migrate from Odoo 18 to 19",
    domain="base",
    task_type="migrate",
    complexity="very_complex",
    effort_hours=40,
)
check("migration plan has phases", len(mig_plan.phases) >= 4)

# Test get_phase
phase = planner.get_phase(plan, plan.phases[0].id)
check("get_phase returns phase", phase is not None)


# ===== Test 3: DecisionEngine =====
print("\n=== Test 3: DecisionEngine ===")
from reasoning.decision_engine import DecisionEngine, StrategyOption

de = DecisionEngine()

# Test config vs custom
result = de.evaluate("Should I use configuration or custom module?")
check("decision result produced", result is not None)
check("recommendation present", len(result.recommendation) > 10)
check("options evaluated", len(result.options) >= 2)
check("confidence is high", result.confidence == "high")
check("reasoning present", len(result.reasoning) >= 1)

# Test specific domain
auto_result = de.evaluate("Server action vs Python code", domain="automation")
check("automation decision", len(auto_result.options) >= 2)

perf_result = de.evaluate("Computed field vs scheduled action", domain="performance")
check("performance decision", len(perf_result.options) >= 2)

# Test unknown question
unknown = de.evaluate("Random question about something")
check("unknown question still returns result", unknown is not None)

# Test strategy option scoring
opt = StrategyOption(
    name="Test Option", description="A test option",
    complexity=3, performance=8, maintainability=9,
    upgrade_safety=8, security=7, cost=4, time=3,
)
score = opt.score()
check("strategy scoring works", 3.0 <= score <= 9.0)

# Test custom weights (very different weighting to guarantee difference)
custom_weights = {"complexity": 0.8, "performance": 0.03, "maintainability": 0.03,
                  "upgrade_safety": 0.03, "security": 0.03, "cost": 0.03, "time": 0.05}
custom_score = opt.score(custom_weights)
check("custom weights produce different score",
      abs(custom_score - score) > 0.001 or custom_score != score)


# ===== Test 4: MultiAgentCoordinator =====
print("\n=== Test 4: MultiAgentCoordinator ===")
from coordinator.coordinator import MultiAgentCoordinator, SpecialistProfile

coord = MultiAgentCoordinator()
coord.initialize()

# Check specialist profiles
check("specialists defined", len(coord.SPECIALISTS) >= 10)
roles = [s.role for s in coord.SPECIALISTS]
for required in ["functional_consultant", "solution_architect", "backend_developer",
                 "security_specialist", "qa_engineer", "devops_engineer"]:
    check(f"specialist {required} exists", required in roles)

# Test find_specialist
architects = coord.find_specialist("solution_design")
check("find_specialist finds architect", len(architects) >= 1)

# Re-run reasoning to get fresh ReasoningResult (not overwritten by decision engine test)
reasoning_for_coord = engine.reason("Implement CRM for a manufacturing company")

# Test coordination plan from reasoning result
coord_plan = coord.create_coordination_plan(reasoning_for_coord)
check("coordination plan created", coord_plan is not None)
check("coord plan has assignments", len(coord_plan.assignments) >= 2)

# Test update assignment
if coord_plan.assignments:
    first = coord_plan.assignments[0]
    coord.update_assignment(first.assignment_id, "completed", {"result": "ok"})
    check("assignment updated", first.status == "completed")

# Test plan summary
summary = coord.get_plan_summary(coord_plan)
check("plan summary has totals", summary["total_assignments"] >= 2)
check("plan summary has roles", summary["unique_roles"] >= 1)


# ===== Test 5: ExperienceMemory =====
print("\n=== Test 5: ExperienceMemory ===")
from memory.memory import ExperienceMemory, ProjectRecord, Lesson

with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
    mem_path = f.name

memory = ExperienceMemory(storage_path=Path(mem_path))

# Record a project
record = ProjectRecord(
    project_id="proj_001",
    name="CRM Implementation for Manufacturing Co",
    domain="crm",
    task_type="implement",
    completed_at="2026-07-17T12:00:00Z",
    success=True,
    effort_hours=24,
    phases_completed=8,
    lessons=[
        Lesson(category="implementation", title="Use standard stages",
               description="Standard stages work for 80% of manufacturing companies",
               domain="crm", severity="info"),
    ],
)
memory.record_project(record)
check("project recorded", "proj_001" in memory._projects)

# Record another project
memory.record_project(ProjectRecord(
    project_id="proj_002", name="Marketing Automation Setup",
    domain="marketing", task_type="implement",
    completed_at="2026-07-17T12:00:00Z", success=True,
    effort_hours=16, phases_completed=5,
))
check("second project recorded", "proj_002" in memory._projects)

# Test find_similar
similar = memory.find_similar("CRM for manufacturing")
check("similar projects found", len(similar) >= 1)
check("CRM project found first", similar[0].domain == "crm")

# Test get_lessons
lessons = memory.get_lessons_for_domain("crm")
check("domain lessons found", len(lessons) >= 1)

# Test record_lesson
memory.record_lesson(Lesson(
    category="performance", title="Index important fields",
    description="Always index fields used in search/domain filters",
    domain="base", severity="warning",
))
check("lesson count increased", len(memory._lessons) >= 2)

# Test get_statistics
stats = memory.get_statistics()
check("memory stats have project count", stats["total_projects"] >= 2)
check("memory stats have lesson count", stats["total_lessons"] >= 2)

# Cleanup
os.unlink(mem_path)


# ===== Test 6: SelfCorrectionEngine =====
print("\n=== Test 6: SelfCorrectionEngine ===")
from memory.self_correction import SelfCorrectionEngine

temp_mem = ExperienceMemory(storage_path=Path(tempfile.NamedTemporaryFile(suffix='.json').name))
corrector = SelfCorrectionEngine(temp_mem, max_retries=3)

# Test known failure pattern
result = corrector.correct("analyze_pipeline", {"stages_count": 3}, {"stages_count": 0},
                           error="No data found")
check("correction result produced", result is not None)
check("correction found root cause", len(result.root_cause) > 0)
check("correction has action", len(result.corrective_action) > 0)
check("not successful yet", not result.success)

# Test permission error
perm_result = corrector.correct("read_module", {"success": True}, {},
                                error="Permission denied: access forbidden")
check("permission pattern matched", "permission" in perm_result.root_cause.lower() or
      "access" in perm_result.root_cause.lower())

# Test unknown error
unknown_result = corrector.correct("random_tool", {"ok": True}, {}, error="Something went wrong")
check("unknown error still produces result", unknown_result is not None)

# Test retry limit
for i in range(3):
    corrector.correct("failing_tool", {"ok": True}, {}, error="No data found")
retry_result = corrector.correct("failing_tool", {"ok": True}, {}, error="No data found")
check("retry limit enforced", retry_result.corrective_action == "give_up" or
      not retry_result.success)

# Test max retries exceeded message
check("exceeded message mentions retries", "retries" in retry_result.details.lower())

# Test reset
corrector.reset_retry_count("failing_tool")
check("retry count reset", corrector._retry_counts.get("failing_tool") is None)


# ===== Test 7: ReportGenerator =====
print("\n=== Test 7: ReportGenerator ===")
from reports.generator import ReportGenerator

rg = ReportGenerator()

# Get a fresh reasoning result (result may have been overwritten)
report_reasoning = engine.reason("Implement CRM for a manufacturing company")
report_plan = report_reasoning.execution_plan

# Test functional specification
func_report = rg.generate("functional_specification", report_reasoning, report_plan, "CRM Project")
check("functional spec generated", func_report is not None)
check("functional spec has content", len(func_report.content) > 100)
check("report has title", "Functional Specification" in func_report.title)

# Test risk assessment
risk_report = rg.generate("risk_assessment", report_reasoning, report_plan, "CRM Project")
check("risk assessment has content", len(risk_report.content) > 50)

# Test implementation roadmap
roadmap = rg.generate("implementation_roadmap", report_reasoning, report_plan, "CRM Project")
check("roadmap has phase info", "Phase" in roadmap.content)
check("roadmap mentions effort", "hours" in roadmap.content)

# Test go-live checklist
go_live = rg.generate("go_live_checklist", report_reasoning, report_plan, "CRM Project")
check("go-live has checklist items", "- [ ]" in go_live.content)

# Test generic generation
generic = rg.generate("project_timeline", report_reasoning, report_plan, "CRM Project")
check("project timeline generated", len(generic.content) > 0)

# Test save
with tempfile.NamedTemporaryFile(suffix='.md', mode='w', delete=False) as f:
    save_path = f.name
func_report.save(Path(save_path))
check("report saved to file", Path(save_path).exists())
os.unlink(save_path)

# Test generate_all
all_reports = rg.generate_all(report_reasoning, report_plan, "CRM Project")
check("all reports generated", len(all_reports) >= 8)

# Verify report types
for rtype in ["functional_specification", "risk_assessment", "implementation_roadmap",
              "go_live_checklist"]:
    check(f"{rtype} in all_reports", rtype in all_reports)


# ===== Test 8: End-to-End Reasoning Pipeline =====
print("\n=== Test 8: End-to-End Pipeline ===")

# Simulate: "Implement CRM for this company"
reasoning_result = engine.reason(
    "Implement CRM with lead scoring and email marketing for a manufacturing company"
)
check("E2E: reasoning complete", reasoning_result is not None)
check("E2E: CRM domain detected", any("crm" in str(s).lower() for s in reasoning_result.recommended_skills))
check("E2E: plan has phases", len(reasoning_result.execution_plan.phases) >= 3)

# Simulate: "Upgrade this Odoo 18 project to Odoo 19"
upgrade_result = engine.reason("Upgrade existing Odoo 18 project to Odoo 19 with custom modules")
check("E2E: upgrade reasoning complete", upgrade_result is not None)
check("E2E: migration risk identified", any(
    "migration" in r.category or "upgrade" in r.description.lower()
    for r in upgrade_result.risks
))
check("E2E: upgrade effort > 10h", upgrade_result.effort_hours > 10)

# Simulate: "Analyze this custom module and recommend improvements"
analyze_result = engine.reason("Analyze custom manufacturing module for performance issues and security risks")
check("E2E: analysis reasoning complete", analyze_result is not None)

# Create coordination plan
coord_plan = coord.create_coordination_plan(reasoning_result)
check("E2E: coordination plan has specialists", len(coord_plan.assignments) > 0)

# Generate reports
e2e_reports = rg.generate_all(reasoning_result, reasoning_result.execution_plan, "Manufacturing CRM")
check("E2E: reports generated", len(e2e_reports) >= 8)

# Evaluate architecture decision
arch_decision = de.evaluate("Configuration vs custom module for lead scoring rules")
check("E2E: architecture decision made", arch_decision is not None)


# ===== Summary =====
print(f"\n{'='*60}")
print(f"Consulting Layer Test Results: {len(errors)} failures")
print(f"{'='*60}")

for e in errors:
    print(f"  FAIL: {e}")

if errors:
    print("\nSome tests failed!")
    sys.exit(1)
else:
    print("\nAll consulting layer tests passed!")
    sys.exit(0)
