# Skill: odoo-development

Odoo Development Expert — Expert-level knowledge of Odoo 19 module development including __manifest__.py, models, views, controllers, OWL components, QWeb reports, RPC, testing, debugging, and linting. Use when the user asks about Module Structure, Model Development, XML Views, HTTP Controllers, OWL Components in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/development/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/development/skill.json` — metadata, modules, dependencies
   - `skills/development/capability.json` — detailed capability definitions
   - `skills/development/knowledge.json` — key models, files, crons, security groups
   - `skills/development/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Module Structure** (`cap_module_structure`): Create Odoo 19 modules with __manifest__.py, __init__.py, data files, models, views, controllers, security, and static assets. Follow directory conventions and naming standards.
- **Model Development** (`cap_models`): Define models, fields, inheritance, computed fields, constraints, onchange, defaults, and ORM methods. Use Odoo 19 decorators and patterns.
- **XML Views** (`cap_views`): Build form, tree, kanban, search, graph, pivot, calendar, and activity views with inheritance, xpath, and Odoo 19 view syntax.
- **HTTP Controllers** (`cap_controllers`): Implement Odoo 19 controllers with @route decorators, auth types, CSRF tokens, JSON endpoints, and public pages.
- **OWL Components** (`cap_owl_components`): Develop Odoo 19 OWL components, hooks, services, templates, and client actions. Use lifecycle methods, props, and reactive state.
- **QWeb Reports** (`cap_reports`): Create PDF/HTML reports using QWeb, ir.actions.report, paper formats, barcodes, and report templates in Odoo 19.
- **RPC & API** (`cap_rpc`): Use external API (XML-RPC, JSON-RPC), ORM methods, controllers, and OWL rpc service for data exchange with Odoo 19.
- **Testing & Debugging** (`cap_testing`): Write Odoo 19 tests with TransactionCase, HttpCase, @tagged, mocks, and query count assertions. Use PDB, logging, and the Odoo shell.
- **Linting & Quality** (`cap_linting`): Apply linting with flake8, pylint, black, pre-commit hooks, and Odoo 19 coding standards for Python and XML.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Development guidance assumes Odoo 19 syntax and patterns; older versions may differ
- Complex OWL scenarios may require specific frontend architecture decisions
- Performance optimization requires separate profiling and query analysis

## Context

- **Domain:** Development
- **Subdomain:** Module Development
- **Skill ID:** skill_development
- **Knowledge package:** `skills/development/`

- **Required modules:** base, web
- **Optional modules:** mail

- **Depends on skills:** skill_base
- **Relevant modules:** base, web, mail
