#!/usr/bin/env python3
"""
Tests: Orchestrator Functionality

Verifies the pipeline orchestrator can:
1. Load pipeline configuration
2. Build prompts from templates
3. Resolve phase inputs correctly
4. Handle single-phase mode
5. Handle error cases
"""

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

errors = []
warnings = []

# --- Test 1: Import orchestrator ---
print("\n=== Test 1: Import Orchestrator ===")
try:
    from orchestrator import PipelineOrchestrator
    print("  PASS: Import successful")
except ImportError as e:
    print(f"  FAIL: Import failed: {e}")
    errors.append("orchestrator_import")
    sys.exit(1)

# --- Test 2: Load pipeline YAML ---
print("\n=== Test 2: Load Pipeline Definition ===")
try:
    import yaml
    pipeline_path = ROOT / "workflows" / "pipeline.yaml"
    with open(pipeline_path) as f:
        pipeline = yaml.safe_load(f)
    assert "pipeline" in pipeline
    phases = pipeline["pipeline"]["phases"]
    assert len(phases) >= 5
    print(f"  PASS: Pipeline has {len(phases)} phases")
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append("pipeline_load")

# --- Test 3: Create orchestrator ---
print("\n=== Test 3: Create Orchestrator ===")
try:
    config = {
        "domain": "Test Domain",
        "versions": ["19.0"],
        "audience": "Test Audience",
        "depth": "deep",
        "source_budget": {"min": 10, "max": 30},
    }
    orch = PipelineOrchestrator(config)
    print(f"  PASS: Orchestrator created for {orch.domain}")
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append("orchestrator_create")

# --- Test 4: Build prompt ---
print("\n=== Test 4: Build Prompt ===")
try:
    agent_config = {
        "user_prompt_template": "Domain: {{domain_name}}, Version: {{version}}"
    }
    inputs = {"domain_name": "CRM", "version": "19.0"}
    prompt = orch._build_prompt(agent_config, inputs)
    expected = "Domain: CRM, Version: 19.0"
    assert prompt == expected, f"Expected '{expected}', got '{prompt}'"
    print(f"  PASS: Template substitution works: '{prompt}'")
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append("prompt_build")

# --- Test 5: Resolve input paths ---
print("\n=== Test 5: Resolve Output Paths ===")
try:
    test_output = {"path": "output/databases/{domain}_test.json"}
    resolved = orch._resolve_output_path(test_output)
    assert "test_domain" in str(resolved).lower()
    print(f"  PASS: Path resolved to {resolved.name}")
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append("path_resolution")

# --- Test 6: Single-phase run ---
print("\n=== Test 6: Single-Phase Run ===")
try:
    orch.run(single_phase="phase_1_domain_research")
    assert "phase_1_domain_research" in orch.status
    print(f"  PASS: Single-phase execution completed")
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append("single_phase_run")

# --- Test 7: Artifact generation ---
print("\n=== Test 7: Artifact Generation ===")
try:
    assert len(orch.artifacts) > 0
    print(f"  PASS: {len(orch.artifacts)} artifacts generated")
    for name, path in orch.artifacts.items():
        assert Path(path).exists(), f"Artifact not found: {path}"
        print(f"    {name}: {path}")
except Exception as e:
    print(f"  FAIL: {e}")
    errors.append("artifact_generation")


# --- Summary ---
print(f"\n{'='*60}")
print(f"Results: {len(errors)} failures")
print(f"{'='*60}")

if errors:
    for e in errors:
        print(f"  FAIL: {e}")
    sys.exit(1)
else:
    print("All tests passed!")
    sys.exit(0)
