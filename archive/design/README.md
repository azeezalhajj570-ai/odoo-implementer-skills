# Archived Design Components

This directory contains the intended architecture for Layers 3–6 of the Odoo AI Knowledge Factory.

These modules are **not production-ready**. They are kept as reference and design artifacts for future implementation.

## Contents

| Component | Original Path | Status |
|-----------|--------------|--------|
| Multi-Agent Coordinator | `coordinator/` | Stub — dataclass assignments, no execution |
| Execution Engine | `execution/engine.py` | Stub — sequential step runner, no real backend |
| Workflow Runner | `execution/workflow_runner.py` | Stub — iterates JSON playbooks |
| Experience Memory | `memory/` | JSON file storage, keyword matching |
| Self-Correction | `memory/self_correction.py` | Rule-based retry patterns |
| OAIOS | `oaios/` | Data models and hardcoded templates |
| Plugins | `plugins/` | Dynamic loader with no sandboxing |
| Project Context | `project/` | Directory scanner, no real integration |
| Reasoning | `reasoning/` | Keyword/template engines, not real AI |
| Reports | `reports/` | Markdown formatter |

## How to restore

To restore any component to the active tree:

1. Move the directory/file back to its original location.
2. Re-implement the stub logic against real systems.
3. Add production tests.
4. Update `__init__.py` files as needed.
