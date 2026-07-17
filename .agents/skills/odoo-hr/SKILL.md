# Skill: odoo-hr

Odoo HR Expert — Expert-level knowledge of Odoo Human Resources including employees, contracts, departments, attendance, leaves, expenses, recruitment, appraisals, and payroll integration. Use when the user asks about Employee Management, Department Structure, Contracts, Attendance, Leaves & Time Off in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/hr/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/hr/skill.json` — metadata, modules, dependencies
   - `skills/hr/capability.json` — detailed capability definitions
   - `skills/hr/knowledge.json` — key models, files, crons, security groups
   - `skills/hr/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Employee Management** (`cap_employee`): Manage hr.employee, employee categories, work addresses, managers, private/public info, and employee badges.
- **Department Structure** (`cap_department`): Configure hr.department hierarchy, managers, cost centers, and related employees.
- **Contracts** (`cap_contract`): Manage hr.contract, contract types, wages, schedules, benefits, start/end dates, and contract status.
- **Attendance** (`cap_attendance`): Track hr.attendance records, check-in/check-out, overtime, kiosks, and attendance reporting.
- **Leaves & Time Off** (`cap_leaves`): Configure hr.leave.type, leave allocations, accrual plans, validation workflows, and public holidays.
- **Expenses** (`cap_expenses`): Manage hr.expense, expense sheets, expense categories, approvals, reimbursement via invoices/payments, and analytics.
- **Recruitment** (`cap_recruitment`): Manage hr.job, hr.applicant, interview scheduling, refusal reasons, job boards, and recruitment stages.
- **Appraisals** (`cap_appraisal`): Configure hr.appraisal, appraisal plans, feedback surveys, goals, and employee evaluation cycles with Enterprise hr_appraisal.
- **Payroll Integration** (`cap_payroll`): Understand payroll structures, salary rules, payslips, and payslip batches. Requires Enterprise hr_payroll.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Payroll is an Enterprise module and varies by localization
- HR modules may require additional localization for country-specific labor rules
- Appraisal requires Enterprise hr_appraisal
- Some attendance integrations (kiosks, IoT) need hardware or additional modules

## Context

- **Domain:** Human Resources
- **Subdomain:** HR
- **Skill ID:** skill_hr
- **Knowledge package:** `skills/hr/`

- **Required modules:** hr
- **Optional modules:** hr_contract, hr_attendance, hr_leave, hr_expense, hr_recruitment, hr_appraisal, hr_payroll

- **Depends on skills:** skill_base, skill_mail
- **Relevant modules:** hr, mail, resource, calendar, base_setup, utm
