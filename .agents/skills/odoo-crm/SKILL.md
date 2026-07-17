# Skill: odoo-crm

Odoo CRM Expert — Expert-level knowledge of Odoo CRM including predictive lead scoring (Naive Bayes), lead mining, lead enrichment, partner autocomplete, pipeline management, sales automation, and marketing attribution. Use when the user asks about Predictive Lead Scoring, IAP Lead Mining, IAP Lead Enrichment, Partner Autocomplete, Pipeline Design in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/crm/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/crm/skill.json` — metadata, modules, dependencies
   - `skills/crm/capability.json` — detailed capability definitions
   - `skills/crm/knowledge.json` — key models, files, crons, security groups
   - `skills/crm/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Predictive Lead Scoring** (`cap_lead_scoring`): Naive Bayes ML model trained on historical conversion data. Configure PLS variables, rebuild frequency tables, interpret probability scores. Formula: P(Won|values) ∝ ∏ P(value|Won)×P(Won). Batch compute step=50000, update step=5000.
- **IAP Lead Mining** (`cap_lead_mining`): Generate leads from external B2B database via DnB API. Filter by country, industry, company size, role, seniority. 1 credit/lead + 1/contact. Endpoint: /api/dnb/1/search_by_criteria.
- **IAP Lead Enrichment** (`cap_lead_enrichment`): Enrich leads with business data via Clearbit API. Auto-enrich on create or manual per-lead. 1 credit/enrichment. Skips generic email providers.
- **Partner Autocomplete** (`cap_partner_autocomplete`): Auto-populate company info via DnB. Works on new company contacts only. Endpoints: search_by_name, search_by_vat, enrich_by_duns, enrich_by_domain.
- **Pipeline Design** (`cap_pipeline`): Multi-stage pipeline with kanban stages, probability tracking, won/lost lifecycle. Stage configuration with rotting thresholds, team-based stages.
- **Lead Auto-Assignment** (`cap_lead_assignment`): Weighted random allocation to teams, round-robin to members with preference domains. Daily quota = assignment_max/30 - lead_day_count. Configurable cron.
- **Opportunity Management** (`cap_opportunity`): Lead-to-opportunity conversion, merge, recurring revenue tracking, expected revenue, prorated MRR.
- **Marketing Attribution** (`cap_marketing_attribution`): UTM-based campaign/source/medium tracking via utm.mixin. Last-touch attribution model. Campaign IDs, source IDs, medium IDs on every lead.
- **Sales Team Management** (`cap_team_management`): Team configuration, member assignment rules, dashboard KPIs, forecast reporting.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- PLS requires sufficient historical won/lost data for meaningful probabilities
- IAP services require purchased credit packs
- Marketing attribution is last-touch only; no multi-touch models

## Context

- **Domain:** Sales
- **Subdomain:** CRM
- **Skill ID:** skill_crm
- **Knowledge package:** `skills/crm/`

- **Required modules:** crm
- **Optional modules:** crm_iap_mine, crm_iap_enrich, partner_autocomplete

- **Depends on skills:** skill_base, skill_mail
- **Relevant modules:** crm, sales_team, utm, phone_validation
