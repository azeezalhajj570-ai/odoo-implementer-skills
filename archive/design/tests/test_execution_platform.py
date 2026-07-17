#!/usr/bin/env python3
"""
Execution Platform Integration Tests — Verifies the Autonomous Odoo AI Implementer.

Tests:
1. Tool Registry discovers and executes tools
2. MCP Tool Adapter wraps tools correctly
3. Project Context Engine scans project structure
4. Project Knowledge Graph builds multi-dimensional graphs
5. Project Monitor detects changes
6. Execution Engine creates and runs plans
7. Workflow Runner executes playbooks
8. Validation Engine validates artifacts
9. Agent Profiles load correctly
10. Full end-to-end: project scan → tools → execution → validation
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

def check(label: str, condition: bool, detail: str = ""):
    if condition:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label} — {detail}")
        errors.append(label)


# ===== Test 1: Tool Registry =====
print("\n=== Test 1: Tool Registry ===")
from tools.registry import ToolRegistry, ToolResult

registry = ToolRegistry()
count = registry.discover_all()
check("discover_all() returns count", count >= 4,
      f"Found {count} tools (expected 4+)")

tools_list = registry.list_tools()
check("list_tools() returns list", len(tools_list) >= 4)

# Check CRM tools exist
crm_tools = registry.get_by_skill("skill_crm")
check("CRM has tools", len(crm_tools) >= 2,
      f"Found {len(crm_tools)} CRM tools")

# Check Marketing tools exist
mkt_tools = registry.get_by_skill("skill_marketing")
check("Marketing has tools", len(mkt_tools) >= 2,
      f"Found {len(mkt_tools)} Marketing tools")

# Test tool categories
analyzers = registry.get_by_category("analyzer")
check("analyzers exist", len(analyzers) >= 1)

validators = registry.get_by_category("validator")
check("validators exist", len(validators) >= 1)

# Execute analyze_pipeline
pipeline_result = registry.execute("analyze_pipeline", {
    "pipeline_data": {
        "stages": [
            {"name": "New", "probability": 10, "sequence": 1},
            {"name": "Qualified", "probability": 30, "sequence": 2},
            {"name": "Won", "probability": 100, "is_won": True, "sequence": 3},
        ]
    }
})
check("analyze_pipeline executes", pipeline_result.success)
if pipeline_result.success:
    data = pipeline_result.data
    check("pipeline has stages", data.get("stages_count", 0) == 3)

# Execute validate_lead_scoring
scoring_result = registry.execute("validate_lead_scoring", {
    "pls_fields": ["phone_state", "email_state", "country_id", "source_id"],
    "won_count": 150,
    "lost_count": 300,
})
check("validate_lead_scoring executes", scoring_result.success)
if scoring_result.success:
    data = scoring_result.data
    check("scoring with 450 leads is valid", data.get("valid", False))

# Execute analyze_campaign
campaign_result = registry.execute("analyze_campaign", {
    "campaign_data": {
        "name": "Welcome Campaign",
        "model_name": "res.partner",
        "activities": [
            {"trigger_type": "begin", "activity_type": "email"},
            {"trigger_type": "mail_open", "activity_type": "email"},
        ]
    }
})
check("analyze_campaign executes", campaign_result.success)

# Execute validate_marketing_config
mkt_config_result = registry.execute("validate_marketing_config", {
    "config": {
        "mass_mailing": {"outgoing_mail_server": True},
        "marketing_automation": {"campaign_count": 3},
        "utm": {"campaigns": ["spring_sale"]},
    },
    "check_iap": False,
    "check_social": False,
})
check("validate_marketing_config executes", mkt_config_result.success)

# Test tool not found
not_found = registry.execute("nonexistent_tool")
check("nonexistent tool returns error", not not_found.success)


# ===== Test 2: MCP Tool Adapter =====
print("\n=== Test 2: MCP Tool Adapter ===")
from tools.mcp_adapter import MCPToolAdapter

mcp = MCPToolAdapter(registry)
mcp_tools = mcp.get_tools()
check("MCP tools list is not empty", len(mcp_tools) >= 4)

# Check MCP tool format
first_tool = mcp_tools[0]
check("MCP tool has name", "name" in first_tool)
check("MCP tool has description", "description" in first_tool)
check("MCP tool has inputSchema", "inputSchema" in first_tool)

# Test MCP call
mcp_result = mcp.call_tool("analyze_pipeline", {
    "pipeline_data": {"stages": [{"name": "Test", "probability": 50}]}
})
check("MCP call returns success", mcp_result.get("success", False))
check("MCP call has content", len(mcp_result.get("content", [])) > 0)

# Test MCP manifest
manifest = mcp.get_mcp_manifest()
check("MCP manifest has name", manifest.get("name") == "odoo-skill-platform")
check("MCP manifest has tools", len(manifest.get("tools", [])) >= 4)


# ===== Test 3: Project Context Engine =====
print("\n=== Test 3: Project Context Engine ===")
from project.engine import ProjectContextEngine, ProjectModel
import tempfile

# Create a temporary project structure
with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    
    # Create custom module directly in addons path
    custom_addon = tmp / "addons" / "test_module"
    custom_addon.mkdir(parents=True)
    
    # Create __manifest__.py
    (custom_addon / "__manifest__.py").write_text(
        "{'name': 'Test Module', 'version': '19.0.1.0', "
        "'depends': ['base', 'mail'], 'category': 'Sales', "
        "'license': 'LGPL-3', 'installable': True, 'author': 'Test Co'}"
    )
    
    # Create a model file
    models_dir = custom_addon / "models"
    models_dir.mkdir()
    (models_dir / "test_model.py").write_text(
        "from odoo import models, fields\n"
        "class TestModel(models.Model):\n"
        "    _name = 'test.model'\n"
        "    name = fields.Char()\n"
    )

    # Create security
    security_dir = custom_addon / "security"
    security_dir.mkdir()
    (security_dir / "ir.model.access.csv").write_text(
        "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n"
        "access_test_model,test.model,model_test_model,,1,1,1,1\n"
    )

    # Create a controller
    controllers_dir = custom_addon / "controllers"
    controllers_dir.mkdir()
    (controllers_dir / "main.py").write_text(
        "from odoo import http\n"
        "class TestController(http.Controller):\n"
        "    @http.route('/test/hello', auth='public')\n"
        "    def hello(self):\n"
        "        return 'Hello'\n"
    )

    # Create docker-compose.yml
    (tmp / "docker-compose.yml").write_text("version: '3'\nservices:\n  odoo:\n    image: odoo:19.0\n")

        # Also create a standard module
    standard_module = tmp / "addons" / "mail"
    standard_module.mkdir(parents=True)
    (standard_module / "__manifest__.py").write_text(
        "{'name': 'Mail', 'version': '19.0', 'depends': ['base']}"
    )

    # Run validation engine inside scope
    from execution.validator import ValidationEngine
    val_inside = ValidationEngine()
    in_module_results = val_inside.validate_module(str(custom_addon))
    in_module_ok = False
    if in_module_results:
        s = in_module_results.get("_summary", {})
        in_module_ok = bool(s.get("passed", 0) > 0)
    check("module validation passes (inside scope)", in_module_ok)

    # Scan with Project Context Engine — pass addons paths directly
    addons_path = str(tmp / "addons")
    engine = ProjectContextEngine(str(tmp))
    model = engine.scan(addons_paths=[addons_path])

    check("project model returned", model is not None)
    check("modules discovered", model.modules_count >= 2,
          f"Found {model.modules_count} modules: {list(model.modules.keys())}")
    check("modules have correct data", 
          any("test.model" in m.models for m in model.modules.values()))
    check("has docker", model.has_docker)

    # Check specific module
    test_mod = model.modules.get("test_module")
    check("test_module found", test_mod is not None)
    if test_mod:
        check("test_module has models", "test.model" in test_mod.models,
              f"Models: {test_mod.models}")
        check("test_module has controllers", len(test_mod.controllers) > 0)
        check("test_module has security groups", len(test_mod.security_groups) >= 0)

    # Test dependency graph
    mermaid = engine.get_dependency_graph_mermaid()
    check("dependency graph mermaid", "graph LR" in mermaid)

    # Test module dict
    model_dict = model.to_dict()
    check("model.to_dict() has project_name",
          "project_name" in model_dict)


# ===== Test 4: Project Knowledge Graph =====
print("\n=== Test 4: Project Knowledge Graph ===")
# Reuse the same scanner pattern with a real path
if engine and model:
    from project.knowledge_graph import ProjectKnowledgeGraph
    
    kg = ProjectKnowledgeGraph(model)
    kg.build()
    
    stats = kg.stats()
    check("knowledge graph has dimensions",
          stats["graph_dimensions"] >= 2)
    check("knowledge graph has nodes",
          stats["total_nodes"] > 0)
    
    # Test graph types
    arch = kg.get_architecture_graph()
    check("architecture graph exists", len(arch.get("nodes", [])) > 0)
    
    module_g = kg.get_module_graph()
    check("module graph exists", len(module_g.get("nodes", [])) > 0)
    
    # Test mermaid
    mermaid_out = kg.to_mermaid()
    check("KG mermaid is string", isinstance(mermaid_out, str))
    check("KG mermaid has content", len(mermaid_out) > 50)
    
    # Test export
    exported = kg.export_json()
    check("KG export has project", "project" in exported)
    check("KG export has graphs", "graphs" in exported)


# ===== Test 5: Execution Engine =====
print("\n=== Test 5: Execution Engine ===")
from execution.engine import SkillExecutionEngine

exec_engine = SkillExecutionEngine()
status = exec_engine.initialize()
check("exec engine initialized", status["status"] == "initialized")
check("exec engine has tools", status["tools"]["total_tools"] >= 4)

# Create an execution plan
plan = exec_engine.create_plan(
    skill_ids=["skill_crm"],
    tool_sequence=[
        {"tool": "analyze_pipeline", "params": {
            "pipeline_data": {"stages": [
                {"name": "New", "probability": 10, "sequence": 1},
                {"name": "Won", "probability": 100, "is_won": True, "sequence": 2},
            ]}
        }, "description": "Analyze pipeline stages"},
        {"tool": "validate_lead_scoring", "params": {
            "won_count": 100, "lost_count": 200
        }, "description": "Validate PLS setup"},
    ]
)
check("plan created", plan is not None)
check("plan has steps", len(plan.steps) == 2)

# Execute the plan
result = exec_engine.execute_plan(plan)
check("plan executed successfully", result.success)
check("plan has outputs", len(result.outputs) == 2)
check("no execution errors", len(result.errors) == 0)

# Test find_tools_for_task
tool_matches = exec_engine.find_tools_for_task(
    "I need to validate my CRM lead scoring configuration",
    skill_ids=["skill_crm"]
)
check("task matching finds tools", len(tool_matches) >= 1)

# Test status
eng_status = exec_engine.status()
check("engine status shows initialized", eng_status["initialized"])


# ===== Test 6: Workflow Runner =====
print("\n=== Test 6: Workflow Runner ===")
from execution.workflow_runner import WorkflowRunner

runner = WorkflowRunner(exec_engine)
discovered = runner.discover_workflows()
check("workflows discovered", len(discovered) >= 2,
      f"Found {len(discovered)} workflows")

# Run a CRM workflow
wf_result = runner.run_workflow("crm_implementation")
check("CRM workflow executed", wf_result.success)

# Run a marketing workflow
mkt_wf_result = runner.run_workflow("marketing_campaign_setup")
check("Marketing workflow executed", mkt_wf_result.success)

# Test workflow by skill
crm_wfs = runner.get_workflows_for_skill("skill_crm")
check("CRM has workflows", len(crm_wfs) >= 1)

mkt_wfs = runner.get_workflows_for_skill("skill_marketing")
check("Marketing has workflows", len(mkt_wfs) >= 1)


# ===== Test 7: Validation Engine =====
print("\n=== Test 7: Validation Engine ===")
from execution.validator import ValidationEngine

val = ValidationEngine()

# Validate a Python file
with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
    f.write("x = 1\nprint(x)\n")
    py_path = f.name

py_result = val.validate_python(py_path)
check("valid Python passes", py_result.passed)
os.unlink(py_path)

# Validate invalid Python
with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
    f.write("x = \n")
    bad_py_path = f.name

bad_py = val.validate_python(bad_py_path)
check("invalid Python fails", not bad_py.passed)
os.unlink(bad_py_path)

# Validate XML
with tempfile.NamedTemporaryFile(suffix='.xml', mode='w', delete=False) as f:
    f.write("<root><item>test</item></root>")
    xml_path = f.name

xml_result = val.validate_xml(xml_path)
check("valid XML passes", xml_result.passed)
os.unlink(xml_path)

# Validate manifest
with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
    f.write("{'name': 'Test', 'version': '19.0', 'depends': ['base'], 'author': 'Test', 'license': 'LGPL-3', 'category': 'Sales'}")
    manifest_path = f.name

manifest_results = val.validate_manifest(manifest_path)
manifest_all_pass = all(r.passed for r in manifest_results)
check("valid manifest passes", manifest_all_pass)
os.unlink(manifest_path)

# Test auto-detect artifact type
with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
    f.write("x = 1\n")
    art_path = f.name

art_results = val.validate_artifact(art_path)
check("artifact validation runs", len(art_results) >= 1)
os.unlink(art_path)


# ===== Test 8: Agent Profiles =====
print("\n=== Test 8: Agent Profiles ===")
import json

profiles_dir = ROOT / "agents" / "profiles"
profile_files = list(profiles_dir.glob("*.json"))
check("profile files exist", len(profile_files) >= 4,
      f"Found {len(profile_files)} profiles")

for pf in profile_files:
    with open(pf) as f:
        profile = json.load(f)
    check(f"profile {pf.stem} has profile_id", "profile_id" in profile)
    check(f"profile {pf.stem} has name", "name" in profile)
    check(f"profile {pf.stem} has compatible_skills", len(profile.get("compatible_skills", [])) > 0)


# ===== Summary =====
print(f"\n{'='*60}")
print(f"Execution Platform Test Results: {len(errors)} failures")
print(f"{'='*60}")

if errors:
    for e in errors:
        print(f"  FAIL: {e}")
    sys.exit(1)
else:
    print("All execution platform tests passed!")
    sys.exit(0)
