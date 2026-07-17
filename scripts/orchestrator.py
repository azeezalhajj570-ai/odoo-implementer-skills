#!/usr/bin/env python3
"""
Odoo Knowledge Factory — Pipeline Orchestrator

Orchestrates the 7-phase pipeline for any Odoo domain.
Supports full runs, incremental runs, single-phase runs, and QA-only runs.

Usage:
    python3 orchestrator.py --domain "Accounting" --versions "19.0" --depth deep
    python3 orchestrator.py --domain "CRM" --single-phase phase_2_source_code
    python3 orchestrator.py --qa-only --domain "Inventory"
"""

import argparse
import json
import logging
import os
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


class PipelineOrchestrator:
    """Orchestrates the Knowledge Factory pipeline for a domain."""

    def __init__(self, config: dict):
        self.config = config
        self.domain = config["domain"]
        self.versions = config.get("versions", ["19.0"])
        self.audience = config.get("audience", "Odoo Consultants")
        self.depth = config.get("depth", "standard")
        self.source_budget = config.get("source_budget", {"min": 25, "max": 80})
        self.pipeline_def = load_yaml(str(ROOT / "workflows" / "pipeline.yaml"))
        self.artifacts: Dict[str, str] = {}
        self.status: Dict[str, str] = {}

    def run(self, single_phase: Optional[str] = None):
        """Execute the pipeline, optionally limiting to one phase."""
        phases = self.pipeline_def["pipeline"]["phases"]
        
        for phase in phases:
            phase_id = phase["id"]
            
            if single_phase and phase_id != single_phase:
                logger.info(f"Skipping phase {phase_id} (single-phase mode)")
                self.status[phase_id] = "skipped"
                continue

            if single_phase is None:
                deps = phase.get("depends_on", [])
                missing_deps = [d for d in deps if self.status.get(d) != "completed"]
                if missing_deps:
                    logger.error(f"Cannot run {phase_id}: missing dependencies {missing_deps}")
                    self.status[phase_id] = "blocked"
                    continue

            logger.info(f"=== Running Phase: {phase['name']} ({phase_id}) ===")
            
            try:
                self._execute_phase(phase)
                self.status[phase_id] = "completed"
            except Exception as e:
                logger.error(f"Phase {phase_id} failed: {e}")
                self.status[phase_id] = "failed"
                if phase.get("error_handling", [{}])[0].get("action") != "skip_and_continue":
                    break

        self._print_summary()

    def _execute_phase(self, phase: dict):
        """Execute a single phase by dispatching to the appropriate agent."""
        phase_id = phase["id"]
        agent_config = self._load_agent_config(phase)
        inputs = self._resolve_inputs(phase)
        outputs = phase.get("outputs", [])

        # Build the agent prompt from inputs + config
        prompt = self._build_prompt(agent_config, inputs)
        
        # In a production system, this would call an LLM or agent API.
        # For now, we log the prompt and simulate artifact generation.
        logger.info(f"Agent prompt prepared for {phase_id}")
        logger.debug(f"Prompt preview: {prompt[:500]}...")

        # Simulate output artifact generation
        for output in outputs:
            output_path = self._resolve_output_path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            artifact = self._generate_placeholder_artifact(output, phase_id)
            with open(output_path, "w") as f:
                json.dump(artifact, f, indent=2)
            
            self.artifacts[output.get("name", output_path.stem)] = str(output_path)
            logger.info(f"Generated {output_path}")

    def _load_agent_config(self, phase: dict) -> dict:
        """Load the agent prompt configuration YAML."""
        prompt_path = phase.get("prompt")
        if not prompt_path:
            prompts = phase.get("prompts", {})
            prompt_path = next(iter(prompts.values())) if prompts else None
        
        if prompt_path:
            return load_yaml(str(ROOT / prompt_path))
        return {}

    def _resolve_inputs(self, phase: dict) -> dict:
        """Resolve phase inputs from previous phase outputs and user config."""
        inputs = {}
        phase_inputs = phase.get("inputs", [])
        for inp in phase_inputs:
            name = inp["name"]
            source = inp.get("source", "user")
            
            if source == "user":
                inputs[name] = self.config.get(name)
            elif source.startswith("phase_"):
                # Reference to previous phase's output
                ref = source.split(".")[-1] if "." in source else name
                inputs[name] = self.artifacts.get(ref)
            elif source == "file":
                inputs[name] = None  # Would be resolved from config
            else:
                inputs[name] = None
        
        # Add standard context
        inputs["domain_name"] = self.domain
        inputs["version_list"] = json.dumps(self.versions)
        inputs["version"] = self.versions[0] if self.versions else "19.0"
        inputs["audience"] = self.audience
        inputs["depth"] = self.depth
        inputs["min_sources"] = self.source_budget["min"]
        inputs["max_sources"] = self.source_budget["max"]
        
        return inputs

    def _build_prompt(self, agent_config: dict, inputs: dict) -> str:
        """Build the full prompt by filling the template with resolved inputs."""
        template = agent_config.get("user_prompt_template", "")
        if not template:
            return json.dumps(inputs, indent=2)
        
        # Simple Jinja-style template substitution
        import re
        def replace_var(match):
            var_name = match.group(1)
            value = inputs.get(var_name, f"{{{{{var_name}}}}}")
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            return str(value) if value is not None else ""
        
        return re.sub(r"\{\{(\w+)\}\}", replace_var, template)

    def _resolve_output_path(self, output: dict) -> Path:
        """Resolve output path template with domain name."""
        path_template = output.get("path", "")
        path_str = path_template.format(domain=self.domain.lower().replace(" ", "_"))
        return ROOT / path_str

    def _generate_placeholder_artifact(self, output: dict, phase_id: str) -> dict:
        """Generate a placeholder artifact structure for the output."""
        return {
            "artifact": output.get("name", "unknown"),
            "phase": phase_id,
            "domain": self.domain,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "placeholder",
            "note": "Replace with actual agent output in production"
        }

    def _print_summary(self):
        """Print execution summary."""
        print("\n" + "=" * 60)
        print("Pipeline Execution Summary")
        print("=" * 60)
        for phase_id, status in self.status.items():
            print(f"  {phase_id}: {status.upper()}")
        print(f"\nArtifacts generated: {len(self.artifacts)}")
        for name, path in self.artifacts.items():
            print(f"  {name}: {path}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Odoo Knowledge Factory Orchestrator")
    parser.add_argument("--domain", required=True, help="Odoo domain to research")
    parser.add_argument("--versions", default="19.0", help="Comma-separated Odoo versions")
    parser.add_argument("--audience", default="Odoo Functional Consultants", help="Target audience")
    parser.add_argument("--depth", default="deep", choices=["overview", "standard", "deep"])
    parser.add_argument("--single-phase", help="Run only this phase")
    parser.add_argument("--qa-only", action="store_true", help="Run QA only on existing artifacts")
    parser.add_argument("--config", help="Path to JSON config file")
    
    args = parser.parse_args()
    
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = {
            "domain": args.domain,
            "versions": args.versions.split(","),
            "audience": args.audience,
            "depth": args.depth,
        }
    
    orchestrator = PipelineOrchestrator(config)
    
    if args.qa_only:
        orchestrator.run(single_phase="phase_7_qa")
    else:
        orchestrator.run(single_phase=args.single_phase)


if __name__ == "__main__":
    main()
