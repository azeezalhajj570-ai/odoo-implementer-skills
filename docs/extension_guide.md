# Odoo AI Knowledge Factory — Extension Guide

## 1. Overview

This guide explains how to extend the Knowledge Factory framework for new domains, new agents, new schemas, and new workflows.

## 2. Adding a New Domain

### 2.1 Prerequisites

- Odoo 19.0 source code accessible (Community, Enterprise, Custom)
- Domain knowledge base with module list
- Source budget allocation (min/max sources)

### 2.2 Steps

**Step 1: Prepare domain context**

Identify the Odoo modules for your domain. Use `manifest.py` inspection:

```bash
# Find relevant modules
grep -r "category.*:.*'Marketing'" /usr/lib/python3/dist-packages/odoo/addons/*/__manifest__.py

# Check module dependencies
python3 -c "
import json
with open('/path/to/module/__manifest__.py') as f:
    m = json.load(f)
    print('Depends:', m.get('depends', []))
    print('Category:', m.get('category'))
"
```

**Step 2: Create domain directory (optional)**

```bash
mkdir -p domains/{domain_name}
touch domains/{domain_name}/notes.md
```

**Step 3: Run the pipeline**

```bash
python3 scripts/orchestrator.py \
    --domain "My Domain" \
    --versions "19.0" \
    --depth deep \
    --audience "Target Audience"
```

**Step 4: Review QA report**

```bash
python3 scripts/qa_validator.py \
    --path output/databases/my_domain_knowledge.json
```

**Step 5: Fix any QA failures**

Review the QA report and address errors:
- Missing citations → add sources
- Broken references → fix source IDs
- Schema violations → correct structure

### 2.3 Domain Configuration File

For repeatable runs, create a domain config file:

```json
{
  "domain": "My Domain",
  "versions": ["19.0"],
  "audience": "Functional Consultants, Technical Consultants",
  "depth": "deep",
  "excluded_scope": [
    "Out of scope items"
  ],
  "source_budget": {
    "min": 25,
    "max": 80
  },
  "enterprise_path": "/path/to/enterprise",
  "community_path": "/path/to/community",
  "custom_path": "/path/to/custom"
}
```

Run with:
```bash
python3 scripts/orchestrator.py --config domains/my_domain/config.json
```

## 3. Adding a New Agent

### 3.1 When to Add a New Agent

- You need a specialized capability not covered by existing agents
- An existing phase needs parallel processing (e.g., multiple specialized researchers)
- You want to experiment with different prompt strategies

### 3.2 Steps

**Step 1: Create prompt file**

```bash
touch prompts/new_agent/new_agent_agent.yaml
```

**Step 2: Define the prompt**

```yaml
prompt_id: prompt_new_agent
agent_role: Custom Agent Role
version: "1.0"
phase: custom_phase
description: What this agent does.
model:
  preferred: gpt-4o
  min_capability: capability
system_prompt: >
  Role definition, rules, and workflow.
user_prompt_template: >
  Template with {{variables}}.
input_schema_ref: schemas/input_schema.json
output_format:
  type: json
  schema_ref: schemas/output_schema.json
guardrails:
  - rule: Never fabricate data
    action: reject
validation:
  schema_ref: schemas/output_schema.json
  checks:
    - required_field_check
```

**Step 3: Register in pipeline**

Add to `workflows/pipeline.yaml`:

```yaml
- id: phase_custom
  name: "Custom Phase"
  agents: ["new_agent"]
  depends_on: ["phase_dependency"]
  inputs:
    - name: input_data
      source: "phase_dependency.output_data"
  outputs:
    - name: output_data
      path: "output/databases/{domain}_output.json"
      schema: "schemas/output_schema.json"
  prompt: "prompts/new_agent/new_agent_agent.yaml"
```

**Step 4: Create output schema (if needed)**

```bash
touch schemas/output_schema.json
```

**Step 5: Register QA validator (if needed)**

In `scripts/qa_validator.py`:

```python
@register_validator("my_schema")
def validate_my_schema(v, data, path):
    """Validate my new schema."""
    for field in ["required_field"]:
        if field not in data:
            v._fail(f"missing_{field}", f"Missing required field: {field}")
```

## 4. Adding a New Schema

### 4.1 When to Add a New Schema

- New agent needs a specific output format
- Existing schema doesn't cover a required data structure
- You need a different validation structure

### 4.2 Steps

**Step 1: Create schema file**

```bash
touch schemas/new_schema.json
```

**Step 2: Define schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Schema Title",
  "type": "object",
  "required": ["required_field"],
  "additionalProperties": false,
  "properties": {
    "required_field": {
      "type": "string",
      "description": "Description of the field"
    },
    "optional_field": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

**Step 3: Update prompt to reference schema**

**Step 4: Register in orchestrator (if schema needs special handling)**

## 5. Adding a New Workflow

### 5.1 When to Add a New Workflow

- You need a different combination of phases
- You want a simplified pipeline for specific tasks
- You need a custom execution order

### 5.2 Steps

**Step 1: Create workflow file**

```bash
touch workflows/custom_workflow.yaml
```

**Step 2: Define workflow**

```yaml
workflow:
  name: "Custom Workflow"
  version: "1.0"
  phases:
    - id: phase_one
      name: "Phase One"
      agents: ["agent_one"]
      prompt: "prompts/agent_one/agent_one.yaml"
      inputs: [...]
      outputs: [...]
    - id: phase_two
      name: "Phase Two"
      agents: ["agent_two"]
      depends_on: ["phase_one"]
      prompt: "prompts/agent_two/agent_two.yaml"
      inputs: [...]
      outputs: [...]
```

**Step 3: Add workflow loader to orchestrator**

In `orchestrator.py`:

```python
def load_workflow(self, workflow_name):
    path = ROOT / "workflows" / f"{workflow_name}.yaml"
    return load_yaml(str(path))
```

## 6. Extending the QA Validator

### 6.1 Adding a New Check

In `scripts/qa_validator.py`:

```python
def _check_cross_cutting(self, data: dict, path: Path):
    """Add custom cross-cutting check."""
    super()._check_cross_cutting(data, path)  # if inheriting
    
    # Custom check example:
    if "domain" in data and data["domain"] != "Accounting":
        self._warn("domain_mismatch", 
                    f"Domain '{data.get('domain')}' does not match expected domain")
```

### 6.2 Adding a New Validator

```python
@register_validator("new_schema")
def validate_new_schema(v, data, path):
    """Validate new schema artifacts."""
    # Check required fields
    for field in ["field_a", "field_b"]:
        if field not in data:
            v._fail(f"missing_{field}", f"Missing: {field}")
    
    # Check cross-references
    if "ref_ids" in data:
        for ref in data["ref_ids"]:
            if not ref.startswith("ref_"):
                v._warn(f"invalid_ref_{ref}", f"Ref should start with 'ref_': {ref}")
```

## 7. Customizing Output Templates

### 7.1 Template Variables

Templates use Jinja2-style variables:

```markdown
# {{domain}} Knowledge Base
Generated: {{generated_at}}
```

### 7.2 Adding a New Template

```bash
touch templates/custom/custom_template.md
```

Reference in agent config:

```yaml
output_format:
  type: markdown
  template: "templates/custom/custom_template.md"
```

## 8. Integration with External Systems

### 8.1 CI/CD Integration

Run QA validation in CI:

```bash
python3 scripts/qa_validator.py --all --domain crm
if [ $? -ne 0 ]; then
    echo "QA validation failed"
    exit 1
fi
```

### 8.2 RAG Indexing Pipeline

After Phase 6, feed `output/databases/*_rag_metadata.json` into your vector database:

```python
# Pseudocode for RAG ingestion
for domain in domains:
    metadata = json.load(open(f"output/databases/{domain}_rag_metadata.json"))
    for chunk in metadata["chunking"]["chunks"]:
        vector_db.upsert(
            id=chunk["chunk_id"],
            vector=get_embedding(chunk["content"]),
            metadata={
                "domain": metadata["domain"],
                "section": chunk["section_id"],
                "source": chunk.get("source_id"),
            }
        )
```

### 8.3 API Integration

Expose the orchestrator via a REST API:

```python
@app.post("/knowledge-factory/run")
def run_pipeline(domain: str, versions: list, depth: str = "deep"):
    config = {"domain": domain, "versions": versions, "depth": depth}
    orch = PipelineOrchestrator(config)
    orch.run()
    return {"status": "completed", "artifacts": orch.artifacts}
```
