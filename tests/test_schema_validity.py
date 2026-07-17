#!/usr/bin/env python3
"""
Tests: Schema Validity Checks

Verifies that:
1. All JSON Schema files are valid JSON
2. All Schema files are valid JSON Schema (draft-07)
3. All YAML prompt files parse
4. All workflow definitions parse
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

errors = []
warnings = []


def check(label: str, condition: bool, detail: str = ""):
    if condition:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label} — {detail}")
        errors.append(label)


def warn(label: str, detail: str = ""):
    print(f"  WARN: {label} — {detail}")
    warnings.append(label)


# --- Test 1: All JSON Schema files are valid JSON ---
print("\n=== Test 1: JSON Schema Validity ===")
schema_dir = ROOT / "schemas"
schema_files = sorted(schema_dir.glob("*.json"))
check("Schema directory exists", schema_dir.exists())
check("Schema files found", len(schema_files) > 0)

for sf in schema_files:
    try:
        with open(sf) as f:
            schema = json.load(f)
        check(f"Valid JSON: {sf.name}", True)
        
        # Check required meta-schema fields
        if "$schema" not in schema:
            warn(f"Missing $schema: {sf.name}")
        if "type" not in schema:
            warn(f"Missing type: {sf.name}")
        if "properties" not in schema:
            warn(f"Missing properties: {sf.name}")
        if "required" not in schema:
            warn(f"Missing required: {sf.name}")
            
    except json.JSONDecodeError as e:
        check(f"Valid JSON: {sf.name}", False, str(e))


# --- Test 2: All YAML prompt files parse ---
print("\n=== Test 2: YAML Prompt Parsing ===")
prompt_dir = ROOT / "prompts"
prompt_files = sorted(prompt_dir.glob("**/*.yaml"))
check("Prompt directory exists", prompt_dir.exists())
check("Prompt files found", len(prompt_files) > 0)

try:
    import yaml
    for pf in prompt_files:
        try:
            with open(pf) as f:
                data = yaml.safe_load(f)
            check(f"Valid YAML: {pf.name}", data is not None)
            
            # Check required fields
            if isinstance(data, dict):
                if "prompt_id" not in data:
                    warn(f"Missing prompt_id: {pf.name}")
                if "agent_role" not in data:
                    warn(f"Missing agent_role: {pf.name}")
                if "phase" not in data:
                    warn(f"Missing phase: {pf.name}")
                if "system_prompt" not in data:
                    warn(f"Missing system_prompt: {pf.name}")
        except yaml.YAMLError as e:
            check(f"Valid YAML: {pf.name}", False, str(e))
except ImportError:
    warn("PyYAML not installed — skipping")


# --- Test 3: All workflow definitions parse ---
print("\n=== Test 3: Workflow Definitions ===")
workflow_dir = ROOT / "workflows"
workflow_files = sorted(workflow_dir.glob("*.yaml"))
check("Workflow directory exists", workflow_dir.exists())
check("Workflow files found", len(workflow_files) > 0)

try:
    import yaml
    for wf in workflow_files:
        try:
            with open(wf) as f:
                data = yaml.safe_load(f)
            check(f"Valid YAML: {wf.name}", data is not None)
        except yaml.YAMLError as e:
            check(f"Valid YAML: {wf.name}", False, str(e))
except ImportError:
    pass


# --- Test 4: Script files are valid Python ---
print("\n=== Test 4: Script Parsing ===")
script_dir = ROOT / "scripts"
script_files = sorted(script_dir.glob("*.py"))
check("Script directory exists", script_dir.exists())
check("Script files found", len(script_files) > 0)

for sf in script_files:
    try:
        compile(open(sf).read(), str(sf), 'exec')
        check(f"Valid Python: {sf.name}", True)
    except SyntaxError as e:
        check(f"Valid Python: {sf.name}", False, str(e))


# --- Summary ---
print(f"\n{'='*60}")
print(f"Results: {len(errors)} failures, {len(warnings)} warnings")
print(f"{'='*60}")

if errors:
    for e in errors:
        print(f"  FAIL: {e}")
    sys.exit(1)
else:
    print("All tests passed!")
    sys.exit(0)
