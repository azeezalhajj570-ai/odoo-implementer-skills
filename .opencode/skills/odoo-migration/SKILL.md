---
name: odoo-migration
description: Use when the user asks about Odoo Migration Expert topics such as Version Upgrade Planning, Migration Scripts, Data Migration in Odoo 19. Loads knowledge from skills/migration/.
---

# Skill: odoo-migration

Odoo Migration Expert — Expert-level knowledge of Odoo version upgrades, migration scripts (pre/post/end), data migration, compatibility analysis, staging testing, rollback strategies, Odoo upgrade service, and OCA migration tools. Use when the user asks about Version Upgrade Planning, Migration Scripts, Data Migration, Compatibility Analysis, Staging Testing in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/migration/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/migration/skill.json` — metadata, modules, dependencies
   - `skills/migration/capability.json` — detailed capability definitions
   - `skills/migration/knowledge.json` — key models, files, crons, security groups
   - `skills/migration/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Version Upgrade Planning** (`cap_version_upgrade`): Assess upgrade path from source Odoo version to 19.0, identify breaking changes, deprecations, and module compatibility. Build phased upgrade plan with cutover strategy.
- **Migration Scripts** (`cap_migration_scripts`): Write pre-migration, post-migration, and end-migration scripts. Use env.cr.execute, env.ref, openupgradelib helpers, and versioned upgrade directories.
- **Data Migration** (`cap_data_migration`): Migrate master data, transactions, attachments, and configurations across versions using ORM, SQL, ETL patterns, and external_id preservation.
- **Compatibility Analysis** (`cap_compatibility_analysis`): Analyze custom modules, third-party apps, and OCA modules for API compatibility with Odoo 19. Detect removed fields, changed signatures, and ORM behavior changes.
- **Staging Testing** (`cap_staging_testing`): Design staging environment, smoke tests, regression tests, and parallel reconciliation procedures before production cutover.
- **Rollback Strategy** (`cap_rollback_strategy`): Define rollback points, database snapshots, backup procedures, and blue/green cutover strategies for failed upgrades.
- **Odoo Upgrade Service** (`cap_odoo_upgrade_service`): Use Odoo SA online upgrade service, test database migration, migration scripts delivery, and validation reports.
- **OCA Migration** (`cap_oca_migration`): Use OpenUpgrade framework, openupgradelib helpers, and OCA migration scripts for community and OCA modules.
- **Post-Migration Validation** (`cap_post_migration`): Run post-upgrade checks: reconcile balances, validate workflows, check user permissions, audit logs, and performance baseline.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Migration complexity depends on custom module count and data volume
- Odoo Upgrade Service requires a valid enterprise contract for some versions
- OpenUpgrade coverage varies by module; unsupported modules require custom scripts
- Rollback after production cutover may cause data loss depending on timing

## Context

- **Domain:** Migration
- **Subdomain:** Version Upgrades
- **Skill ID:** skill_migration
- **Knowledge package:** `skills/migration/`

- **Required modules:** base
- **Optional modules:** upgrade, openupgrade

- **Depends on skills:** skill_base
- **Relevant modules:** base, web
