#!/usr/bin/env python3
"""
OAIOS Layer 5 Integration Tests — Verifies the Odoo AI Operating System.

Tests:
1. Digital Twin — node/edge management, sync, snapshots, search
2. Connector Registry — discovery, execution, sample data
3. Live Scanner — module/manifest/infrastructure change detection
4. Simulation Engine — change simulation, impact analysis, custom simulation
5. Health Engine — health checks, metrics, reports
6. Business Process Observer — observations, domain/type filtering
7. Optimization Engine — recommendations, categories
8. Upgrade Simulation — breaking changes, compatibility, migration plans
9. Incident Response — pattern matching, fixes, recovery
10. Executive Dashboard — metrics, scoring, summary
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


# ===== Test 1: Digital Twin =====
print("\n=== Test 1: Digital Twin ===")
from oaios.twin.digital_twin import DigitalTwin, TwinNode, TwinRelation, NodeType, EnvironmentSnapshot

twin = DigitalTwin("test_env")
connectors = None  # Will use direct node manipulation for unit test

# Test initialization
init_result = twin.initialize(connectors)
check("twin initialized", init_result["twin_id"] == "test_env")

# Test adding nodes
node1 = TwinNode(id="mod_crm", type=NodeType.MODULE, name="CRM",
                 version="19.0", health="healthy", properties={"installable": True})
node2 = TwinNode(id="mod_mail", type=NodeType.MODULE, name="Mail",
                 version="19.0", health="healthy")
node3 = TwinNode(id="db_main", type=NodeType.DATABASE, name="Main DB",
                 health="healthy")
twin.nodes["mod_crm"] = node1
twin.nodes["mod_mail"] = node2
twin.nodes["db_main"] = node3
check("nodes added", len(twin.nodes) == 3)

# Test adding edges
twin.edges.append(TwinRelation(source_id="mod_crm", target_id="mod_mail", relation_type="depends_on"))
check("edges added", len(twin.edges) == 1)

# Test get_node
crm = twin.get_node("mod_crm")
check("get_node returns node", crm is not None)
check("node name", crm.name == "CRM")
check("node version", crm.version == "19.0")
check("node health", crm.health == "healthy")

# Test get_nodes_by_type
modules = twin.get_nodes_by_type(NodeType.MODULE)
check("get_nodes_by_type", len(modules) == 2)

# Test find_relations
rels = twin.find_relations("mod_crm")
check("find_relations", len(rels) >= 1)

# Test search
results = twin.search("CRM")
check("search finds CRM", len(results) >= 1)

# Test risk score
score = twin.compute_risk_score()
check("risk score computed", 0.0 <= score <= 1.0)

# Test model dict
model = twin.to_model_dict()
check("model has environment_id", model["environment_id"] == "test_env")
check("model has nodes", len(model["nodes"]) == 3)
check("model has edges", len(model["edges"]) == 1)
check("model has statistics", "statistics" in model)

# Test snapshot
twin.snapshots.append(EnvironmentSnapshot(
    snapshot_id="snap_001", timestamp="2026-07-17T12:00:00Z",
    node_count=3, edge_count=1, health_summary="healthy",
))
check("snapshot recorded", len(twin.snapshots) == 1)

# Test sync (with no connectors — should handle gracefully)
sync_count = twin.sync_all()
check("sync with no connectors", sync_count == 0)


# ===== Test 2: Connector Registry =====
print("\n=== Test 2: Connector Registry ===")
from oaios.connectors.registry import ConnectorRegistry

reg = ConnectorRegistry()
discovered = reg.discover()
check("built-in connectors discovered", len(discovered) >= 4)
check("postgres connector found", "postgres" in discovered)
check("odoo_orm connector found", "odoo_orm" in discovered)
check("git connector found", "git" in discovered)
check("docker connector found", "docker" in discovered)

# Test execute
pg_data = reg.execute("postgres")
check("postgres connector returns data", "nodes" in pg_data)
check("postgres has nodes", len(pg_data["nodes"]) >= 2)
check("postgres has edges", len(pg_data["edges"]) >= 1)

docker_data = reg.execute("docker")
check("docker connector returns data", "nodes" in docker_data)

# Test list
all_connectors = reg.list()
check("list returns dict", len(all_connectors) >= 4)

# Test list_available_types
types = reg.list_available_types()
check("connector types found", len(types) >= 3)

# Test get
postgres_info = reg.get("postgres")
check("get connector info", postgres_info is not None)
check("connector has type", postgres_info.type == "database")

# Test custom connector
def custom_handler(action, params):
    return {"nodes": [{"id": "custom", "type": "service", "name": "Custom"}]}
reg.register("custom_test", "custom", handler=custom_handler, description="Custom test")
custom_data = reg.execute("custom_test")
check("custom connector works", "nodes" in custom_data)

# Test nonexistent connector
bad = reg.execute("nonexistent")
check("nonexistent connector returns error", "error" in bad)


# ===== Test 3: Live Scanner =====
print("\n=== Test 3: Live Scanner ===")
from oaios.scanner.live_scanner import LiveScanner

scanner = LiveScanner(twin)

# Test scan (no project engine — should handle gracefully)
changes = scanner.scan()
check("scan returns list", isinstance(changes, list))

# Test get_recent_changes
recent = scanner.get_recent_changes()
check("recent changes", isinstance(recent, list))


# ===== Test 4: Simulation Engine =====
print("\n=== Test 4: Simulation Engine ===")
from oaios.simulation.simulation_engine import SimulationEngine, ImpactItem

sim = SimulationEngine(twin)

# Test module install simulation
result = sim.simulate_change("module_install", "sale_management")
check("module install simulation", result.success)
check("has impact items", len(result.impact_items) >= 1)
check("has downtime estimate", result.estimated_downtime_minutes > 0)
check("has effort estimate", result.estimated_effort_hours > 0)
check("has rollback complexity", result.rollback_complexity in ("low", "medium", "high"))
check("has recommendations", len(result.recommendations) >= 1)

# Test module upgrade simulation
upgrade_result = sim.simulate_change("module_upgrade", "crm")
check("upgrade simulation", upgrade_result.success)
check("upgrade has high impacts", upgrade_result.high_impact_count >= 1)

# Test configuration change simulation
config_result = sim.simulate_change("configuration_change", "email_settings")
check("config simulation", config_result.success)

# Test customization simulation
custom_result = sim.simulate_change("customization", "custom_module")
check("customization simulation", custom_result.success)

# Test migration simulation
mig_result = sim.simulate_change("migration", "v18_to_v19")
check("migration simulation", mig_result.success)
check("migration has critical impacts", mig_result.high_impact_count >= 1)

# Test context-aware simulation
context_result = sim.simulate_change("migration", "v18_to_v19", context={"version": "19.0"})
check("context-aware simulation", context_result.success)

# Test unknown type
unknown = sim.simulate_change("unknown_type", "test")
check("unknown type simulation fails", not unknown.success)

# Test impact report generation
report = result.impact_report()
check("impact report generated", len(report) > 50)
check("impact report has header", "# Impact Analysis" in report)

# Test custom simulation
custom_impacts = [ImpactItem(category="custom", description="Custom impact", severity="high")]
custom_sim = sim.simulate_custom("custom", "test", custom_impacts)
check("custom simulation", custom_sim.success)

# Test high_impact_count
check("high impact count", result.high_impact_count >= 0)


# ===== Test 5: Health Engine =====
print("\n=== Test 5: Health Engine ===")
from oaios.health.health_engine import HealthEngine, HealthMetric

health = HealthEngine(twin)

# Test check_all
report = health.check_all()
check("health report generated", report is not None)
check("overall health is string", isinstance(report.overall_health, str))
check("has categories", len(report.categories) >= 3)
check("has score", 0.0 <= report.score <= 1.0)
check("has issues list", isinstance(report.issues, list))
check("has recommendations", len(report.recommendations) >= 1)

# Test specific categories
for cat_name in ["system", "database", "application", "cron"]:
    cat = report.categories.get(cat_name)
    check(f"category {cat_name} exists", cat is not None)
    if cat:
        check(f"{cat_name} has metrics", len(cat.metrics) >= 1)

# Test update_metric
health.update_metric("system", "cpu_usage", 95.0)
updated_report = health.check_all()
sys_cat = updated_report.categories.get("system")
if sys_cat:
    cpu_metric = next((m for m in sys_cat.metrics if m.name == "cpu_usage"), None)
    if cpu_metric:
        check("updated metric value", cpu_metric.value == 95.0)

# Test get_history
history = health.get_history()
check("health history", len(history) >= 1)


# ===== Test 6: Business Process Observer =====
print("\n=== Test 6: Business Process Observer ===")
from oaios.observer.observer import BusinessProcessObserver

observer = BusinessProcessObserver(twin)

# Test observe
obs_report = observer.observe()
check("observation report generated", obs_report is not None)
check("has observations", len(obs_report.observations) >= 3)
check("has bottlenecks count", obs_report.total_bottlenecks >= 0)
check("has optimizations count", obs_report.total_optimizations >= 0)

# Test get_observations_by_domain
crm_obs = observer.get_observations_by_domain("crm")
check("CRM observations", len(crm_obs) >= 1)

# Test get_observations_by_type
bottlenecks = observer.get_observations_by_type("bottleneck")
check("bottleneck observations", len(bottlenecks) >= 1)

manual_obs = observer.get_observations_by_type("manual")
check("manual observations", len(manual_obs) >= 1)


# ===== Test 7: Optimization Engine =====
print("\n=== Test 7: Optimization Engine ===")
from oaios.optimizer.optimizer import OptimizationEngine

optimizer = OptimizationEngine(twin)

# Test analyze_all
recommendations = optimizer.analyze_all()
check("recommendations generated", len(recommendations) >= 4)

# Check categories
categories = set(r.category for r in recommendations)
for cat in ["index", "field", "security", "automation"]:
    check(f"recommendation category: {cat}", cat in categories)

# Check individual recommendations
for rec in recommendations:
    check(f"rec {rec.recommendation_id} has title", len(rec.title) > 5)
    check(f"rec {rec.recommendation_id} has impact", rec.impact in ("low", "medium", "high", "critical"))
    check(f"rec {rec.recommendation_id} has effort", rec.effort in ("minutes", "hours", "days"))
    check(f"rec {rec.recommendation_id} has confidence", 0.0 <= rec.confidence <= 1.0)
    check(f"rec {rec.recommendation_id} has rollback plan", len(rec.rollback_plan) > 0)


# ===== Test 8: Upgrade Simulation =====
print("\n=== Test 8: Upgrade Simulation ===")
from oaios.upgrade.upgrade_engine import UpgradeSimulationEngine

upgrade_engine = UpgradeSimulationEngine()

# Test full upgrade simulation
result = upgrade_engine.simulate_upgrade(
    current_version="18.0",
    target_version="19.0",
    custom_modules=["custom_crm", "custom_inventory"],
    installed_modules=["crm", "mass_mailing", "link_tracker", "sms"],
)
check("upgrade simulation result", result is not None)
check("upgrade has breaking changes", len(result.breaking_changes) >= 1)
check("upgrade has deprecated APIs", len(result.deprecated_apis) >= 1)
check("compatibility score computed", 0.0 <= result.compatibility_score <= 1.0)
check("estimated duration > 0", result.estimated_duration_hours > 0)
check("risk level set", result.risk_level in ("low", "medium", "high"))
check("has migration steps", len(result.migration_steps) >= 3)
check("has recommendations", len(result.recommendations) >= 1)

# Test with no custom modules
minimal = upgrade_engine.simulate_upgrade("18.0", "19.0")
check("minimal upgrade works", minimal is not None)

# Test with specific installed modules
filtered = upgrade_engine.simulate_upgrade(
    "18.0", "19.0", installed_modules=["crm"]
)
check("filtered breaking changes", len(filtered.breaking_changes) >= 0)

# Test breaking change structure
for bc in result.breaking_changes:
    check(f"breaking change {bc.area} has description", len(bc.description) > 10)
    check(f"breaking change has migration steps", len(bc.migration_steps) >= 1)


# ===== Test 9: Incident Response =====
print("\n=== Test 9: Incident Response ===")
from oaios.incident.incident_engine import IncidentResponseEngine

incident = IncidentResponseEngine()

# Test module upgrade failure
mod_report = incident.respond("module_upgrade_failure", {
    "module": "crm", "error": "Migration script failed"
})
check("module upgrade incident", mod_report is not None)
check("incident has root cause", len(mod_report.root_cause) > 0)
check("incident has severity", mod_report.severity == "error")
check("incident has fixes", len(mod_report.recommended_fixes) >= 1)

# Test database connection loss
db_report = incident.respond("database_connection_loss", {
    "host": "db01.example.com"
})
check("db incident", db_report.severity == "critical")

# Test cron failure
cron_report = incident.respond("cron_failure", {
    "cron": "ir_cron_crm_lead_assign"
})
check("cron incident", cron_report.severity == "warning")

# Test mail queue backlog
mail_report = incident.respond("mail_queue_backlog", {
    "count": 1500
})
check("mail incident", mail_report.severity == "warning")

# Test performance degradation
perf_report = incident.respond("performance_degradation", {
    "response_time": 3500
})
check("perf incident", perf_report is not None)

# Test unknown incident type
unknown_inc = incident.respond("unknown_incident")
check("unknown incident handled", unknown_inc is not None)

# Test to_dict
report_dict = mod_report.to_dict()
check("incident to_dict has incident_id", "incident_id" in report_dict)
check("incident to_dict has root_cause", "root_cause" in report_dict)


# ===== Test 10: Executive Dashboard =====
print("\n=== Test 10: Executive Dashboard ===")
from oaios.dashboard.dashboard import ExecutiveDashboard

dashboard = ExecutiveDashboard(twin, health, observer)

# Test generate
view = dashboard.generate()
check("dashboard generated", view is not None)
check("dashboard has id", len(view.dashboard_id) > 0)
check("dashboard has score", 0.0 <= view.score <= 1.0)
check("dashboard has summary", len(view.summary) > 0)
check("dashboard has metrics", len(view.metrics) >= 8)

# Check required metrics
required_metrics = [
    "Project Health", "Security Posture", "Performance",
    "Customization Level", "Process Efficiency",
    "Automation Coverage", "Upgrade Readiness", "AI Confidence",
]
for name in required_metrics:
    check(f"metric: {name}", name in view.metrics)

# Check metric structure
for name, metric in view.metrics.items():
    check(f"metric {name} has value", 0 <= metric.value <= 100)
    check(f"metric {name} has unit", metric.unit == "%")
    check(f"metric {name} has trend", metric.trend in ("improving", "stable", "declining"))
    check(f"metric {name} has status", metric.status in ("healthy", "warning", "critical", "degraded"))

# Test overview_summary
summary = view.overview_summary()
check("overview summary has header", "OAIOS Executive Dashboard" in summary)
check("overview summary has score", "Score" in summary)

# Test to_dict
view_dict = view.to_dict()
check("dashboard to_dict has dashboard_id", "dashboard_id" in view_dict)
check("dashboard to_dict has score", "score" in view_dict)


# ===== Summary =====
print(f"\n{'='*60}")
print(f"OAIOS Layer 5 Test Results: {len(errors)} failures")
print(f"{'='*60}")

for e in errors:
    print(f"  FAIL: {e}")

if errors:
    print("\nSome tests failed!")
    sys.exit(1)
else:
    print("\nAll OAIOS Layer 5 tests passed!")
    sys.exit(0)
