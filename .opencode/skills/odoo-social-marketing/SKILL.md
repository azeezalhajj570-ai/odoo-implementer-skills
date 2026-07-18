---
name: odoo-social-marketing
description: Use when the user asks about Odoo Social Marketing Expert topics such as Social Account Management, Multi-Platform Publishing, Post Scheduling & Cron, AI-Powered Social Posting, Activity Review Workflow in Odoo 19. Loads knowledge from skills/social_marketing/.
---

# Skill: odoo-social-marketing

Odoo Social Marketing Expert — Expert-level knowledge of Odoo Social Marketing including social account management, multi-platform publishing (Facebook, Instagram, LinkedIn, X/Twitter, YouTube), post scheduling, stream monitoring, campaign tracking, media attachments, and AI-generated content integration. Use when the user asks about Social Account Management, Multi-Platform Publishing, Post Scheduling & Cron, Social Media Attachments, Stream Monitoring, AI-Powered Social Posting, Activity Review Workflow in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/social_marketing/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/social_marketing/skill.json` — metadata, modules, dependencies
   - `skills/social_marketing/capability.json` — detailed capability definitions
   - `skills/social_marketing/knowledge.json` — key models, files, crons, security groups
   - `skills/social_marketing/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Social Account Management** (`cap_social_accounts`): Configure and manage social media accounts (social.account) across Facebook, Instagram, LinkedIn, X/Twitter, and YouTube. Handle OAuth authorization, token refresh, page linking, and account-level permissions.
- **Multi-Platform Publishing** (`cap_social_posting`): Create, schedule, and publish social.post records across one or more platforms. Manage post states (draft, scheduled, posted, failed), per-platform live posts (social.live.post), character limits, and platform-specific formatting.
- **Post Scheduling & Cron** (`cap_post_scheduling`): Schedule posts via scheduled_date field and the social posting cron. Handle timezone-aware publication, failed state fallback, and batch processing of due posts.
- **Social Media Attachments** (`cap_media_attachments`): Attach images and videos to social.post records via ir.attachment. Validate media requirements per platform (dimensions, size, format, count) and link attachments to live posts.
- **Stream Monitoring** (`cap_stream_monitoring`): Create social.stream and collect social.stream.post records for mentions, hashtags, pages, and engagement tracking. Configure stream types and refresh cadence per platform API.
- **Campaign & UTM Tracking** (`cap_campaign_tracking`): Link social.post records to utm.campaign via campaign_id. Track source, medium, and campaign attribution for social traffic using utm.mixin.
- **AI-Powered Social Posting** (`cap_ai_social_posting`): Dynamic multi-company AI social posting pipeline. One unified AI agent reads brand guidelines from partner notes, detects industry, searches web, generates posts, creates review activities, and auto-schedules on approval. See full workflow below.
- **Activity Review Workflow** (`cap_activity_review`): Review AI-generated drafts via mail.activity before publishing. Mark activity Done to auto-schedule via base.automation rule. Configurable deadline and email notifications per company.
- **Social Marketing Security** (`cap_social_security`): Configure social marketing user and manager groups, record rules for multi-company/account isolation, and access control for streams, accounts, and posts.
- **Social Analytics & Reporting** (`cap_social_analytics`): Read engagement metrics from live posts, build dashboards, and report on social campaign performance by platform, account, and campaign.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## AI-Powered Social Posting Pipeline

A dynamic multi-company AI social posting system that automatically discovers companies with social accounts and generates tailored content.

### Architecture

```
Cron (daily at configured time)
  ↓
Server Action — Dynamic Multi-Company
  ↓
For each company with active social accounts:
  ├─ 1. Read partner.comment (HTML field) → brand voice, tone, language
  ├─ 2. Detect industry from company name + partner notes (sport / tech / default)
  ├─ 3. DEDUP: check last 5 posts → avoid repeating topics
  ├─ 4. Call ai.agent._tool_web_search() with industry query + brand context
  ├─ 5. Build post content (web results or fallback headlines)
  ├─ 6. Create social.post with state='draft'
  ├─ 7. Create mail.activity "Social Post Review" assigned to admin
  └─ 8. Send email notification to company.email
```

### Review & Publish Flow

```
Draft post + Activity
  │
  ├─ Admin reviews in Activities panel
  ├─ Mark Activity "Done"
  │     ↓
  ├─ Automation rule triggers (on_write on mail.activity)
  │     ↓
  ├─ Server action runs → reads activity.res_id → post state='scheduled', scheduled_date=now+1h
  │     ↓
  └─ Built-in "Social: Publish Scheduled Posts" cron (hourly) publishes due posts
```

### Components to Create

| Component | Purpose |
|-----------|---------|
| **AI Agent** (ai.agent) | Single unified agent — Gemini 2.5 Flash, balanced style, topic linked |
| **Topic** (ai.topic) | "Social Content Posting" — instructions for brand-aware post generation, linked to Web Search tool |
| **Sources** (ai.agent.source) | Web URLs for news: tech sources (TechCrunch, The Verge AI) + sports sources (BBC Sport, Sky Sports) + general (Hacker News) |
| **Main Action** (ir.actions.server) | Pipeline: discover companies → read brand → search → draft → activity → email |
| **Finalize Action** (ir.actions.server) | Receives mail.activity records, checks state='done' + activity_type_id, schedules related post |
| **Automation Rule** (base.automation) | Trigger on mail.activity write → runs finalize action |
| **Activity Type** (mail.activity.type) | "Social Post Review" — icon fa-check-circle, model social.post |
| **Cron** (ir.cron) | Daily trigger for main action |
| **UTM Source** (utm.source) | "Social Media" — tracking for posts |

### Industry Detection Logic

Scans `company.name` + `partner.comment` for keywords:
- **sport:** sport, رياضة, نبض, كرة, athlete, stadium, esport, sports
- **tech:** tech, تقنية, software, digital, رقمي, تطبيق, ai, intelligence
- **default:** falls back to tech

### Topic Deduplication

Before web search, query last 5 posts per company:
```
last_posts = env['social.post'].search([
    ('company_id', '=', company.id),
    ('state', 'in', ['draft', 'scheduled', 'posted']),
], limit=5, order='create_date desc')
```
Pass dedup context to web search: `"AVOID repeating these topics: {headlines}"`

### Partner Notes Format

Brand guidelines in `res.partner.comment` must be HTML:
```html
<p>Company description and mission.</p>
<p>Brand voice guidelines:</p>
<ul>
  <li>Content requirements</li>
  <li>Tone and language preferences</li>
  <li>Target audience</li>
</ul>
```

### Adding a New Company

1. Create `res.company` record (set email for notifications)
2. Write brand guidelines in partner's `comment` (HTML)
3. Connect social accounts (`social.account` with `company_id` set)
4. Done — next cron run discovers automatically

### Web Search via AI Agent

The `_tool_web_search` method on `ai.agent` searches the web using configured LLM provider:
```python
agent = env['ai.agent'].browse(agent_id)
ai_context = {}
result = agent._tool_web_search(
    ai_context,           # dict, receives result
    query,                # search query string
    'web',                # retrieval mode
    context_hint          # brand context for relevance
)
```

### Post Content Format

```
{Company Name} | {أحدث الأخبار/Latest News}

{insight 1}

📌 {insight 2}

📌 {insight 3}

💡 {takeaway}

#Hashtag1 #Hashtag2
```

### Email Notification

Sent to `company.email` with:
- Company name and post status
- Post preview (formatted)
- Platform list
- Direct link to the post for review

### Image Attachment (Optional)

Images can be attached via `ir.attachment`:
```python
att = env['ir.attachment'].create({
    'name': 'image.jpg',
    'datas': base64_data,
    'store_fname': 'image.jpg',
    'res_model': 'social.post',
    'res_id': post.id,
    'mimetype': 'image/jpeg',
    'type': 'binary',
})
post.write({
    'image_ids': [(4, att.id)],
    'facebook_image_ids': [(4, att.id)],
    'linkedin_image_ids': [(4, att.id)],
})
```

## Limitations

- Publishing requires valid OAuth tokens and is subject to platform API rate limits
- AI web search uses configured LLM provider; subject to API quotas and rate limits
- mail.activity.state is computed (not stored) — cannot filter by it in domains
- Partner notes must be in HTML format for proper rendering
- ir.cron in Odoo 19 uses state='code' + code field, no numbercall field
- social.account uses media_type field (not platform) for platform filtering
- Instagram direct publishing requires Business/Creator accounts and proper Meta permissions
- YouTube posting typically requires videos, not text-only posts

## Context

- **Domain:** Marketing
- **Subdomain:** Social Marketing
- **Skill ID:** skill_social_marketing
- **Knowledge package:** `skills/social_marketing/`

- **Required modules:** social_marketing, utm, ai_app, mail
- **Optional modules:** social_facebook, social_instagram, social_linkedin, social_twitter, social_youtube, project

- **Depends on skills:** skill_base, skill_marketing, skill_mail, skill_ai
- **Relevant modules:** social_marketing, social_facebook, social_instagram, social_linkedin, social_twitter, social_youtube, utm, mail, ai_app
