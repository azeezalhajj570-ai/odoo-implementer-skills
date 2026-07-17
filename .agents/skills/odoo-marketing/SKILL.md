# Skill: odoo-marketing

Odoo Marketing Automation Expert — Expert-level knowledge of Odoo marketing automation including Email Marketing (mass_mailing v2.7), Marketing Automation campaigns (9 trigger types), A/B testing, SMS marketing, social marketing, link tracking, UTM attribution, and AI-powered content generation. Use when the user asks about Email Marketing, Marketing Automation Campaigns, A/B Testing, Link Tracking & Attribution, UTM Campaign Tracking in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/marketing/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/marketing/skill.json` — metadata, modules, dependencies
   - `skills/marketing/capability.json` — detailed capability definitions
   - `skills/marketing/knowledge.json` — key models, files, crons, security groups
   - `skills/marketing/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Email Marketing** (`cap_email_marketing`): Mass mailing creation, drag-and-drop email builder, A/B testing, scheduling, link tracking, recipient targeting (lists, filters, domains), statistics (opens, clicks, bounces, replies), blacklist management, unsubscribe flows.
- **Marketing Automation Campaigns** (`cap_marketing_automation`): Multi-step campaign workflows with 9 trigger types (begin, activity, mail_open, mail_not_open, mail_click, mail_not_click, mail_reply, mail_not_reply, mail_bounce). 2 activity types: email and server action. Participant state machine: running -> completed/unlinked. Scheduled via 12h sync cron + 1h execution cron.
- **A/B Testing** (`cap_ab_testing`): Built-in email A/B testing with random split sampling. Winner selection criteria: manual, open rate, click rate, reply rate, leads generated, quotations, revenues. Cron-based winner dispatch.
- **Link Tracking & Attribution** (`cap_link_tracking`): Automatic link shortening in emails via link_tracker. Click recording with IP, country, timestamp. UTM parameter injection. Redirect via /r/<code>. Integration with mass_mailing and marketing_automation.
- **UTM Campaign Tracking** (`cap_utm_tracking`): utm.mixin providing campaign_id, medium_id, source_id. Auto-creation of UTM records. Cookie-based tracking with 31-day expiry. Integration across CRM, mass_mailing, website.
- **SMS Marketing** (`cap_sms_marketing`): SMS campaign creation via mass_mailing_sms. IAP SMS or Twilio backend. Mailing lists, blacklists, delivery tracking.
- **Social Marketing** (`cap_social_marketing`): Multi-platform post scheduling (Facebook, Instagram, LinkedIn, X/Twitter, YouTube). Social streams for monitoring. Post campaigns.
- **Campaign Templates** (`cap_campaign_templates`): 6 pre-built campaign templates: Tag Hot Contacts, Welcome Flow, Double Opt-in, Commercial Prospection, Schedule Calls, Prioritize Hot Leads. Extensible via _get_campaign_templates_info.
- **AI-Powered Content** (`cap_ai_content`): AI prompt integration in email templates via o_editor_prompt divs. AI-generated subject lines, body content, and SEO meta tags. Integration with ai.agent platform.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Marketing Automation requires mass_mailing (Email Marketing) as a dependency
- SMS requires IAP credits or Twilio account
- A/B testing only available for email, not multi-channel
- No dedicated abandoned cart module; requires manual configuration

## Context

- **Domain:** Marketing
- **Subdomain:** Marketing Automation
- **Skill ID:** skill_marketing
- **Knowledge package:** `skills/marketing/`

- **Required modules:** mass_mailing, marketing_automation, link_tracker, utm
- **Optional modules:** mass_mailing_sms

- **Depends on skills:** skill_base, skill_mail
- **Relevant modules:** mass_mailing, marketing_automation, link_tracker, utm
