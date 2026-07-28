# Current AI Social Marketing Implementation — Architecture Analysis

**Author:** Senior Odoo Enterprise Functional Solution Architect  
**Date:** 2026-07-20  
**Odoo Version:** 19.0 Enterprise  
**Status:** Complete  
**Scope:** Reverse-engineering of the existing implementation. No redesign proposals.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Functional Overview](#2-functional-overview)
3. [Business Workflow](#3-business-workflow)
4. [Technical Architecture](#4-technical-architecture)
5. [Execution Flow](#5-execution-flow)
6. [Current AI Pipeline](#6-current-ai-pipeline)
7. [AI Agents](#7-ai-agents)
8. [AI Topics](#8-ai-topics)
9. [AI Tools](#9-ai-tools)
10. [Data Flow](#10-data-flow)
11. [Configuration](#11-configuration)
12. [Existing Odoo Models](#12-existing-odoo-models)
13. [Scheduled Actions](#13-scheduled-actions)
14. [Server Actions](#14-server-actions)
15. [Activities](#15-activities)
16. [Social Marketing Integration](#16-social-marketing-integration)
17. [Manual Review Process](#17-manual-review-process)
18. [Publishing Workflow](#18-publishing-workflow)
19. [Error Handling](#19-error-handling)
20. [Logging](#20-logging)
21. [Security](#21-security)
22. [Multi-company Behaviour](#22-multi-company-behaviour)
23. [Sequence Diagram](#23-sequence-diagram)
24. [Component Diagram](#24-component-diagram)
25. [Strengths](#25-strengths)
26. [Limitations](#26-limitations)

---

## 1. Executive Summary

### What This Document Is

This document provides a complete reverse-engineering and architecture analysis of the existing AI-powered Social Marketing implementation running on Odoo 19 Enterprise at azeez-tech.com. It documents every component, configuration, workflow, and integration point discovered through system inspection.

### What This System Does

The system automatically discovers companies with active social media accounts, reads their brand guidelines from partner notes, determines their industry, searches the web for relevant news, generates branded social media posts, creates review activities, notifies administrators via email, and — upon review approval — schedules the posts for publication. The entire pipeline runs on a daily cron schedule and uses Google Gemini 2.5 Flash as its AI provider.

### Scope of Analysis

This analysis covers:

- All AI Agents, Topics, and Tools
- All Server Actions (the pipeline logic)
- All Scheduled Actions (crons)
- All Automated Actions
- All Activity Types
- All relevant Odoo models
- All companies with social accounts
- All knowledge sources (web URLs referenced in AI topic sources)
- All configuration parameters

### Key Finding

The system is a functional proof-of-concept built entirely within Odoo's low-code framework (server actions, ai.agent, ai.topic, base.automation, ir.cron). It has no custom Python modules, no external services, and no custom Odoo models. The entire pipeline is a single monolithic server action (record #845) that orchestrates research, content generation, deduplication, draft creation, activity scheduling, and email notification in one procedural code block.

---

## 2. Functional Overview

### Business Problem Solved

Companies managing social media accounts through Odoo Social Marketing need to consistently publish fresh, branded content without manual daily effort. The system addresses this by:

1. **Automated discovery**: Finds companies with active social accounts automatically.
2. **Brand-aware generation**: Reads brand guidelines from each company's partner notes.
3. **Industry detection**: Determines whether a company is tech or sports to tailor web searches.
4. **Web research**: Uses Google Gemini's web search capability to find relevant news.
5. **Content creation**: Generates formatted social media posts.
6. **Review workflow**: Creates review activities and email notifications.
7. **Duplicate prevention**: Attempts to prevent publishing similar content (with three layers of dedup).
8. **Error resilience**: Handles AI API failures gracefully with alert activities.

### Current Limitations in Coverage

- Only 2 companies have active social accounts with social media platforms: AzeezTech (tech, Facebook + Instagram + LinkedIn) and NabdSportsAI (sport, accounts not fully visible).
- The system only supports two industries (sport/tech) through hardcoded keyword detection.
- Only one AI provider (Google Gemini) is used.
- All companies use the same AI agent and topic — no per-company agent selection.
- The pipeline does not distinguish between platform types for content formatting.

---

## 3. Business Workflow

### Complete Business Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DAILY AUTOMATED CYCLE                       │
│                                                                     │
│    Cron #54 fires at 8:00 PM                                        │
│         │                                                            │
│         ▼                                                            │
│    Load action #845 code                                             │
│         │                                                            │
│         ▼                                                            │
│    Iterate all companies in system                                   │
│         │                                                            │
│         ├── Filter: companies with active social accounts            │
│         │         on Facebook/LinkedIn/Instagram/Twitter             │
│         │                                                            │
│         └── For each matching company:                               │
│               ├── Read partner.comment (brand guidelines)           │
│               ├── Detect industry (sport/tech via keyword match)     │
│               ├── Fetch last 10 posts (dedup context)                │
│               ├── Build search query per industry                    │
│               ├── Call agent #14._tool_web_search()                  │
│               │     with brand context + dedup context               │
│               ├── Parse web search result                            │
│               │     ├── If "NO_FRESH_ANGLE" → skip                  │
│               │     ├── If error (quota/rate limit) → create alert   │
│               │     └── If success → extract content                 │
│               ├── Format post content                                │
│               ├── Hard dedup check (first 200 chars)                 │
│               │     └── If match → skip                              │
│               ├── Create social.post (draft)                         │
│               ├── Schedule review activity                           │
│               └── Send email notification                            │
│                                                                     │
│    Activity created for admin                                        │
│         │                                                            │
│         ▼                                                            │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         MANUAL REVIEW CYCLE                         │
│                                                                     │
│    Admin opens Activities panel                                      │
│         │                                                            │
│         ▼                                                            │
│    Sees "Review: {Company} post" activity                            │
│         │                                                            │
│         ├── Open activity → read post preview                       │
│         │                                                            │
│         ├── Open social.post → review full content                  │
│         │                                                            │
│         ├── Options:                                                │
│         │    ├── Approve → Mark Activity Done                       │
│         │    │            → Automation triggers                      │
│         │    │            → Action #849 schedules post (now+1h)     │
│         │    │            → Cron #15 publishes                       │
│         │    │                                                       │
│         │    ├── Reject → Mark Done (with feedback)                  │
│         │    │          → (no auto retrigger implemented)            │
│         │    │                                                       │
│         │    └── Regenerate → Run Rewrite action                    │
│         │                   → Action #850 generates new draft        │
│         │                   → New activity created                   │
└─────────────────────────────────────────────────────────────────────┘
```

### User Journey

| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | Administrator | Configure brand guidelines in partner.comment | HTML saved to database |
| 2 | Administrator | Connect social accounts per company | social.account records created |
| 3 | Administrator | (Optional) Set up calendar for 8PM review | None — cron runs automatically |
| 4 | System | Cron fires at 8PM | Pipeline runs for all companies |
| 5 | System | Search web, generate content | social.post created as draft |
| 6 | System | Create review activity | mail.activity scheduled |
| 7 | System | Send notification email | mail.mail sent |
| 8 | Administrator | Read email | Navigates to post |
| 9 | Administrator | Review post in Activities panel | Sees full content |
| 10 | Administrator | Mark Activity Done | Automation fires |
| 11 | System | Schedule post for +1 hour | social.post state='scheduled' |
| 12 | System | Hourly publication cron | Post published to connected accounts |

### Manual Steps

1. **Setting up brand guidelines**: Administrator must write HTML-formatted brand guidelines in the partner's Notes tab.
2. **Connecting social accounts**: Administrator must authenticate OAuth for each social platform.
3. **Reviewing drafts**: Administrator must open Activities panel, review, and mark Done.
4. **Regenerating rejected posts**: No automated rejection flow — administrator must manually run the Rewrite action.
5. **Monitoring alerts**: Administrator must check activities for ⚠️ Web Search Failed alerts.

### Automatic Steps

1. Discovery of companies with accounts (no configuration needed).
2. Industry detection from company name + notes.
3. Web research via Gemini API.
4. Content generation and formatting.
5. Draft post creation.
6. Review activity creation.
7. Email notification.
8. Activity Done → schedule → publish (automatic after human review).

---

## 4. Technical Architecture

### Architecture Type

The implementation uses **Odoo low-code architecture** exclusively. No custom Python modules (`__manifest__.py` files) have been created. All business logic is implemented through:

- `ir.actions.server` records (Python code stored in database)
- `ir.cron` records (scheduled actions)
- `base.automation` records (automated actions on model events)
- `mail.activity.type` records (activity types)
- `ai.agent` records (AI agent definitions)
- `ai.topic` records (AI prompt instructions)
- `ai.topic.tool` records (tools available to AI topics
- `social.post` records (social media posts)
- `social.account` records (social media accounts)
- `res.partner.comment` field (brand guidelines storage)
- `ir.config_parameter` (system parameters, including AI API keys)

### Module Composition

There are **no custom modules**. The implementation uses:

- `ai_app` — core AI module (agents, topics, tools, web search)
- `social_marketing` — social media posting
- `social_facebook` — Facebook publishing
- `social_linkedin` — LinkedIn publishing
- `ai_whatsapp` — WhatsApp AI integration (separate from social posting)
- `mail` — messaging, activities, email
- `base` — core Odoo models (res.company, res.partner)

### Data Storage

| Data | Location | Format |
|------|----------|--------|
| Brand guidelines | `res.partner.comment` | HTML text |
| Company configuration | `res.company` fields | Odoo model fields |
| Social accounts | `social.account` | Odoo model with OAuth tokens |
| Social posts | `social.post` | Odoo model with message content |
| AI agent definitions | `ai.agent` | Odoo model |
| AI prompt instructions | `ai.topic.instructions` | Text |
| AI tools | `ir.actions.server` | Python code |
| Pipeline logic | `ir.actions.server.code` | Python code |
| Cron schedule | `ir.cron` | Odoo model fields |
| Activities | `mail.activity` | Odoo model |
| Email notifications | `mail.mail` | Odoo model |

### External Dependencies

- **Google Gemini API** (gemini-2.5-flash model) for web search and content generation.
- **Social platform APIs** (Facebook, LinkedIn) for publishing — handled by Odoo's existing social modules.

---

## 5. Execution Flow

### Full Trace

```
Time: 20:00:00
Cron #54 fires
  └── code: env['ir.actions.server'].browse(846).run()
         └── Action #846 "AI Social News: Dynamic Post at 8PM"
                └── code: env['ir.actions.server'].browse(845).run()
                       └── Action #845 "AI Social News: Dynamic Multi-Company"
                              │
                              ├── Administration setup
                              │   ├── admin_user = env.user (Administrator)
                              │   ├── admin_email from partner.email
                              │   ├── now = datetime.datetime.now()
                              │   ├── agent = env['ai.agent'].browse(14)  (Social Media Agent)
                              │   └── activity_type = env['mail.activity.type'].browse(9)  (Social Post Review)
                              │
                              ├── Company loop starts
                              │   └── env['res.company'].search([])
                              │       └── Returns: [Royal Abaya, Yemen Royal Honey, Royal Men's Wear, 
                              │                      ThedailyQuran, AzeezTech, NabdSportsAI]
                              │
                              ├── Company #5: AzeezTech
                              │   ├── Find social accounts
                              │   │   └── social.account.search([
                              │   │       ('company_id', '=', 5),
                              │   │       ('active', '=', True),
                              │   │       ('media_type', 'in', ['facebook', 'linkedin', 'instagram', 'twitter'])
                              │   │   ])
                              │   │   └── Returns: [#11 Facebook, #12 Instagram]
                              │   │       (Instagram marked disconnected but still returned)
                              │   │
                              │   ├── Read brand guidelines
                              │   │   └── partner_id = company.partner_id (#18 AzeezTech)
                              │   │   └── partner.comment → HTML string (Arabic brand guidelines)
                              │   │   └── brand_summary = clean HTML, first 1500 chars
                              │   │
                              │   ├── Industry detection
                              │   │   └── text = (company.name + brand_notes).lower()
                              │   │   └── Check keywords: sport, رياضة, نبض, كرة, athlete, stadium, esport, sports
                              │   │   └── Default: 'tech'
                              │   │   └── query = 'latest AI technology news breakthroughs business'
                              │   │
                              │   ├── Dedup: fetch last 10 posts
                              │   │   └── social.post.search([
                              │   │       ('company_id', '=', 5),
                              │   │       ('state', 'in', ['draft', 'scheduled', 'posted'])
                              │   │   ], limit=10, order='create_date desc')
                              │   │   └── Build dedup_context with numbered recent posts
                              │   │
                              │   ├── Call AI Agent
                              │   │   └── agent._tool_web_search(ai, query, 'web', full_context)
                              │   │   │   where full_context = 
                              │   │   │   'BRAND GUIDELINES (FOLLOW THESE FIRST): Company: AzeezTech. 
                              │   │   │    {brand_summary}. Industry: tech. 
                              │   │   │    SEMANTIC DEDUP CHECK REQUIRED. Recent posts: Post1: ...'
                              │   │   │
                              │   │   └── Result: raw text (or error)
                              │   │       ├── If "NO_FRESH_ANGLE" → log, skip
                              │   │       ├── If error keywords → search_results = ''
                              │   │       └── If success → search_results = result_text
                              │   │
                              │   ├── Format post content
                              │   │   └── If search_results >= 200 chars:
                              │   │       ├── Clean text (remove #, *, quotes)
                              │   │       ├── Extract lines > 40 chars and < 500 chars
                              │   │       ├── Build: {Company} | {Header}
                              │   │       │         {insight 1}
                              │   │       │         📌 {insight 2}
                              │   │       │         📌 {insight 3}
                              │   │       │         💡 #Hashtag
                              │   │       └── Header: arabic or english based on keywords
                              │   │
                              │   ├── Error handling
                              │   │   └── If no post_content:
                              │   │       ├── Create alert activity on partner
                              │   │       │   (summary="⚠️ Web Search Failed: AzeezTech")
                              │   │       ├── Include error details in activity note
                              │   │       └── continue (skip to next company)
                              │   │
                              │   ├── Hard dedup
                              │   │   └── Compare first 200 chars against all posts
                              │   │       ├── If match → log + continue
                              │   │       └── If no match → proceed
                              │   │
                              │   ├── Create social.post (draft)
                              │   │   └── post = env['social.post'].create({
                              │   │       'message': post_content,
                              │   │       'account_ids': [(6, 0, [11, 12])],
                              │   │       'company_id': 5,
                              │   │       'state': 'draft',
                              │   │       'source_id': UTM source or False
                              │   │   })
                              │   │
                              │   ├── Create review activity
                              │   │   └── post.activity_schedule(
                              │   │       activity_type_id=9,  (Social Post Review)
                              │   │       summary='Review: AzeezTech post',
                              │   │       note=post_content[:500],
                              │   │       user_id=admin_user.id,
                              │   │       date_deadline=today 21:00
                              │   │   )
                              │   │
                              │   └── Send email notification
                              │       └── mail.mail.create({
                              │           subject='[Review] AzeezTech Post - Jul 20',
                              │           body_html=formatted preview,
                              │           email_to='support@azeez-tech.com',
                              │           ...
                              │       }).send()
                              │
                              ├── Company #43: NabdSportsAI
                              │   └── Similar flow with 'sport' industry, different query
                              │
                              └── Done (2 companies processed)
```

---

## 6. Current AI Pipeline

### Architecture

The pipeline is a **single stage** implemented within one server action:

```
┌────────────────────────────────────────────────────────┐
│                Action #845 (Monolithic)                 │
│                                                        │
│  Company Loop                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  For each company:                               │  │
│  │                                                   │  │
│  │  1. Discovery (social.account search)             │  │
│  │  2. Brand extraction (partner.comment)             │  │
│  │  3. Industry detection (keyword match)             │  │
│  │  4. Dedup context (last 10 posts)                  │  │
│  │  5. Web search call (agent #14)                    │  │
│  │     ├─ Research + generation + dedup all in one    │  │
│  │     └─ Single Gemini API call                      │  │
│  │  6. Content formatting                             │  │
│  │  7. Hard dedup (200-char check)                    │  │
│  │  8. Draft creation                                 │  │
│  │  9. Activity creation                              │  │
│  │  10. Email notification                            │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### Why It's Monolithic

The pipeline was designed as a single `for` loop because:

- The `_tool_web_search` method on `ai.agent` handles both research AND content generation in one call — the AI agent receives the full context (brand guidelines + dedup + research query) and produces formatted content directly.
- There is no separation between "what to research" and "what to generate" — the AI produces both in one pass.
- There is no intermediary data structure passed between stages — each company is processed completely before the next one starts.

### Key Integration Point

The only AI integration is:

```python
agent = env['ai.agent'].browse(14)
ai = {}
result = agent._tool_web_search(ai, query, 'web', full_context)
```

This single call does everything:
1. Receives the brand context, dedup info, and search query.
2. Calls Gemini 2.5 Flash via the `_tool_web_search` method.
3. Returns the generated content (or error).

---

## 7. AI Agents

### Agent Inventory

There are 8 AI agents in the system, but only **one** is directly used by the social posting pipeline (agent #14). Agent #9 is used by an older tool (action #838) which is on topic #13 but is not actively called by the pipeline.

| ID | Name | LLM Model | Used By | Active |
|----|------|-----------|---------|--------|
| 1 | Odoo Agent | gemini-2.5-flash | System (Ask AI) | Yes |
| 2 | Ask AI | gemini-2.5-flash | Chat/Assistant | Yes |
| 4 | Livechat AI Agent | gpt-4o | Livechat | Yes |
| 5 | Ask AI [azeeztech] | gemini-2.5-flash | AzeezTech knowledge | Yes |
| 7 | WhatsApp AI Agent [2] | gemini-2.5-flash | WhatsApp automation | Yes |
| 9 | AI News Social Poster | gemini-2.5-flash | Old tool #838 | Yes |
| 10 | Odoo Image Generation Agent | gemini-2.5-flash | Image generation | Yes |
| **14** | **Social Media Agent** | **gemini-2.5-flash** | **Action #845** | **Yes** |

### Agent #14 — Social Media Agent (Primary)

**Purpose:** The single AI entity responsible for generating social media content for all companies.

**Model:** Google Gemini 2.5 Flash
**Style:** Balanced
**Role:** Unified social media content agent for all companies

**System Prompt:**
```
You are the unified social media content agent for all companies in this Odoo system.

For each company you serve:
- Read the company partner's Notes (comment field) — this contains the brand voice, tone, language, and content guidelines
- Detect the company's industry from their name and notes (tech, sports, general business)
- Search the web for the latest relevant news in that industry
- Create an engaging, human-written social media post following the brand voice

Post Structure:
- Engaging headline (relevant to the company)
- 2-3 insights or bullet points with real substance
- A key takeaway that provides value to readers
- A call to action (ask a question, encourage discussion)
- 3-5 relevant hashtags in the brand's preferred language

Languages: Follow the brand guidelines. Arabic brands get Arabic posts. English or bilingual as specified.
Tone: Professional, engaging, human — never robotic or generic.
```

**Assigned Topic:** #13 — Social Content Posting

**Tools Available (via Topic #13):**

| Tool ID | Name | Model | Method |
|---------|------|-------|--------|
| 664 | AI: Add Tags | documents.document | `_ai_action_add_tags` |
| 145 | AI: Adjust Search | ai.agent | `_ai_tool_adjust_search` |
| 838 | AI Social News Generator | social.post | (uses agent #9) |
| 835 | AI: Web Search | ai.agent | `_tool_web_search` |

Note: Only tool #835 is actually called by the pipeline. Tools 664, 145, and 838 are assigned to the topic but not invoked in the current pipeline code.

**How the Agent is Called:**
The pipeline calls `agent._tool_web_search()` directly. This is a method on `ai.agent` that uses the AI model to perform web searches.

```python
agent = env['ai.agent'].browse(14)
ai = {}
result = agent._tool_web_search(ai, query, 'web', full_context)
```

### Agent #9 — AI News Social Poster (Legacy)

**Purpose:** Older agent used by tool #838. Active but not used in the main pipeline.

**System Prompt:** Focuses on AI/tech news curation for Facebook and LinkedIn, with Arabic/English language support.

**Note:** Tool #838 is on Topic #13's tool list but is not called by the pipeline code. It may be available for manual execution.

---

## 8. AI Topics

### Topic Inventory

There are 13 topics in the system. Three are relevant to the social posting pipeline:

| ID | Name | Used By Agent | Role |
|----|------|---------------|------|
| 13 | Social Content Posting | #14 | Main pipeline topic |
| 11 | AI & Tech News Curation | #9 (legacy) | Older news curation |
| 12 | Social Media Post Writing | (not directly used) | Post writing guidelines |

### Topic #13 — Social Content Posting (Primary)

**Purpose:** Provides instructions to Agent #14 for generating brand-aware social media posts with semantic deduplication.

**Variables:** None — all context is passed through the `full_context` parameter in the `_tool_web_search` call.

**Prompt Structure:**
```
[Role Definition]
You help generate social media posts for multiple companies.

[Processing Steps]
For each company:
1. Read partner notes for brand guidelines
2. Detect industry
3. Search web for relevant news
4. Create branded post
5. Include relevant hashtags

[Format Rules]
Post format: headline, 2-3 insights, takeaway, CTA, hashtags

[Dedup Protocol]
--- SEMANTIC DEDUPLICATION PROTOCOL ---
(semantic similarity check instructions)

[Examples]
- EN/Arabic duplicate detection examples
```

**Tools Assigned:**
- 664 (AI: Add Tags) — not invoked by pipeline
- 145 (AI: Adjust Search) — not invoked by pipeline
- 838 (AI Social News Generator) — not invoked by pipeline
- 835 (AI: Web Search) — **the only tool actually invoked**

**How the Topic is Used:**
The topic's `instructions` field is loaded by the agent when `_tool_web_search` is called. The `full_context` string is passed as the search context, which the agent combines with its system prompt and topic instructions to produce a response.

**Output Format:**
The agent returns raw text — typically a structured social media post with headline, insights (with 📌 bullets), key takeaway (💡), and hashtags.

### Topics #11 and #12 (Legacy)

**Topic #11 — AI & Tech News Curation:**
Instructions to search for AI tech news and curate 3 stories. Tools include web search and the older AI Social News Generator (#838).

**Topic #12 — Social Media Post Writing:**
General post writing guidelines for Facebook and LinkedIn.

These topics exist from an earlier implementation phase and are no longer actively used.

---

## 9. AI Tools

### Tool Inventory

The system has many tools registered as `ir.actions.server` records on model `ai.agent`. Only one is actively used by the pipeline:

| ID | Name | Model | Method | Used By Pipeline |
|----|------|-------|--------|------------------|
| 835 | AI: Web Search | ai.agent | `_tool_web_search` | **Yes** |
| 838 | AI Social News Generator | social.post | Uses agent #9 directly | No (on topic but not invoked) |
| 664 | AI: Add Tags | documents.document | `_ai_action_add_tags` | No |
| 145 | AI: Adjust Search | ai.agent | `_ai_tool_adjust_search` | No |
| 139 | AI: Get Fields | ai.agent | `_ai_tool_get_fields` | No |
| 146 | AI: Search | ai.agent | `_ai_tool_search` | No |
| 147 | AI: Read group | ai.agent | `_ai_tool_read_group` | No |

### Tool #835 — AI: Web Search (Critical)

**Why it exists:** Provides web search capability to AI agents through the configured LLM provider (Gemini). This is the primary method by which the pipeline obtains information to create posts.

**When called:** Once per company per pipeline run.

**Which agent uses it:** Agent #14 (Social Media Agent).

**Which topic invokes it:** Topic #13 (Social Content Posting), though the call is made directly in the pipeline code, not triggered by the topic's tool resolution.

**Expected input:**
```python
agent._tool_web_search(
    ai,           # dict — method writes result into this dict
    query,        # str — search query
    'web',        # str — retrieval mode (always 'web')
    full_context  # str — brand guidelines + dedup context + instructions
)
```

**Expected output:**
The method populates the `ai` dict with the search results. The exact structure depends on the underlying implementation in the `ai_app` module.

**Failure behavior:**
- If the result is empty, shorter than 50 chars, or contains error keywords, `search_results` is set to `''`.
- If the AI returns `NO_FRESH_ANGLE`, the pipeline logs and skips.
- If the underlying Gemini API fails (quota, 503, etc.), the exception is caught and `search_results` is set to `''`.

### Tool #838 — AI Social News Generator (Legacy)

**Why it exists:** Older tool that uses Agent #9 directly to generate AI news for an image search query. Purely for testing/legacy purposes.

**When called:** Never in production — assigned to Topic #13 but not invoked by pipeline action #845.

### Tool #664 — AI: Add Tags

**Purpose:** Tags documents using AI. Not related to social posting but assigned to Topics #11, #12, #13.

---

## 10. Data Flow

### Complete Data Flow Per Company

```
─────────────────────────────────────────────────────────────────
STEP 1: Company Discovery
─────────────────────────────────────────────────────────────────

Input:  env['res.company'].search([]) — all companies
Output: List of company browse records

Transformation: None (raw Odoo ORM query)

─────────────────────────────────────────────────────────────────
STEP 2: Account Filtering
─────────────────────────────────────────────────────────────────

Input:  company.id
        social.account.search([
            ('company_id', '=', company.id),
            ('active', '=', True),
            ('media_type', 'in', ['facebook', 'linkedin', 'instagram', 'twitter']),
        ])
Output: Recordset of matching social accounts, or empty

Transformation: Reject companies with no matching accounts (continue)

─────────────────────────────────────────────────────────────────
STEP 3: Brand Guidelines Extraction
─────────────────────────────────────────────────────────────────

Input:  partner = company.partner_id
        brand_notes = partner.comment (HTML string or '')
Output: brand_summary — first 1500 chars of cleaned text

Transformation: 
        HTML tags stripped: <p>→\n, </p>→\n, <br/>→\n, <li>→\n- , 
        </li>/<ul>/</ul> removed

─────────────────────────────────────────────────────────────────
STEP 4: Industry Detection
─────────────────────────────────────────────────────────────────

Input:  text = (company.name + ' ' + brand_notes).lower()
Output: industry = 'tech' or 'sport'
        query = 'latest AI technology news breakthroughs business' 
              or 'AI in sports latest news'

Transformation:
        If any keyword (sport, رياضة, نبض, كرة, athlete, stadium, 
        esport, sports) found in text → industry='sport'
        Default → industry='tech'

─────────────────────────────────────────────────────────────────
STEP 5: Dedup Context Building
─────────────────────────────────────────────────────────────────

Input:  social.post.search([...], limit=10, order='create_date desc')
Output: dedup_context string

Transformation:
        For each post: extract message[:300], join with ' | '
        Prefix: 'SEMANTIC DEDUP CHECK REQUIRED. Recent posts: '
        Suffix: 'You MUST NOT repeat... If all same, respond NO_FRESH_ANGLE'

─────────────────────────────────────────────────────────────────
STEP 6: AI Web Search Call
─────────────────────────────────────────────────────────────────

Input:  agent = env['ai.agent'].browse(14)
        query = (from step 4)
        full_context = 'BRAND GUIDELINES (FOLLOW THESE FIRST): ' 
                     + 'Company: ' + company.name + '. ' 
                     + brand_summary + '. Industry: ' + industry + '. '
                     + dedup_context
Output: search_results string (from AI response), or ''

Transformation:
        agent._tool_web_search(ai, query, 'web', full_context)
        → If NO_FRESH_ANGLE found: log, skip
        → If error keywords found: search_results = ''
        → If success: search_results = result_text

─────────────────────────────────────────────────────────────────
STEP 7: Post Content Formatting
─────────────────────────────────────────────────────────────────

Input:  search_results (raw text from AI)
Output: post_content (formatted post), or '' (empty = alert)

Transformation:
        1. Replace carriage returns and escaped newlines
        2. Split by newline, filter lines > 30 chars
        3. Clean each line: remove #, *, ", '
        4. Keep lines between 40-500 chars
        5. If >= 2 lines remain:
           - Build header: "أحدث الأخبار" (Arabic) or "Latest News" (English)
           - Format: CompanyName | Header\n\n
                     {line1}\n\n📌 {line2}\n\n📌 {line3}\n\n💡 #CompanyName
        6. If fewer than 2 lines remain: post_content = '' (alert)

─────────────────────────────────────────────────────────────────
STEP 8: Hard Dedup Check
─────────────────────────────────────────────────────────────────

Input:  post_content[:200]
        env['social.post'].search([...not in last_post_ids], limit=10)
Output: continue or skip

Transformation:
        For each old post: compare first 200 chars (stripped)
        If any match: log 'DUPLICATE DETECTED', continue (next company)

─────────────────────────────────────────────────────────────────
STEP 9: Draft Post Creation
─────────────────────────────────────────────────────────────────

Input:  post_content, account_ids, company_id
Output: social.post record (state='draft')

Models: social.post.create({
    'message': post_content,
    'account_ids': [(6, 0, [account_ids])],
    'company_id': company.id,
    'state': 'draft',
    'source_id': source.id or False,
})

─────────────────────────────────────────────────────────────────
STEP 10: Review Activity Creation
─────────────────────────────────────────────────────────────────

Input:  post browse record, activity_type_id=9
Output: mail.activity record

Models: post.activity_schedule(
    act_type_xmlid=False,
    activity_type_id=9,
    summary=f'Review: {company.name} post',
    note=post_content[:500],
    user_id=admin.id,
    date_deadline=today 21:00,
)

─────────────────────────────────────────────────────────────────
STEP 11: Email Notification
─────────────────────────────────────────────────────────────────

Input:  post content, company.email, base_url
Output: mail.mail record (sent)

Models: mail.mail.create({
    'subject': '[Review] {company} Post - {date}',
    'body_html': formatted HTML with preview + link,
    'email_to': company.email,
    'email_from': admin.company_id.email,
}).send()
```

---

## 11. Configuration

### Configurable Items

| Item | Location | Type | Editable By |
|------|----------|------|-------------|
| AI Provider | `ir.config_parameter` (API key) | System parameter | Administrator |
| AI Model | `ai.agent.llm_model` | Selection (per agent) | Administrator |
| AI Agent | `ai.agent.system_prompt` | Text | Administrator |
| AI Topic Instructions | `ai.topic.instructions` | Text | Administrator |
| Brand Guidelines | `res.partner.comment` | HTML | Administrator |
| Company Email | `res.company.email` | Char | Administrator |
| Social Accounts | `social.account` | Odoo record | Social Marketing |
| Cron Schedule | `ir.cron.interval_number/type` | Integer/Selection | Administrator |
| Server Action Code | `ir.actions.server.code` | Python code | Administrator/Technical |
| Activity Type | `mail.activity.type` | Odoo record | Administrator |
| Automation Rule | `base.automation` | Odoo record | Administrator |

### Industry Detection Configuration

Industries are **not configurable**. The detection uses hardcoded keyword lists in the server action code:

```python
# tech (default)
# No positive keywords — tech is the fallback

# sport (detected by any of these):
['sport', 'رياضة', 'نبض', 'كرة', 'athlete', 'stadium', 'esport', 'sports']
```

### Search Query Configuration

Search queries are **not configurable**. Hardcoded in server action:

```python
'latest AI technology news breakthroughs business'  # tech
'AI in sports latest news'                           # sport
```

### Brand Guidelines Configuration

Brand guidelines are **minimally configurable** through `res.partner.comment`. The administrator writes free-form HTML. There is no validation, no structure enforcement, and no default values.

### Web Source URLs

Web source URLs are **not configurable**. They are hardcoded within the AI agent's topic sources (ai.agent.source records) and the topic instructions themselves. The specific sources referenced:

| Topic | Sources |
|-------|---------|
| Agent #14 Topic #13 | None visible in instructions — search is driven by the query string |
| Agent #9 (legacy) | AI/tech news sources (from earlier configuration) |

### System Parameters (ir.config_parameter)

No custom system parameters exist for the social posting pipeline. The Gemini API key is configured through Odoo's standard AI provider configuration (Settings > General Settings > AI).

---

## 12. Existing Odoo Models

### Models Used (No Custom Models)

| Model | Usage | Key Fields |
|-------|-------|------------|
| `res.company` | Company entity | `id`, `name`, `email`, `partner_id`, |
| `res.partner` | Company contact with brand notes | `id`, `name`, `comment` (HTML brand guidelines) |
| `res.lang` | Language configuration | `code`, `name` |
| `res.users` | Administrator user | `id`, `partner_id`, `company_id` |
| `ai.agent` | AI agent definitions | `id`, `name`, `llm_model`, `system_prompt`, `topic_ids`, `response_style`, `partner_id`, `source_id` |
| `ai.topic` | AI prompt instructions | `id`, `name`, `description`, `instructions`, `tool_ids` |
| `ai.topic.tool` | Tool definitions (linked to `ir.actions.server`) | `id`, `name`, `model`, `method`, `description` |
| `ai.agent.source` | Knowledge sources for AI agents | `id`, `name`, `url`, `agent_id` |
| `social.post` | Social media posts | `id`, `message`, `state`, `company_id`, `account_ids`, `scheduled_date`, `create_date` |
| `social.account` | Social media accounts | `id`, `name`, `company_id`, `media_type`, `active` |
| `social.media.type` | Platform types (Facebook, LinkedIn, etc.) | `id`, `name` |
| `social.live.post` | Published posts | `id`, `post_id`, `state`, `published_date` |
| `mail.activity` | Activities | `id`, `summary`, `activity_type_id`, `res_model`, `res_id`, `user_id`, `date_deadline`, `state` |
| `mail.activity.type` | Activity types | `id`, `name`, `icon`, `res_model`, `category` |
| `mail.mail` | Email messages | `id`, `subject`, `body_html`, `email_to`, `state` |
| `ir.actions.server` | Server action definitions | `id`, `name`, `model_id`, `state`, `code` |
| `ir.cron` | Scheduled actions | `id`, `name`, `active`, `state`, `code`, `interval_number`, `interval_type`, `nextcall`, `user_id` |
| `base.automation` | Automation rules | `id`, `name`, `model_id`, `trigger`, `action_server_ids`, `filter_pre_domain` |
| `ir.config_parameter` | System parameters | `id`, `key`, `value` |
| `utm.source` | UTM tracking sources | `id`, `name` |

### Key Relationships

```
res.company (1) ──── (N) social.account
res.company (1) ──── (1) res.partner (via partner_id)
res.partner (1) ──── has comment field (brand guidelines)

social.account (N) ──── (1) res.company
social.account (N) ──── (1) social.media.type (via media_id)

social.post (N) ──── (1) res.company
social.post (N) ──── (N) social.account (via account_ids M2M)
social.post (N) ──── (1) mail.activity (via activity references)

ai.agent (1) ──── (N) ai.topic (via topic_ids M2M)
ai.topic (1) ──── (N) ai.topic.tool (via tool_ids M2M → ir.actions.server)

mail.activity (N) ──── (1) mail.activity.type
mail.activity (N) ──── (1) social.post (via res_model='social.post', res_id)

ir.cron (1) ──── (1) ir.actions.server (via ir_actions_server_id)
base.automation (N) ──── (N) ir.actions.server (via action_server_ids)
```

---

## 13. Scheduled Actions

### Cron Inventory

| ID | Name | Active | Interval | Next Run | Model | Code |
|----|------|--------|----------|----------|-------|------|
| **54** | **AI Social News: Dynamic Post at 8PM** | Yes | 1 day | 2026-07-21 20:00 | social.post | `env['ir.actions.server'].browse(846).run()` |
| **15** | **Social: Publish Scheduled Posts** | Yes | 1 hour | Hourly | social.post | `model._cron_publish_scheduled()` |
| 11 | AI Embedding: Generate Embeddings | Yes | 9999 months | - | (built-in) | `model._cron_generate_embedding()` |
| 12 | AI Agent Sources: Process Sources | Yes | 9999 months | - | (built-in) | `model._cron_process_sources()` |
| 13 | AI Fields: Compute AI fields | Yes | 1 day | - | (built-in) | `model._cron_fill_ai_fields()` |
| 3 | Mail: Email Queue Manager | Yes | 1 hour | - | (built-in) | `model.process_email_queue()` |
| 6 | Mail: Fetchmail Service | Yes | 5 mins | - | (built-in) | `model._fetch_mails()` |
| 7 | Mail: Post scheduled messages | Yes | 1 day | - | (built-in) | `model._post_messages_cron()` |
| 9 | Mail: send web push notification | Yes | 1 day | - | (built-in) | `model._push_notification_to_endpoint()` |
| 17 | Digest Emails | Yes | 1 day | - | (built-in) | `model._cron_send_digest_email()` |
| 30 | Product: send email regarding products availability | Yes | 1 hour | - | (built-in) | (built-in) |

### Cron #54 — AI Social News: Dynamic Post at 8PM

- **Model:** `social.post`
- **Code:** `env['ir.actions.server'].browse(846).run()`
- **Calls Action:** #846 "AI Social News: Dynamic Post at 8PM"
- **Interval:** Every 1 day
- **Next Run:** 2026-07-21 20:00:00
- **Active:** Yes

**Note:** Action #846 is a wrapper that simply calls action #845:
```python
env['ir.actions.server'].browse(845).run()
```

This indirection allows the cron and action to be managed separately.

### Cron #15 — Social: Publish Scheduled Posts (Built-in)

- **Model:** `social.post`
- **Code:** `model._cron_publish_scheduled()` — standard Odoo method
- **Interval:** Every 1 hour
- **Active:** Yes
- **Purpose:** Publishes all social.post records with `state='scheduled'` and `scheduled_date <= now`

This is the standard Odoo Social Marketing cron — no custom modifications.

---

## 14. Server Actions

### Action Inventory

| ID | Name | Model | State | Purpose |
|----|------|-------|-------|---------|
| **845** | **AI Social News: Dynamic Multi-Company** | social.post | code | **Main pipeline** |
| **846** | **AI Social News: Dynamic Post at 8PM** | social.post | code | Cron wrapper → calls #845 |
| **849** | **Auto Schedule on Activity Done** | mail.activity | code | Triggered by automation → schedules post |
| **850** | **Rewrite with AI** | social.post | code | Manual action → regenerates post content |
| 835 | AI: Web Search | ai.agent | code | Tool for _tool_web_search |
| 838 | AI Social News Generator | social.post | code | Legacy tool using agent #9 |

### Action #845 — AI Social News: Dynamic Multi-Company (Primary)

**Responsibility:** Full pipeline orchestrator for all companies.

**Model:** `social.post` (bound to this model but operates independently)

**Code Summary:** ~140 lines of Python in a single `for` loop.

**Processing Flow (detailed in Section 5):**
1. Setup: admin user, agent #14, activity type #9
2. Loop over all companies:
   a. Find social accounts matching platform criteria
   b. Extract brand guidelines from partner.comment
   c. Detect industry (sport/tech via keywords)
   d. Fetch last 10 posts for dedup, build context
   e. Call agent._tool_web_search()
   f. Handle errors: NO_FRESH_ANGLE, quota, bad results
   g. Format post content from search results
   h. Create alert activity if web search failed
   i. Hard dedup check (first 200 chars)
   j. Create social.post (draft state)
   k. Create review activity on the post
   l. Send email notification

**Dependencies:**
- Agent #14 (Social Media Agent)
- Activity Type #9 (Social Post Review)
- UTM Source "Social Media" (attempts to find or create)
- `res.company` records
- `social.account` records with active=true, media_type in platform list

### Action #846 — AI Social News: Dynamic Post at 8PM

**Responsibility:** Wrapper that allows the cron to indirectly run action #845.

**Code:** `env['ir.actions.server'].browse(845).run()`

**Purpose:** This indirection lets an administrator modify the pipeline (change action #845) without touching the cron configuration. It also allows manual execution from the server action list.

### Action #849 — Auto Schedule on Activity Done

**Responsibility:** Receive activity records, check if they are "Social Post Review" activities marked done, and schedule the associated post.

**Model:** `mail.activity` (bound to Activity model)

**Code:**
```python
for activity in records:
    if activity.state != 'done' or activity.activity_type_id.id != 9:
        continue
    if activity.res_model == 'social.post' and activity.res_id:
        post = env['social.post'].browse(activity.res_id)
        if post and post.state == 'draft':
            now = datetime.datetime.now()
            scheduled = now.replace(hour=now.hour + 1, minute=0, second=0)
            post.write({
                'state': 'scheduled',
                'scheduled_date': scheduled.strftime('%%Y-%%m-%%d %%H:%%M:%%S'),
            })
            log('Post auto-scheduled: id=' + str(post.id))
```

**Trigger:** Called by Automation Rule #2 when a `mail.activity` record is written
**Filter:** Only processes activities where `state` changes from `!= 'done'` to `'done'`
**Activity Type Filter:** Only activity_type_id = 9 (Social Post Review)
**Result:** Sets `state='scheduled'` and `scheduled_date` to next hour (now+1h)

### Action #850 — Rewrite with AI

**Responsibility:** Manual action that regenerates post content for a selected post using fresh web search. Does NOT use the dedup protocol or brand context from action #845.

**Model:** `social.post`

**Code:** Similar to the content generation part of action #845, but simplified:
- Reads brand notes (first 400 chars only)
- Calls _tool_web_search with minimal context
- Only replaces the post's `message` field
- Does NOT create new activities or send emails

**Limitations:**
- Only passes 400 chars of brand context (vs 1500 in the main pipeline)
- No dedup context passed
- No NO_FRESH_ANGLE detection
- No error keyword detection
- Always generates Arabic header "أحدث الأخبار" regardless of company profile

---

## 15. Activities

### Activity Type Inventory

Only one custom activity type exists for the social posting pipeline:

| ID | Name | Icon | Category | Model | Decoration |
|----|------|------|----------|-------|------------|
| 9 | Social Post Review | fa-check-circle | default | social.post | warning |

### Activity Type #9 — Social Post Review

**Created:** Custom activity type for the AI social posting pipeline.

**Fields:**
- `name`: "Social Post Review"
- `icon`: fa-check-circle
- `category`: default
- `res_model`: social.post (default model for activities of this type)
- `decoration_type`: warning (visually highlighted in Activities panel)
- `chaining_type`: suggest

**How it's used:**
1. Action #845 creates an activity on each new draft post:
   ```python
   post.activity_schedule(
       act_type_xmlid=False,
       activity_type_id=9,
       summary='Review: {company.name} post',
       note=post_content[:500],
       user_id=admin_user.id,
       date_deadline=deadline,
   )
   ```
2. Administrator sees the activity in the Activities panel.
3. Opening the activity shows the post preview (first 500 chars).
4. Marking the activity "Done" triggers Automation Rule #2.

### Alert Activities (Web Search Failed)

When web search fails, an activity is created on the company's partner record (not on a social post):

```python
partner.activity_schedule(
    act_type_xmlid=False,
    activity_type_id=9,
    summary='⚠️ Web Search Failed: {company.name}',
    note='Error details...',
    user_id=admin_user.id,
    date_deadline=deadline,
)
```

These activities use the same type (9) but are attached to `res.partner` records, not `social.post`.

---

## 16. Social Marketing Integration

### Integration Points

The pipeline integrates with Odoo Social Marketing through:

1. **`social.account`** — discovers which companies have active social accounts with the right `media_type` (facebook, linkedin, instagram, twitter) and `active=True`.

2. **`social.post`** — creates draft posts with the generated content, linked to company and accounts.

3. **`social.live.post`** — indirectly, through the built-in publication cron (Cron #15).

4. **`social.media.type`** — uses the `media_type` field (not `platform`) to filter accounts. Values: `facebook`, `linkedin`, `instagram`, `twitter`, `youtube`, `push_notifications`.

5. **UTM** — attempts to find or set `utm.source` with name "Social Media" on created posts. If the source doesn't exist, the field is set to False (no error).

### Platform Coverage

The pipeline only processes accounts with `media_type` in:
```python
['facebook', 'linkedin', 'instagram', 'twitter']
```

Notably:
- YouTube accounts are excluded from content generation.
- Push Notification accounts are excluded.
- Instagram accounts are included but may have `is_media_disconnected=True`.

### UTM Source

The pipeline attempts to set `utm.source` on created posts:
```python
source = env['utm.source'].search([('name', '=', 'Social Media')], limit=1)
post.create({
    ...
    'source_id': source.id if source else False,
})
```

At the time of analysis, the "Social Media" UTM source does not exist, so `source_id` is false for all created posts.

---

## 17. Manual Review Process

### Step-by-Step Process

1. **Notification**: Administrator receives an email notification:
   - Subject: `[Review] {Company} Post - {Date}`
   - Body: HTML preview of the post with a link to the Odoo form view

2. **Activity Panel**: The administrator opens Activities (bell icon in top bar).

3. **Review**: Clicks on the activity "Review: {Company} post" →
   - Opens the activity detail
   - Shows the post content preview (first 500 chars)
   - Shows deadline (today at 9 PM from pipeline)

4. **Options**:

   | Action | How | System Response |
   |--------|-----|-----------------|
   | **Approve** | Mark Activity Done | Automation #2 fires → Action #849 schedules post for +1 hour |
   | **Edit** | Open post from activity link, modify content | Save changes → Mark Activity Done → Automation fires |
   | **Regenerate** | Run "Rewrite with AI" action from post form | Action #850 generates new content, replaces message |
   | **Discard** | Postpone or reschedule activity | Post remains in draft; next cron run may detect it as duplicate |

5. **Activity Done → Schedule**: The activity being marked "done" triggers:
   - Automation #2 (filter: state changes from `!= done` to `done`)
   - Action #849 checks: is activity type #9? Yes → is res_model social.post? Yes →
   - Sets `state='scheduled'`, `scheduled_date = now + 1 hour`

6. **Publication**: Cron #15 (hourly) picks up the scheduled post and publishes it to all connected accounts.

### Manual Only Actions

- **Rewriting content**: Must manually run Action #850 from the post form.
- **Rejecting posts**: No "reject" workflow — the activity can be canceled or postponed.
- **Skipping duplicate posts**: Must manually delete or archive.
- **Monitoring web search failures**: Must check Activities for ⚠️ alerts.

---

## 18. Publishing Workflow

### Full Publication Chain

```
Action #845 creates social.post (state='draft')
         │
         ▼
    Activity created (type: Social Post Review)
         │
         ▼
    Admin marks Activity Done
         │
         ▼
    Automation #2 fires (on_write, mail.activity)
         │
         ▼
    Filter: state changes from != 'done' to 'done'
    (filter_pre_domain: [['state', '!=', 'done']])
         │
         ▼
    Action #849 runs:
        - Checks activity_type_id == 9 (Social Post Review)
        - Checks res_model == 'social.post'
        - Checks post.state == 'draft'
        - Sets state='scheduled'
        - Sets scheduled_date = now + 1 hour
         │
         ▼
    Cron #15 runs (every hour)
         │
         ▼
    Finds social.post where state='scheduled' AND scheduled_date <= now
    Calls model._cron_publish_scheduled()
         │
         ▼
    Publishes post to configured social accounts
    (Facebook, LinkedIn, etc.) using OAuth tokens
         │
         ▼
    state → 'posted'
    social.live.post created per platform
```

---

## 19. Error Handling

### Error Detection Strategy

The pipeline identifies errors through keyword matching on the AI response:

```python
error_keywords = [
    'failed', 'quota', 'rate limit', 'rate_limit', 
    'error', 'not available', 'try again later'
]
is_error = any(kw in result_text.lower() for kw in error_keywords)
```

### Error Categories and Responses

| Error Type | Detection | Response |
|------------|-----------|----------|
| **Gemini quota exhausted** | Keyword match in response | Creates alert activity on partner |
| **Rate limited** | Keyword match | Creates alert activity on partner |
| **Network/timeout** | Python exception caught | `search_results = ''`, alert activity created |
| **No results** | Result < 50 chars or < 200 chars | Alert activity created |
| **DUPLICATE** | NO_FRESH_ANGLE in AI response | Logs and skips (continue) |
| **Exact match duplicate** | First 200 chars comparison | Logs and skips (continue) |
| **No companies with accounts** | Inner loop never executed | Logs "No companies found" |

### Alert Activity Format

When web search fails, the activity note includes:
```
Web search failed for {company}.

The AI could not fetch live news to generate a post.
Error: {first 300 chars of error response}

Possible causes: API quota exceeded, network issue, or service outage.
Check the Gemini API key in Settings > Parameters or wait for quota reset.
```

### What Is NOT Handled

- **AI provider timeout**: The `_tool_web_search` timeout behavior depends on the underlying implementation. No explicit timeout control.
- **Partial failures**: If one company succeeds and another fails, both are logged but no summary is produced.
- **Rate limit for all companies**: If quota is exhausted mid-pipeline, remaining companies silently fail.
- **Activity link resolution**: Alert activities are on the partner record, not linked to a post — no navigation path from activity to the failed company's configuration.

---

## 20. Logging

### Current Logging Implementation

Logging is minimal and uses Odoo's built-in `log()` function within server actions:

```python
log('No fresh angle for ' + company.name + ' — AI reported NO_FRESH_ANGLE')
log('Web search failed for ' + company.name + ' — alert activity created')
log('DUPLICATE DETECTED for ' + company.name + ' — skipping (matches post #' + str(old_post.id) + ')')
log('Draft post created for ' + company.name + ': id=' + str(post.id))
log('No companies found')
```

### Where Logs Go

`log()` calls in server actions write to the Odoo server log (typically `stdout` or log file). These are **not stored in a database model** — there is no:

- Audit log model
- AI execution log model
- Post creation history model
- Search history model
- Dedup decision history model

### What Is Missing

- No record of what search query was used per company per run.
- No record of what the AI returned (full response).
- No record of token usage or cost.
- No record of pipeline execution duration.
- No aggregate statistics (posts per day, success rate, etc.).
- No visual dashboard or log viewer.

---

## 21. Security

### Security Architecture

The pipeline runs as the Administrator user (`env.user = admin`). There is no dedicated system user or service account.

### Access Rights

The pipeline relies entirely on the built-in Administrator user having full access to all models:

- `res.company` — search, read all companies
- `social.account` — search, read all accounts
- `social.post` — create, write, read all posts
- `res.partner` — read, write all partners
- `mail.activity` — create, schedule
- `mail.mail` — create, send
- `ir.actions.server` — execute
- `ai.agent` — call methods

### Security Groups

No custom security groups have been created for the social posting pipeline. The system is accessed through the existing `Administrator / Settings` group.

### Multi-company Security

No multi-company record rules are implemented for the pipeline components. The pipeline iterates `res.company.search([])` — ALL companies — without filtering by the current user's allowed companies. This means:

- Any company in the system (even ones the admin doesn't belong to) will have posts generated.
- Brand guidelines for all companies are readable by the pipeline.
- No company isolation in execution logs (since there are no execution logs).

---

## 22. Multi-company Behaviour

### Current Implementation

The pipeline discovers all companies indiscriminately:

```python
companies = env['res.company'].search([])
```

No company filter is applied. All 6 companies in the system are checked. Most are filtered out by the account search (no matching social accounts).

### Companies with Social Accounts

| Company ID | Name | Has Active Social (FB/LI/IG/TW) | Industry |
|-----------|------|--------------------------------|----------|
| 5 | AzeezTech | Yes (#11 Facebook, #12 Instagram) | tech |
| 43 | NabdSportsAI | Yes (2 accounts) | sport |
| 1 | Royal Abaya | No | - |
| 2 | Yemen Royal Honey | No | - |
| 3 | Royal Men's Wear | No | - |
| 4 | ThedailyQuran | No | - |

### Company Isolation

Since all pipeline logic runs as Administrator with full access:

- **Brand guidelines**: All company partners are readable.
- **Posts**: All companies' posts are readable and writable.
- **Activities**: All activities are visible to Administrator.
- **Accounts**: All accounts are visible.

There is no data isolation between companies in the current pipeline. This is acceptable for the current deployment (single-enterprise scenario) but would be a concern in a multi-tenant environment.

---

## 23. Sequence Diagram

```
┌─────────┐     ┌────────────┐     ┌────────────┐     ┌───────────┐     ┌──────────┐     ┌─────────┐     ┌───────────┐
│ Cron #54 │     │ Action #846 │     │ Action #845 │     │ Agent #14 │     │ social.  │     │ mail.   │     │ mail.mail │
│ (8PM)    │     │ (Wrapper)   │     │ (Pipeline)  │     │ (Gemini)  │     │ post     │     │activity │     │           │
└─────┬────┘     └──────┬─────┘     └──────┬──────┘     └─────┬─────┘     └────┬─────┘     └───┬─────┘     └─────┬─────┘
      │                  │                  │                   │                │               │               │
      │ Fires            │                  │                   │                │               │               │
      │─────────────────→│                  │                   │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │ Calls pipeline   │                   │                │               │               │
      │                  │─────────────────→│                   │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Loop companies    │                │               │               │
      │                  │                  │───┐               │                │               │               │
      │                  │                  │   │ for each co   │                │               │               │
      │                  │                  │◄──┘               │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Find accounts     │                │               │               │
      │                  │                  │───────────────┐   │                │               │               │
      │                  │                  │               │   │                │               │               │
      │                  │                  │◄──────────────┘   │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Read partner      │                │               │               │
      │                  │                  │ .comment          │                │               │               │
      │                  │                  │───────────────┐   │                │               │               │
      │                  │                  │               │   │                │               │               │
      │                  │                  │◄──────────────┘   │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Build context     │                │               │               │
      │                  │                  │ Fetch last 10     │                │               │               │
      │                  │                  │ posts             │                │               │               │
      │                  │                  │───┐               │                │               │               │
      │                  │                  │   │               │                │               │               │
      │                  │                  │◄──┘               │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ _tool_web_search  │                │               │               │
      │                  │                  │──────────────────→│                │               │               │
      │                  │                  │                   │  Gemini API    │               │               │
      │                  │                  │                   │───────┐        │               │               │
      │                  │                  │                   │       │        │               │               │
      │                  │                  │   Search Results  │◄──────┘        │               │               │
      │                  │                  │◄──────────────────│                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Check NO_FRESH_   │                │               │               │
      │                  │                  │ ANGLE / error     │                │               │               │
      │                  │                  │───┐               │                │               │               │
      │                  │                  │   │               │                │               │               │
      │                  │                  │◄──┘               │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Format content    │                │               │               │
      │                  │                  │───┐               │                │               │               │
      │                  │                  │   │               │                │               │               │
      │                  │                  │◄──┘               │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Hard dedup check  │                │               │               │
      │                  │                  │───┐               │                │               │               │
      │                  │                  │   │               │                │               │               │
      │                  │                  │◄──┘               │                │               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ If passed:        │                │               │               │
      │                  │                  │ Create draft post │                │               │               │
      │                  │                  │───────────────────────────────────→│               │               │
      │                  │                  │                   │                │  (draft)      │               │
      │                  │                  │◄───────────────────────────────────│               │               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Schedule activity │                │               │               │
      │                  │                  │──────────────────────────────────────────────────→│               │
      │                  │                  │                   │                │               │  (pending)    │
      │                  │                  │◄──────────────────────────────────────────────────│               │
      │                  │                  │                   │                │               │               │
      │                  │                  │ Send email        │                │               │               │
      │                  │                  │───────────────────────────────────────────────────────────────→│
      │                  │                  │                   │                │               │               │
      │                  │                  │ Next company...   │                │               │               │
```

---

## 24. Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Odoo 19 Enterprise Instance                           │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    AI Social Posting Pipeline                          │   │
│  │                                                                        │   │
│  │  ┌──────────────┐                                                       │   │
│  │  │  Cron #54    │────Daily 8PM────→ Action #846 ──→ Action #845        │   │
│  │  └──────────────┘                                                       │   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                   Action #845 Code Body                          │   │   │
│  │  │                                                                   │   │   │
│  │  │  ┌────────────────────────┐    ┌──────────────────────────────┐ │   │   │
│  │  │  │ Company Discovery      │    │ Industry Detection           │ │   │   │
│  │  │  │ res.company.search([]) │    │ if 'sport' in text: sport    │ │   │   │
│  │  │  │ social.account.search()│    │ else: tech (default)          │ │   │   │
│  │  │  └────────────────────────┘    └──────────────────────────────┘ │   │   │
│  │  │                                                                   │   │   │
│  │  │  ┌────────────────────────┐    ┌──────────────────────────────┐ │   │   │
│  │  │  │ Brand Extraction       │    │ Dedup Context                │ │   │   │
│  │  │  │ partner.comment → text│    │ last 10 posts → numbered list│ │   │   │
│  │  │  │ HTML → cleaned 1500c   │    │ SEMANTIC DEDUP prefix         │ │   │   │
│  │  │  └────────────────────────┘    └──────────────────────────────┘ │   │   │
│  │  │                                                                   │   │   │
│  │  │  ┌────────────────────────────────────────────────────────────┐ │   │   │
│  │  │  │ AI Call: _tool_web_search(agent #14, query, 'web',        │ │   │   │
│  │  │  │   context = BRAND GUIDELINES FIRST + dedup_context)        │ │   │   │
│  │  │  └────────────────────────────────────────────────────────────┘ │   │   │
│  │  │                                                                   │   │   │
│  │  │  ┌────────────────────────┐    ┌──────────────────────────────┐ │   │   │
│  │  │  │ Error Handling         │    │ Content Formatting            │ │   │   │
│  │  │  │ NO_FRESH_ANGLE → skip  │    │ Extract lines > 40 chars     │ │   │   │
│  │  │  │ quota/rate limit → alt │    │ Build: header + insights     │ │   │   │
│  │  │  │ exception → alt        │    │ 💡 #Hashtag                  │ │   │   │
│  │  │  └────────────────────────┘    └──────────────────────────────┘ │   │   │
│  │  │                                                                   │   │   │
│  │  │  ┌────────────────────────┐    ┌──────────────────────────────┐ │   │   │
│  │  │  │ Hard Dedup             │    │ Post + Activity + Email      │ │   │   │
│  │  │  │ first 200 chars match  │    │ social.post.create(draft)   │ │   │   │
│  │  │  │ if match → skip        │    │ post.activity_schedule()    │ │   │   │
│  │  │  └────────────────────────┘    │ mail.mail.create().send()   │ │   │   │
│  │  │                                └──────────────────────────────┘ │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    AI Components                                      │   │
│  │                                                                        │   │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌─────────────────┐ │   │
│  │  │ Agent #14          │  │ Topic #13          │  │ Tools (topic)   │ │   │
│  │  │ Social Media Agent │  │ Social Content     │  │ #835 Web Search │ │   │
│  │  │ Gemini 2.5 Flash   │  │ Posting            │  │ #664 Add Tags   │ │   │
│  │  │ Balanced           │  │ Dedup protocol     │  │ #145 Adj Search │ │   │
│  │  │ Unified for all    │  │ Brand instructions │  │ #838 Gen (old)  │ │   │
│  │  └────────────────────┘  └────────────────────┘  └─────────────────┘ │   │
│  │                                                                        │   │
│  │  ┌────────────────────┐  ┌────────────────────┐                       │   │
│  │  │ Agent #9 (legacy)  │  │ Topics #11, #12    │                       │   │
│  │  │ AI News Social     │  │ AI & Tech News     │                       │   │
│  │  │ Poster (not used)  │  │ Curation (not used)│                       │   │
│  │  └────────────────────┘  └────────────────────┘                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Review & Publish                                   │   │
│  │                                                                        │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────┐ │   │
│  │  │ Activity Type #9 │  │ Automation Rule  │  │ Action #849         │ │   │
│  │  │ Social Post      │  │ #2               │  │ Auto Schedule:      │ │   │
│  │  │ Review           │  │ on_write         │  │ → state='scheduled' │ │   │
│  │  │ fa-check-circle  │  │ mail.activity    │  │ → now + 1 hour      │ │   │
│  │  │ warning decor    │  │ filter: != done  │  └─────────────────────┘ │   │
│  │  └──────────────────┘  └──────────────────┘                            │   │
│  │                                                                        │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────┐ │   │
│  │  │ Cron #15         │  │ social.post      │  │ Social Accounts     │ │   │
│  │  │ Publish Scheduled│  │ state=posted     │  │ (Facebook, LinkedIn)│ │   │
│  │  │ Every hour       │  │ live.post created│  │ OAuth connected     │ │   │
│  │  └──────────────────┘  └──────────────────┘  └─────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Data Store                                        │   │
│  │                                                                        │   │
│  │  res.company ── res.partner (comment=brand guidelines)                 │   │
│  │       │                                                               │   │
│  │       └── social.account (Facebook, Instagram, LinkedIn, Twitter)      │   │
│  │       └── social.post (draft → scheduled → posted)                     │   │
│  │            └── mail.activity (Social Post Review)                      │   │
│  │            └── mail.mail (Review notification)                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    External Systems                                  │   │
│  │                                                                        │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                │   │
│  │  │ Google Gemini│   │ Facebook API│   │ LinkedIn API│                │   │
│  │  │ 2.5 Flash   │   │ (OAuth2)    │   │ (OAuth2)    │                │   │
│  │  │ Web search  │   │ Publish     │   │ Publish     │                │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 25. Strengths

### 1. Fully Odoo-Native

The entire implementation uses standard Odoo models (`ai.agent`, `ai.topic`, `ir.actions.server`, `ir.cron`, `base.automation`, `mail.activity`). No custom modules, no third-party dependencies, no external databases. This means:

- All configuration is visible and editable from the Odoo UI.
- Standard Odoo upgrades won't break custom Python modules.
- Any Odoo administrator can understand the architecture.
- No deployment complexity beyond standard Odoo.

### 2. AI Provider Abstraction (Partial)

The `ai.agent._tool_web_search()` method abstracts the underlying AI provider. The pipeline calls this method without knowing whether Gemini, OpenAI, or another provider handles the request. The provider is configured once in the agent record.

### 3. No Custom Odoo Models

Zero custom models means zero database migrations, zero schema conflicts, zero upgrade concerns. Everything uses existing Odoo table structures.

### 4. Editable AI Topics

The topic instructions (`ai.topic.instructions`) are stored in the database and editable from the Odoo UI. Administrators can modify the AI's behavior, dedup protocol, and post format without any code changes.

### 5. Editable Server Actions

The pipeline logic is in `ir.actions.server.code`, which is editable from Settings > Technical > Actions > Server Actions. This allows technical administrators to modify behavior without deploying code.

### 6. Semantic Dedup Protocol

The topic instructions include a well-defined "SEMANTIC DEDUPLICATION PROTOCOL" that explicitly instructs the AI to:
- Compare keywords and topics across languages
- Avoid same topics even when rephrased
- Return `NO_FRESH_ANGLE` when all search results cover duplicate topics

This is a good pattern for AI-level duplicate prevention.

### 7. Graceful Error Handling

The pipeline handles:
- Quota exhaustion (creates alert activities instead of failing silently)
- Rate limiting (detects error keywords)
- Missing companies (logs and continues)
- Duplicate detection (hard dedup as safety net)

### 8. Multi-Company Discovery

The pipeline automatically discovers any company with active social accounts — no per-company configuration is needed for the basic flow.

### 9. Standard Activity Review Flow

The review process uses Odoo's standard `mail.activity` framework. Administrators see review requests in their Activities panel alongside all other activities — no separate UI needed.

### 10. Separation of Cron and Pipeline

Cron #54 calls Action #846, which calls Action #845. This indirection means:
- The cron schedule can be changed without touching the pipeline.
- The pipeline can be triggered manually from the Server Actions list without waiting for the cron.
- Both can be tested independently.

---

## 26. Limitations

### 1. Monolithic Pipeline Architecture

**Observation:** All pipeline stages (research, content generation, dedup, formatting, draft creation, activity creation, email) are in a single server action with a single `for` loop.

**Impact:**
- Cannot run stages independently.
- Cannot test research without also testing generation.
- Cannot add new stages without modifying the entire action.
- A failure in any stage blocks the entire company's pipeline.
- No modularity — the action is ~140 lines of procedural code.

### 2. Hardcoded Industry Detection

**Observation:** Two hardcoded industry lists in the server action code:

```python
['sport', 'رياضة', 'نبض', 'كرة', 'athlete', 'stadium', 'esport', 'sports']
```

Default: `tech` (no positive keywords to match).

**Impact:**
- Only sport and tech are supported.
- Adding a new industry requires modifying Python code.
- Companies like "Royal Men's Wear" (fashion) would default to "tech" — producing irrelevant AI news content about AI breakthroughs when fashion news would be appropriate.
- No industry configuration UI.

### 3. Hardcoded Search Queries

**Observation:**
```python
query = 'AI in sports latest news' if industry == 'sport' else 'latest AI technology news breakthroughs business'
```

**Impact:**
- Every "tech" company searches for the same topic, regardless of their specific focus.
- AzeezTech (AI consulting) and a hypothetical hardware manufacturer would both search "AI technology breakthroughs" — ignoring hardware news.
- Cannot customize queries per company without code changes.

### 4. Unstructured Brand Guidelines

**Observation:** Brand guidelines are stored in `res.partner.comment` as free-form HTML.

**Impact:**
- No field-level validation — brand voice, tone, language, forbidden words are all in one HTML blob.
- The pipeline must parse HTML to extract plain text for the AI.
- Different companies may have different HTML structures, leading to inconsistent extraction.
- No default values, tooltips, or guided setup.
- Hard to enforce that essential fields (language, tone) are filled.
- Cannot filter or query by brand properties (e.g., "find all companies using Arabic").

### 5. No Knowledge Management

**Observation:** Knowledge sources are not modeled. The AI searches the web generically based on the hardcoded query. The only URL configuration is through `ai.agent.source` records which are not used by the pipeline.

**Impact:**
- Every company searches the open web — no access to internal documentation, private knowledge bases, or curated sources.
- No way to exclude irrelevant sources.
- No source trust scoring or priority.
- No caching of search results — every pipeline run searches fresh.

### 6. Single AI Agent for All Responsibilities

**Observation:** Agent #14 handles:
- Reading brand guidelines
- Understanding company context
- Searching the web
- Generating content
- Performing deduplication (via topic instructions)

**Impact:**
- No separation of concerns — the agent is both researcher and writer.
- Cannot optimize different agents for different tasks (a specialized research agent could use a different model/prompt than a generation agent).
- The system prompt and topic instructions must cover all responsibilities in one document.
- Harder to debug which part of the prompt controls which aspect of behavior.

### 7. No Quality Audit

**Observation:** There is no quality gate. Content goes from AI → draft → review with no automated quality check.

**Impact:**
- Posts may contain spelling errors, unsupported claims, or off-brand content.
- The quality of posts depends entirely on Gemini's baseline quality.
- No automated enforcement of character limits, hashtag counts, or platform rules.
- No user-editable quality criteria.

### 8. Text-Only Dedup as Safety Net

**Observation:** The hard dedup compares exact first-200 character strings.

**Impact:**
- Misses semantic duplicates (different wording, same topic).
- Misses translated duplicates (English vs Arabic same topic).
- The AI-level dedup (NO_FRESH_ANGLE) partially addresses this, but it depends entirely on Gemini's judgment — no systematic comparison.

### 9. No Execution Logging

**Observation:** Only 6 `log()` calls exist in the pipeline. No structured logging model.

**Impact:**
- Cannot audit past pipeline runs.
- Cannot debug "why did this post get created" for past posts.
- Cannot measure token usage, cost, or performance.
- No history of what the AI returned for a given company on a given day.

### 10. No Per-Company Agent Assignment

**Observation:** All companies use Agent #14 with Topic #13.

**Impact:**
- Companies with different needs (sport vs tech, Arabic vs English) cannot have different AI configurations.
- Must change the same topic for all companies simultaneously.
- Cannot set different temperatures, models, or response styles per company.

### 11. No Content Variant Generation

**Observation:** The pipeline generates exactly one post per company per run.

**Impact:**
- No per-platform content optimization (Facebook vs LinkedIn post format differences are handled by the AI in one pass).
- No A/B testing of different messages.
- No option to generate multiple variants and select the best.

### 12. Limited Automation on Rejection

**Observation:** If an administrator rejects a post, there is no automated re-generation.

**Impact:**
- Administrator must manually run the "Rewrite with AI" action.
- No context is passed about why the post was rejected (the rewrite action doesn't ask for feedback).
- No automated escalation if a post is rejected multiple times.

### 13. Hardcoded Email and UTM

**Observation:** The UTM source name is hardcoded as "Social Media". The email "from" address uses the admin's company email. No email templates are used.

**Impact:**
- Cannot change the UTM source without code changes.
- Email format is hardcoded in the action — no email template editing through UI.

### 14. No Post Scheduling Per Company

**Observation:** Cron #54 runs daily at 8PM for ALL companies.

**Impact:**
- Cannot set different posting times per company.
- Cannot set different maximum posts per day per company.
- If a company should post twice daily, a separate cron would be needed.

### 15. No Performance Optimization

**Observation:** No indexing, caching, or batch processing strategies implemented.

**Impact:**
- Every pipeline run scans all companies.
- Every run fetches last 10 posts for each company.
- Brand guidelines are extracted and cleaned from HTML each run (no caching).
- AI web search is called fresh for each company — no deduplication of queries.

### 16. No Extensibility Mechanism

**Observation:** Adding a new capability (e.g., image generation, SEO optimization) would require modifying the server action code.

**Impact:**
- The pipeline is closed to extension — no plugin mechanism.
- New stages cannot be "plugged in" without editing the existing code.
- Adding functionality increases code complexity in the already monolithic action.

---

**Document Status:** Complete  

**Analysis Coverage:** 100% of discovered components documented.  
**Custom Models:** 0 — all functionality uses existing Odoo models.  
**Lines of Pipeline Code:** ~140 (single server action).  
**Software Versions:** Odoo 19.0 Enterprise, Gemini 2.5 Flash.
