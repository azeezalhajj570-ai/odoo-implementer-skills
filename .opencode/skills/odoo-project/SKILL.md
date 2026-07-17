---
name: odoo-project
description: Use when the user asks about Odoo Project Expert topics such as Project Setup & Configuration, Task Lifecycle Management, Timesheet Tracking in Odoo 19. Loads knowledge from skills/project/.
---

# Skill: odoo-project

Odoo Project Expert — Expert-level knowledge of Odoo Project and Task management including project planning, task lifecycle, kanban stages, timesheets, forecasting, resource allocation, and project profitability. Use when the user asks about Project Setup & Configuration, Task Lifecycle Management, Timesheet Tracking, Project Planning & Scheduling, Resource Allocation in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/project/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/project/skill.json` — metadata, modules, dependencies
   - `skills/project/capability.json` — detailed capability definitions
   - `skills/project/knowledge.json` — key models, files, crons, security groups
   - `skills/project/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Project Setup & Configuration** (`cap_project_setup`): Create and configure projects with visibility (portal, employees, followers), stages, tags, analytic accounts, and collaboration settings.
- **Task Lifecycle Management** (`cap_task_lifecycle`): Manage task creation, assignment, priorities, kanban states (normal, done, blocked), deadlines, and stage transitions with mail.activity integration.
- **Timesheet Tracking** (`cap_timesheets`): Record and validate timesheets via account.analytic.line linked to hr.employee and project.task. Support grid view, timers, and invoicing readiness.
- **Project Planning & Scheduling** (`cap_project_planning`): Use Gantt charts, milestones, dependencies, and deadlines to plan project execution and track progress against planned hours.
- **Resource Allocation** (`cap_resource_allocation`): Assign tasks to users, balance workloads across teams, and use project_forecast for capacity planning and scheduling.
- **Project Profitability** (`cap_project_profitability`): Track project profitability through timesheet costs, sale order links, billed hours, and margin analysis (sale_timesheet enterprise).
- **Visibility & Collaboration** (`cap_project_visibility`): Configure project visibility for portal users, employees, or private followers. Manage project.collaborator access and customer sharing.
- **Stage Automation & KPIs** (`cap_stage_automation`): Configure automated actions, SLAs, stage-change notifications, and project dashboard KPIs including burndown and forecasting.
- **Project Security Model** (`cap_project_security`): Apply security groups (project.group_project_user, project.group_project_manager) and record rules for multi-company, private tasks, and visibility.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Project Forecast is an Enterprise feature requiring project_forecast module
- Sale-timesheet profitability requires sale_timesheet and a linked sales order
- Resource allocation views are simplified without full workforce management

## Context

- **Domain:** Project
- **Subdomain:** Project Management
- **Skill ID:** skill_project
- **Knowledge package:** `skills/project/`

- **Required modules:** project
- **Optional modules:** hr_timesheet, sale_timesheet, project_forecast

- **Depends on skills:** skill_base, skill_mail
- **Relevant modules:** project, hr_timesheet, sale_timesheet, project_forecast, analytic, hr, sales_team
