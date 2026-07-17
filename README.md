# Odoo AI Knowledge Factory

A production-grade framework for generating reusable AI Skills for every Odoo Enterprise domain. The Knowledge Factory researches, analyzes, documents, validates, and packages expert-level domain knowledge into machine-readable artifacts optimized for AI consumption.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Odoo AI Knowledge Factory                  │
├──────────┬──────────┬──────────┬──────────┬──────────┬───────┤
│  Phase 1 │  Phase 2 │  Phase 3 │  Phase 4 │  Phase 5 │Phase 6│
│  Domain  │  Source  │ Business │   AI     │   AI     │ Knowl.│
│ Research │  Code    │ Process  │Intell.   │  Skill   │Package│
│          │  Intell. │          │          │  Gen.    │       │
├──────────┴──────────┴──────────┴──────────┴──────────┴───────┤
│                    Phase 7: Quality Assurance                  │
├─────────────────────────────────────────────────────────────┤
│    Output: Canonical JSON + Markdown + Diagrams + RAG Index   │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Full Pipeline Run

```bash
# Research a complete domain
python3 scripts/orchestrator.py \
    --domain "CRM" \
    --versions "19.0" \
    --depth deep \
    --audience "Odoo Functional Consultants, AI Engineers"
```

### Single Phase

```bash
# Run only the source code intelligence phase
python3 scripts/orchestrator.py \
    --domain "CRM" \
    --single-phase phase_2_source_code
```

### QA Validation

```bash
# Validate existing artifacts
python3 scripts/qa_validator.py --path output/databases/crm_knowledge.json

# Validate all artifacts for a domain
python3 scripts/qa_validator.py --all --domain crm --output output/reports/crm_qa.json
```

## Repository Structure

```
knowledge-factory/
├── prompts/                    # Agent prompt configurations (YAML)
│   ├── domain_research/        # Phase 1: Domain Research Agent
│   ├── source_discovery/       # Phase 2: Source Discovery Agent
│   ├── source_verification/    # Phase 2: Source Verification Agent
│   ├── source_code_analysis/   # Phase 3: Source Code Analysis Agent
│   ├── business_process/       # Phase 4: Business Process Agent
│   ├── ai_integration/         # Phase 5: AI Integration Agent
│   ├── skill_generator/        # Phase 6: AI Skill Generator
│   ├── documentation_generator/# Phase 6: Documentation Generator
│   ├── json_generator/         # Phase 6: JSON Generator
│   ├── knowledge_graph_generator/ # Phase 6: Knowledge Graph Generator
│   ├── qa_agent/               # Phase 7: QA Agent
│   └── rag_packaging/          # Phase 7: RAG Packaging Agent
├── schemas/                    # JSON Schemas for all artifacts
│   ├── knowledge_base.json     # Domain Knowledge Base schema
│   ├── source_registry.json    # Source Registry schema
│   ├── module_catalog.json     # Module Catalog schema
│   ├── model_catalog.json      # Model Catalog schema
│   ├── skill_definition.json   # AI Skill Definition schema
│   ├── prompt_configuration.json   # Prompt Configuration schema
│   ├── validation_report.json  # QA Validation Report schema
│   └── metadata.json           # RAG Metadata schema
├── workflows/                  # Pipeline orchestration definitions
│   ├── pipeline.yaml           # Full 7-phase pipeline
│   ├── single_skill.yaml       # Single skill generation
│   └── qa_pipeline.yaml        # Standalone QA pipeline
├── templates/                  # Output templates
│   ├── knowledge_base/         # Knowledge Base Markdown template
│   ├── implementation_guide/   # Implementation Guide template
│   ├── skill/                   # Skill Definition template
│   └── report/                  # Report template
├── scripts/                    # Automation scripts
│   ├── orchestrator.py         # Pipeline orchestrator
│   └── qa_validator.py         # QA validation tool
├── skills/                     # Generated AI Skills (per domain)
├── output/                     # Pipeline output
│   ├── databases/              # Machine-readable JSON artifacts
│   ├── logs/                   # Execution logs
│   └── reports/                # Human-readable documentation
├── domains/                    # Domain-specific references
│   └── references/             # Cross-domain reference material
├── docs/                       # Framework documentation
│   └── images/                 # Architecture diagrams
├── examples/                   # Example outputs for sample domains
│   ├── accounting/
│   ├── crm/
│   └── inventory/
├── tests/                      # Test suite
│   ├── fixtures/               # Test data fixtures
│   ├── test_output/            # Test-generated output
│   ├── test_schema_validity.py # Schema validation tests
│   ├── test_orchestrator.py    # Orchestrator tests
│   ├── test_qa_validator.py    # QA validator tests
│   └── run_all.sh              # Test runner
└── README.md                   # This file
```

## Seven-Phase Pipeline

### Phase 1 — Domain Research
Research a domain from authoritative sources. Scoped research brief → source discovery → claim extraction → synthesis → verification → packaging.

### Phase 2 — Source Code Intelligence
Analyze actual Odoo source code (Community, Enterprise, Custom). Manifest analysis, model/field/method catalog, security audit, view/controller/report analysis, extension points.

### Phase 3 — Business Intelligence
Extract business processes, functional workflows, implementation patterns, and industry best practices from domain + code analysis.

### Phase 4 — AI Intelligence
Identify where AI enhances Odoo (assistants, agents, RAG, scoring, content generation, workflow automation, recommendation). Document implementation approaches.

### Phase 5 — AI Skill Generator
Generate production-ready AI Skills with purpose, scope, inputs/outputs, prompt templates, validation rules, and troubleshooting guides.

### Phase 6 — Knowledge Packaging
Canonical JSON, Markdown docs, Mermaid diagrams, search index, cross-references, RAG metadata, chunking, embeddings.

### Phase 7 — Quality Assurance
Automated validation: broken references, missing citations, contradictions, hallucination risk, schema compliance, cross-reference integrity.

## Design Principles

- **Modular** — Each component can be used independently
- **Extensible** — Add new domains with minimal effort
- **Version-aware** — Support multiple Odoo versions
- **Source-driven** — Every claim cites its origin
- **Citation-first** — Non-negotiable traceability
- **AI-friendly** — Optimized for AI consumption
- **RAG-ready** — Chunked, embedded, indexed
- **Machine-readable** — JSON schema-validated artifacts
- **Human-readable** — Clear Markdown documentation
- **Production-ready** — Tested, validated, maintainable

## License

This framework is designed for use with Odoo Enterprise under the applicable Odoo Enterprise License. Component licenses vary (LGPL-3 for community code, OEEL-1 for Enterprise code, OPL-1 for proprietary modules).
