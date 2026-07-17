# Skill: odoo-security

Odoo Security Expert — Expert-level knowledge of Odoo security including access rights, record rules, groups, model access, field permissions, OWL security, XSS/CSRF protection, secure coding, GDPR/privacy, and audit trails. Use when the user asks about Access Rights, Record Rules, Field Permissions, Group Design, OWL Security in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/security/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/security/skill.json` — metadata, modules, dependencies
   - `skills/security/capability.json` — detailed capability definitions
   - `skills/security/knowledge.json` — key models, files, crons, security groups
   - `skills/security/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Access Rights** (`cap_access_rights`): Design and implement ACL groups (ir.model.access), model-level permissions (create/read/write/unlink), and group hierarchies with implied groups.
- **Record Rules** (`cap_record_rules`): Define domain-based record rules (ir.rule) for multi-company, multi-department, and ownership-based data isolation. Apply global and per-user rules.
- **Field Permissions** (`cap_field_permissions`): Apply field-level security using groups= on fields, readonly attributes, and computed restricted fields. Use ir.model.fields access restrictions.
- **Group Design** (`cap_group_design`): Create security groups, categories, implied groups, and role-based access control. Map business roles to Odoo groups.
- **OWL Security** (`cap_owl_security`): Handle OWL component security, RPC access control, user context, and client-side validation in Odoo 19 web framework.
- **Web Vulnerabilities** (`cap_web_vulnerabilities`): Prevent XSS, CSRF, SQL injection, and unsafe eval. Use Markup, out-escaping, and proper controller decorators in Odoo 19.
- **Secure Coding** (`cap_secure_coding`): Apply secure coding practices: avoid SQL injection, sanitize inputs, use sudo correctly, validate RPC calls, and protect sensitive data.
- **GDPR & Privacy** (`cap_gdpr_privacy`): Implement GDPR/privacy controls: data retention, right to erasure, privacy lookup, anonymization, consent tracking, and lawful basis.
- **Audit & Logging** (`cap_audit_logging`): Configure audit trails, field tracking, log access, record change tracking, and security event monitoring in Odoo.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Record rules apply only at ORM level; raw SQL bypasses them
- Field-level groups can be circumvented by determined users via RPC
- Client-side security in OWL is not a substitute for server-side enforcement
- GDPR compliance requires legal process design beyond technical controls

## Context

- **Domain:** Security
- **Subdomain:** Access Control
- **Skill ID:** skill_security
- **Knowledge package:** `skills/security/`

- **Required modules:** base, web
- **Optional modules:** privacy_lookup

- **Depends on skills:** skill_base
- **Relevant modules:** base, web, mail
