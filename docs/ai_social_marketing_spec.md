# AI-Powered Social Marketing Platform — Implementation Specification

**Version:** 2.0  
**Author:** Senior Odoo Enterprise Functional Solution Architect  
**Date:** 2026-07-20  
**Odoo Version:** 19.0 Enterprise  
**Status:** Draft for Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Requirements](#2-business-requirements)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-functional Requirements](#4-non-functional-requirements)
5. [Architecture Overview](#5-architecture-overview)
6. [AI Pipeline](#6-ai-pipeline)
7. [AI Agents](#7-ai-agents)
8. [AI Topics](#8-ai-topics)
9. [Brand Profile Design](#9-brand-profile-design)
10. [Knowledge Catalog Design](#10-knowledge-catalog-design)
11. [Knowledge Source Design](#11-knowledge-source-design)
12. [Duplicate Detection Strategy](#12-duplicate-detection-strategy)
13. [Quality Audit Strategy](#13-quality-audit-strategy)
14. [Odoo Models](#14-odoo-models)
15. [User Interface](#15-user-interface)
16. [Configuration Menus](#16-configuration-menus)
17. [Scheduled Actions](#17-scheduled-actions)
18. [Activities](#18-activities)
19. [Security Groups](#19-security-groups)
20. [Record Rules](#20-record-rules)
21. [Multi-company Behavior](#21-multi-company-behavior)
22. [User Flows](#22-user-flows)
23. [Sequence Diagrams](#23-sequence-diagrams)
24. [Error Handling](#24-error-handling)
25. [Performance Strategy](#25-performance-strategy)
26. [Scalability Strategy](#26-scalability-strategy)
27. [Extensibility Strategy](#27-extensibility-strategy)
28. [Migration Strategy](#28-migration-strategy)
29. [Backward Compatibility Strategy](#29-backward-compatibility-strategy)
30. [Testing Strategy](#30-testing-strategy)
31. [Documentation Plan](#31-documentation-plan)
32. [Future Roadmap](#32-future-roadmap)

---

## 1. Executive Summary

### Purpose

This specification defines a next-generation AI-powered Social Marketing platform for Odoo 19 Enterprise. The solution replaces the existing monolithic social posting pipeline with a modular, multi-agent architecture that supports unlimited companies, industries, languages, and AI providers — all configurable from the Odoo UI.

### Current State Analysis

The existing implementation (v1.0) has proven the concept but has architectural limitations:

| Limitation | Impact | Resolution in v2.0 |
|------------|--------|---------------------|
| Single monolithic agent handles research, generation, dedup | No separation of concerns; hard to debug or extend | Five independent agents with single responsibilities |
| Brand guidelines stored in unstructured `partner.comment` HTML | No structured validation; arbitrary content; hard to query | Structured `social.brand.profile` model |
| Hardcoded industry detection (sport/tech) | Cannot support new industries without code change | Configurable industry profiles per company |
| Hardcoded web search queries | All companies search the same topics | Knowledge catalogs with per-company sources |
| Hardcoded Gemini provider | Cannot switch AI providers; vendor lock-in | Provider-agnostic abstraction via `ai.agent` |
| No quality audit | Posts may contain grammar errors, unsupported claims | Quality Audit Agent as final gate |
| Text-only dedup (200-char match) | Misses semantic duplicates across languages | Semantic embedding-based dedup with similarity threshold |
| Single server action (#845) does everything | Spaghetti logic; impossible to test individually | Pipeline of independent actions called by a scheduler |
| No structured duplicate index | Duplicate detection is O(n) per run | Published posts stored in embedding index for O(1) lookup |

### Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Cron Scheduler                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Pipeline Orchestrator (ir.actions.server)          │   │
│  │                                                     │   │
│  │  For each enabled company:                          │   │
│  │    ├─ Load AI Configuration                         │   │
│  │    ├─ Load Brand Profile                            │   │
│  │    ├─ Load Knowledge Sources                        │   │
│  │    ├─ [Agent] Research Agent  ──→ Research Result   │   │
│  │    ├─ [Agent] Post Generator  ──→ Draft Content     │   │
│  │    ├─ [Agent] Duplicate Review ──→ Accept / Rewrite │   │
│  │    ├─ [Agent] Rewrite Agent    ──→ Regenerated      │   │
│  │    ├─ [Agent] Quality Audit    ──→ Pass / Fail      │   │
│  │    ├─ Create social.post (draft)                    │   │
│  │    └─ Create Review Activity                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Key Decisions

1. **Odoo-native**: Uses existing `ai.agent`, `ai.topic`, `social.post`, `mail.activity`, `ir.cron` — no external services required.
2. **Configuration over customization**: Every behavior is driven by database records, not code.
3. **Provider agnostic**: AI capabilities delegated to `ai.agent` which supports Gemini, OpenAI, Anthropic, and custom providers.
4. **Incremental migration**: Existing v1.0 components (agent #14, topic #13, actions #845/#849/#850, cron #54) remain functional during migration. New components are additive.

---

## 2. Business Requirements

### BR-01: Multi-Company AI-Powered Social Media

The system shall automatically discover, research, generate, review, and publish social media content for any number of companies with different industries, languages, and brand requirements.

### BR-02: Brand Consistency

Every generated post shall reflect the company's structured Brand Profile — including voice, tone, language, audience, and positioning — without manual prompting.

### BR-03: Knowledge-Driven Research

Research shall be guided by each company's Knowledge Catalog — a configurable set of URLs, RSS feeds, internal documentation, and industry sources. No URLs shall be hardcoded.

### BR-04: Semantic Duplicate Prevention

The system shall prevent publishing content substantially similar to previous posts, regardless of language or phrasing. Similarity detection shall use semantic embeddings, not string matching.

### BR-05: Quality Assurance

Every generated post shall pass an automated quality audit covering grammar, spelling, brand voice, platform compliance, factual claims, and originality before submission for human review.

### BR-06: Configurable Review Workflow

Administrators shall configure whether posts require human review, auto-publish, or follow a staged approval process — per company, per platform, or per content type.

### BR-07: Provider Independence

The solution shall support multiple AI providers (Google Gemini, OpenAI, Anthropic, custom) through Odoo's existing `ai.agent` abstraction. Switching providers shall require no code changes.

### BR-08: Audit Trail

Every AI action — research, generation, dedup review, rewrite, audit — shall be logged with inputs, outputs, timestamps, and the responsible agent, enabling compliance and debugging.

### BR-09: Horizontal Scalability

The pipeline shall support thousands of companies with millions of historical posts without performance degradation in duplicate detection or research.

### BR-10: Extensibility

New AI agents (image generation, translation, SEO, newsletter) shall be added by registering a new `ai.agent` and `ai.topic` record — not by modifying the pipeline.

---

## 3. Functional Requirements

### FR-01: Company AI Configuration (`social.company.ai.config`)

Each company shall have an AI configuration record containing:

| Field | Type | Purpose |
|-------|------|---------|
| `company_id` | m2o → res.company | Owning company |
| `active` | boolean | Enable/disable AI for this company |
| `ai_provider_id` | m2o → ai.provider | AI provider (Gemini, OpenAI, etc.) |
| `ai_model` | selection | Model variant (e.g., gemini-2.5-flash) |
| `temperature` | float | Creativity control (0.0–1.0) |
| `languages` | m2m → res.lang | Supported languages in priority order |
| `platforms` | m2m → social.media.type | Enable posting to Facebook, LinkedIn, etc. |
| `max_posts_per_day` | integer | Throttle to prevent over-posting |
| `review_required` | boolean | Require manual review before publishing |
| `auto_publish` | boolean | Skip scheduler — publish immediately |
| `similarity_threshold` | float | 0.0–1.0; post is marked duplicate above this |
| `embedding_provider_id` | m2o → ai.provider | Provider for text embeddings |
| `research_agent_id` | m2o → ai.agent | Assigned research agent |
| `generation_agent_id` | m2o → ai.agent | Assigned post generation agent |
| `dedup_agent_id` | m2o → ai.agent | Assigned duplicate review agent |
| `rewrite_agent_id` | m2o → ai.agent | Assigned rewrite agent |
| `audit_agent_id` | m2o → ai.agent | Assigned quality audit agent |

### FR-02: Brand Profile (`social.brand.profile`)

Each company shall have one Brand Profile containing structured fields:

| Field | Type | Purpose |
|-------|------|---------|
| `company_id` | m2o → res.company | Owning company |
| `active` | boolean | Enable/disable this profile |
| `mission` | text | Company mission statement |
| `vision` | text | Company vision |
| `industry` | m2o → social.industry | Configurable industry |
| `products` | text | Product descriptions |
| `services` | text | Service descriptions |
| `target_audience` | text | Who the content is for |
| `customer_personas` | text | Detailed persona descriptions |
| `brand_voice` | selection | Professional/Casual/Technical/Inspirational |
| `tone` | selection | Formal/Friendly/Authoritative/Witty |
| `writing_style` | text | Style guide notes |
| `preferred_vocabulary` | text | Terms to use |
| `forbidden_vocabulary` | text | Terms to avoid |
| `keywords` | text | SEO/topic keywords |
| `competitors` | text | Competitor names |
| `unique_selling_proposition` | text | USP |
| `language_ids` | m2m → res.lang | Language preferences |
| `cta_style` | text | Preferred call-to-action style |
| `hashtag_strategy` | text | Hashtag guidelines |
| `image_style` | text | Image/visual preferences |
| `formatting_rules` | text | Formatting conventions |
| `platform_preferences` | text | Per-platform notes |
| `business_goals` | text | Current business objectives |
| `example_posts` | text | Reference posts for style |
| `notes` | html | Any additional context |

### FR-03: Industry Configuration (`social.industry`)

A standalone model for industry definitions:

| Field | Type | Purpose |
|-------|------|---------|
| `name` | char | Industry name (e.g., "Technology") |
| `code` | char | Machine-readable code |
| `keywords` | text | Detection keywords for auto-classification |
| `default_query` | text | Default research query |
| `active` | boolean | Enable/disable |

### FR-04: Knowledge Catalog (`social.knowledge.catalog`)

| Field | Type | Purpose |
|-------|------|---------|
| `company_id` | m2o → res.company | Owning company |
| `name` | char | Catalog name |
| `active` | boolean | Enable/disable |
| `source_ids` | o2m → social.knowledge.source | Knowledge sources |

### FR-05: Knowledge Source (`social.knowledge.source`)

| Field | Type | Purpose |
|-------|------|---------|
| `catalog_id` | m2o → social.knowledge.catalog | Parent catalog |
| `company_id` | related | Company (via catalog) |
| `name` | char | Source name |
| `url` | char | Source URL |
| `source_type` | selection | RSS / Website / API / Document / YouTube / GitHub |
| `description` | text | What this source contains |
| `active` | boolean | Enable/disable |
| `priority` | integer | 1–100; higher = more weight |
| `language` | m2o → res.lang | Content language |
| `country` | m2o → res.country | Geographic relevance |
| `categories` | m2m → social.content.category | Topic categories |
| `search_keywords` | text | Keywords used when querying this source |
| `refresh_frequency` | selection | Hourly / Daily / Weekly / Manual |
| `auth_type` | selection | None / API Key / Basic Auth / OAuth2 / Custom Header |
| `auth_headers` | text | JSON: custom headers |
| `timeout` | integer | Request timeout in seconds |
| `max_articles` | integer | Maximum articles per sync |
| `trust_score` | float | 0.0–1.0; source reliability |
| `last_sync` | datetime | Last synchronization timestamp |
| `last_successful_sync` | datetime | Last successful sync |
| `sync_status` | selection | Idle / Running / Success / Error |
| `sync_error` | text | Last error message |
| `notes` | text | Internal notes |

### FR-06: Content Category (`social.content.category`)

| Field | Type | Purpose |
|-------|------|---------|
| `name` | char | Category name |
| `code` | char | Machine-readable code |
| `parent_id` | m2o → self | Parent category |
| `active` | boolean | Enable/disable |

### FR-07: AI Execution Log (`social.ai.log`)

Records every AI agent execution for audit:

| Field | Type | Purpose |
|-------|------|---------|
| `company_id` | m2o → res.company | Target company |
| `agent_id` | m2o → ai.agent | Which agent was called |
| `topic_id` | m2o → ai.topic | Which topic was used |
| `stage` | selection | Research / Generate / Dedup / Rewrite / Audit |
| `input_summary` | text | Summary of input context |
| `output_summary` | text | Summary of output |
| `full_input` | text | Complete input (capped at 10KB) |
| `full_output` | text | Complete output (capped at 10KB) |
| `duration_seconds` | float | Execution time |
| `status` | selection | Success / Failed / Skipped / Timeout |
| `error_message` | text | Error details if failed |
| `token_count_input` | integer | Tokens consumed |
| `token_count_output` | integer | Tokens consumed |
| `cost_estimate` | float | Estimated cost in provider currency |
| `create_date` | datetime | When logged |

### FR-08: Post Semantic Index (`social.post.embedding`)

Stores embeddings for semantic duplicate detection:

| Field | Type | Purpose |
|-------|------|---------|
| `post_id` | m2o → social.post | The published post |
| `company_id` | related | Company via post |
| `embedding` | binary | Vector embedding (1536-dim or similar) |
| `provider` | m2o → ai.provider | Which provider generated the embedding |
| `model` | char | Which embedding model was used |

### FR-09: Pipeline Stage Configuration (`social.pipeline.stage`)

Controls which stages execute per company:

| Field | Type | Purpose |
|-------|------|---------|
| `company_id` | m2o → res.company | Target company |
| `stage` | selection | Research / Generate / Dedup / Rewrite / Audit |
| `enabled` | boolean | Whether this stage runs |
| `sequence` | integer | Execution order |

---

## 4. Non-functional Requirements

### NFR-01: Performance

- Duplicate detection against 1 million posts shall complete in under 2 seconds using vector index.
- Single company pipeline execution shall complete in under 60 seconds (excluding AI API latency).
- AI execution logs shall be async — not blocking the pipeline.

### NFR-02: Scalability

- Support 10,000+ companies on a single Odoo instance.
- Support 10 million+ social.post records without query degradation.
- Embedding index shall support incremental updates (no full rebuild).

### NFR-03: Availability

- Pipeline failures for one company shall not affect other companies.
- Failed stages shall be retried with exponential backoff (3 attempts).
- AI provider unavailability shall not crash the pipeline — it shall log and skip.

### NFR-04: Security

- Companies shall never see other companies' Brand Profiles, Knowledge Sources, or AI logs.
- API keys stored in `ir.config_parameter` with encryption.
- AI execution logs shall be readable only by company administrators and the Social Marketing Manager group.

### NFR-05: Maintainability

- AI prompts shall be editable via Odoo UI (ai.topic records).
- Pipeline stages shall be reorderable via sequence field.
- New agents shall be pluggable without pipeline modification.
- All business logic shall be in server actions (auditable, no-code modification).

### NFR-06: Observability

- Every pipeline execution shall produce an AI log record.
- Dashboard showing: posts per day, duplicate rate, audit pass rate, AI cost.
- Activity feed for pipeline failures.

---

## 5. Architecture Overview

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Odoo 19 Enterprise                     │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────────┐   │
│  │ ir.cron  │──→│ Server   │──→│ AI Pipeline           │   │
│  │ Scheduler│   │ Action   │   │ Orchestrator          │   │
│  └──────────┘   │ (847)    │   └──────┬───────────────┘   │
│                 └──────────┘          │                    │
│                                       ▼                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Pipeline Stages (per company, sequential)          │   │
│  │                                                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │ Research │─→│Generate  │─→│Duplicate │         │   │
│  │  │ Agent    │  │Agent     │  │Review    │         │   │
│  │  └──────────┘  └──────────┘  └────┬─────┘         │   │
│  │                                   │                │   │
│  │                    ┌──────────────┼──────────┐     │   │
│  │                    ▼              ▼          ▼     │   │
│  │              [Duplicate]    [Not Duplicate]       │   │
│  │                    │              │                │   │
│  │              ┌──────────┐  ┌──────────┐          │   │
│  │              │Rewrite   │  │Quality   │          │   │
│  │              │Agent     │  │Audit     │          │   │
│  │              └──────────┘  └────┬─────┘          │   │
│  │                                 │                │   │
│  │                    ┌────────────┼──────────┐     │   │
│  │                    ▼            ▼          ▼     │   │
│  │              [Pass]       [Fail]                │   │
│  │                    │            │                │   │
│  │              social.post    Activity             │   │
│  │              (draft) +      "Audit Failed"      │   │
│  │              Review                                │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### Component Relationships

```
res.company (1) ──────── (1) social.company.ai.config
res.company (1) ──────── (1) social.brand.profile
res.company (1) ──────── (1) social.knowledge.catalog
social.knowledge.catalog (1) ──── (N) social.knowledge.source
social.knowledge.source (N) ──── (N) social.content.category
social.post (1) ──────── (1) social.post.embedding
social.company.ai.config (N) ──── (N) ai.agent (via agent fields)
social.company.ai.config (N) ──── (N) ai.topic (via pipeline stage config)
social.post (1) ──────── (N) social.ai.log
res.company (1) ──────── (N) social.ai.log
ai.agent (1) ──────── (N) social.ai.log
```

### Module Structure

```
social_ai_core/           # Base models, pipeline, configuration
social_ai_brand/          # Brand Profile, Industry
social_ai_knowledge/      # Knowledge Catalog, Sources, Categories
social_ai_pipeline/       # Pipeline orchestrator, stages, logs
social_ai_dedup/          # Semantic dedup, embedding storage
social_ai_audit/          # Quality audit
```

---

## 6. AI Pipeline

### Pipeline Orchestrator

A single `ir.actions.server` record acts as the orchestrator. It:

1. Queries `social.company.ai.config` for active companies.
2. For each company, reads `social.pipeline.stage` records ordered by `sequence`.
3. Executes each enabled stage sequentially.
4. Passes the output of each stage as input to the next.
5. Creates `social.ai.log` entries for each stage execution.
6. On failure at any stage, logs the error, creates an activity, and continues to the next company.

### Stage Input/Output Contract

| Stage | Input | Output |
|-------|-------|--------|
| Research | Brand Profile, Knowledge Sources, Industry | Research Result (text: headlines, articles, insights) |
| Generate Post | Research Result, Brand Profile, Platform, Language | Draft Content (title, body, hashtags, CTA) |
| Duplicate Review | Draft Content, Semantic Embedding, Post Embedding Index | Similarity Score, Verdict (Duplicate/Not Duplicate) |
| Rewrite | Draft Content, Brand Profile, Duplicate Reason | Regenerated Content or New Angle |
| Quality Audit | Final Content, Brand Profile, Platform Rules | Pass/Fail, Recommendations |

### Pipeline Context Dictionary

A Python dict passed through stages:

```python
context = {
    'company': company,            # res.company browse record
    'brand_profile': profile,      # social.brand.profile
    'config': ai_config,           # social.company.ai.config
    'sources': knowledge_sources,  # list of social.knowledge.source
    'industry': industry,          # social.industry
    'platforms': platforms,        # list of social.media.type
    'languages': languages,        # list of res.lang
    'stage_results': {},           # dict[stage_name] = result
    'ai_logs': [],                 # list of dicts for batch log creation
}
```

---

## 7. AI Agents

### Agent 1: Research Agent

| Property | Value |
|----------|-------|
| **Model** | `ai.agent` |
| **Name** | "Social Research Agent" |
| **Topic** | "Social Research" |
| **Role** | Collect and synthesize information from Knowledge Sources |
| **Input** | Brand Profile (structured), list of Knowledge Source descriptions |
| **Output** | Structured research result: 5-10 relevant articles with headlines, summaries, source attribution |
| **Constraints** | Never generates posts. Never compares to previous posts. Never audits. |

**Prompt Strategy (Topic instructions):**
```
Role: You are a research analyst for {company_name}.

Read the following Brand Profile and identify the company's industry, audience, products, and business goals.

Then, review the provided Knowledge Sources. For each source, extract the most relevant, timely, and interesting information that would be valuable to the company's audience.

Your output must:
- Be in the company's primary language: {primary_language}
- Include 5-10 distinct articles or insights
- For each: headline, 2-sentence summary, source attribution
- Prioritize information published in the last 7 days
- Exclude information already covered in previous posts (see dedup context)
```

### Agent 2: Post Generation Agent

| Property | Value |
|----------|-------|
| **Model** | `ai.agent` |
| **Name** | "Social Post Generator" |
| **Topic** | "Social Post Generation" |
| **Role** | Transform research into branded social posts |
| **Input** | Brand Profile, Research Result, Target Platform, Language |
| **Output** | Title, Content (platform-optimized), Hashtags, CTA, Image prompt |
| **Constraints** | Never receives previous posts. Only creates content from provided research. |

### Agent 3: Duplicate Review Agent

| Property | Value |
|----------|-------|
| **Model** | `ai.agent` |
| **Name** | "Social Duplicate Reviewer" |
| **Topic** | "Social Duplicate Review" |
| **Role** | Determine if generated content is semantically similar to historical posts |
| **Input** | Draft Content, List of top-5 most similar historical posts (retrieved via embedding) |
| **Output** | JSON: `{"duplicate": bool, "similarity_score": float, "reason": str, "recommendation": str}` |
| **Constraints** | Only compares ideas, not wording. Language-agnostic comparison. |

**Post-fetch logic (in orchestrator, not agent):**
- Generate embedding for new draft content.
- Query `social.post.embedding` with cosine similarity.
- Return top 5 most similar posts.
- Only invoke agent if similarity > configured threshold.

### Agent 4: Rewrite Agent

| Property | Value |
|----------|-------|
| **Model** | `ai.agent` |
| **Name** | "Social Post Rewriter" |
| **Topic** | "Social Post Rewrite" |
| **Role** | Regenerate content from a different angle without new research |
| **Input** | Original Draft, Brand Profile, Reason for rewrite, Available angles |
| **Output** | New Draft Content (different angle) or "NO_FRESH_ANGLE" |
| **Constraints** | Only requests new research if all 6 angles are exhausted. |

**Available rewrite angles:**
1. Different audience segment
2. Different business value proposition
3. Deeper technical insight
4. Broader industry trend
5. Case study / use case angle
6. Opinion / thought leadership angle

### Agent 5: Quality Audit Agent

| Property | Value |
|----------|-------|
| **Model** | `ai.agent` |
| **Name** | "Social Quality Auditor" |
| **Topic** | "Social Quality Audit" |
| **Role** | Final quality gate before review |
| **Input** | Final Draft, Brand Profile, Platform rules |
| **Output** | JSON: `{"pass": bool, "checks": [{"check": str, "status": str, "detail": str}], "overall_score": int}` |
| **Constraints** | Only audits — never modifies content. |

**Audit checks:**
| Check | Description |
|-------|-------------|
| Grammar | No spelling or grammar errors |
| Brand Voice | Matches brand voice and tone |
| Platform Compliance | Within character limits, format rules |
| Hashtag Quality | Relevant, not excessive, follows strategy |
| CTA Quality | Present and appropriate |
| Originality | Not plagiarized from sources |
| Factual Accuracy | No unsupported claims |
| Readability | Appropriate reading level |
| Language Compliance | In the correct language |
| Inclusivity | No problematic language |

---

## 8. AI Topics

Every AI Agent shall have its own `ai.topic` record. Topics are the single source of truth for prompt behavior.

| Topic Name | Agent | Editable Fields |
|------------|-------|-----------------|
| "Social Research" | Research Agent | `instructions` (prompt), `tool_ids` |
| "Social Post Generation" | Post Generator | `instructions`, `tool_ids` |
| "Social Duplicate Review" | Duplicate Reviewer | `instructions`, `tool_ids` |
| "Social Post Rewrite" | Rewrite Agent | `instructions`, `tool_ids` |
| "Social Quality Audit" | Quality Auditor | `instructions`, `tool_ids` |

Each topic's `instructions` field shall contain:
- Role definition
- Input specification
- Output specification
- Constraints and rules
- Example output format

Administrators shall be able to:
- Modify topic instructions via Settings > Technical > AI > Topics
- Test topics with sample input
- Version topics (compare before/after changes)

**No prompt shall exist inside Python code, server action code, or any non-database location.**

---

## 9. Brand Profile Design

### Purpose

Replace the current free-form `res.partner.comment` HTML field with a structured `social.brand.profile` model that AI agents can reliably parse and follow.

### Why Structured

| Free-form (current) | Structured (target) |
|---------------------|---------------------|
| AI must extract meaning from arbitrary HTML | AI reads known fields with defined semantics |
| No validation — anything can be entered | Field-level validation and tooltips |
| Hard to query (e.g., "all companies using Arabic") | Standard Odoo filters on any field |
| Brand voice not consistently applied | AI always sees the same structured context |
| Incomplete profiles silently produce bad posts | Required fields enforced |
| Similar companies require manual copy-paste | Industry defaults with company overrides |

### Industry Defaults

The `social.industry` model provides default values for:

- Default research queries
- Suggested keywords
- Common hashtags
- Typical audience personas
- Platform recommendations

When creating a new Brand Profile, industry defaults pre-fill the form. Companies can override any field.

### Integration with `res.partner.comment`

During migration, the existing `partner.comment` field is read once and used to populate the new Brand Profile. After migration, `partner.comment` is no longer used for brand configuration — it remains available for free-form internal notes.

### AI Consumption

The Brand Profile is serialized to a structured text block when passed to AI agents:

```
BRAND PROFILE FOR {company_name}
Industry: {industry.name}
Mission: {mission}
Target Audience: {target_audience}
Brand Voice: {brand_voice}
Tone: {tone}
Language: {languages}
Preferred Vocabulary: {preferred_vocabulary}
Forbidden Vocabulary: {forbidden_vocabulary}
CTA Style: {cta_style}
Hashtag Strategy: {hashtag_strategy}
...
```

---

## 10. Knowledge Catalog Design

### Purpose

Each company owns exactly one Knowledge Catalog containing zero or more Knowledge Sources. The Research Agent reads only enabled sources from the catalog.

### Why Per-Company Catalogs

- Prevents information leakage between companies.
- Allows industry-specific sources for each company.
- Enables source weighting (priority, trust_score) per company context.
- Supports multi-company environments where competitors must not share sources.

### Catalog Lifecycle

1. **Created**: Automatically when `social.company.ai.config` is created.
2. **Populated**: Administrator adds Knowledge Sources via UI.
3. **Enabled**: Catalog is active when the company AI config is active.
4. **Synchronized**: Sources are fetched per their `refresh_frequency`.
5. **Queried**: Research Agent reads catalog at pipeline start.

---

## 11. Knowledge Source Design

### Source Types

| Type | Description | Sync Method |
|------|-------------|-------------|
| `website` | Public web page | HTTP GET, extract text |
| `rss` | RSS/Atom feed | Parse XML, extract articles |
| `api` | REST/GraphQL API | Authenticated HTTP request |
| `document` | Internal document | Read from ir.attachment or document module |
| `youtube` | YouTube channel | YouTube Data API |
| `github` | GitHub repo/releases | GitHub API |

### Sync Strategy

Each source is synchronized independently via a scheduled action:

1. For sources with `refresh_frequency = 'hourly'`: synced every hour.
2. For `daily`: synced at a configurable time.
3. For `weekly`: synced on a configurable day.
4. For `manual`: only synced when administrator triggers it.

Sync results are cached in a transient model `social.knowledge.article`:

| Field | Type | Purpose |
|-------|------|---------|
| `source_id` | m2o | Source |
| `url` | char | Article URL |
| `title` | char | Article title |
| `summary` | text | Extracted summary |
| `published_date` | datetime | When article was published |
| `fetched_date` | datetime | When we fetched it |
| `relevance_score` | float | Relevance to company (computed) |

Articles older than 30 days are automatically purged.

### Relevance Scoring

When the Research Agent queries the catalog, articles are scored by:

1. **Recency**: 0.0–1.0 (newer = higher)
2. **Source Trust**: trust_score field (0.0–1.0)
3. **Source Priority**: priority field (normalized 0.0–1.0)
4. **Keyword Match**: overlap between article text and Brand Profile keywords

Final score = (recency * 0.3) + (trust * 0.2) + (priority * 0.2) + (keyword_match * 0.3)

Articles sorted by final score, top N passed to Research Agent.

---

## 12. Duplicate Detection Strategy

### Architecture

```
New Post Content
      │
      ▼
┌─────────────────┐
│ Generate         │  ai.agent._tool_generate_embedding() or API call
│ Embedding        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cosine Similarity│  SELECT embedding <=> $new_embedding
│ Search           │  FROM social_post_embedding
│ (PostgreSQL      │  WHERE company_id = $company_id
│  pgvector)       │  ORDER BY similarity DESC LIMIT 5
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Duplicate Review │  AI Agent compares new content vs top 5
│ Agent            │  Returns: {duplicate: bool, score: float}
└─────────────────┘
```

### Why Hybrid Approach

- **Vector similarity alone** is fast but imprecise — catches surface-level matches, misses conceptual duplicates.
- **AI comparison alone** is accurate but slow and expensive — cannot compare against millions of posts.
- **Hybrid**: Vector search narrows to top 5 candidates. AI does deep semantic comparison on just those 5.

### Embedding Storage

Use PostgreSQL `pgvector` extension for embedding storage:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The `social.post.embedding` model stores vectors as `vector(1536)` type.

### Incremental Indexing

When a post is published:
1. Generate embedding via configured `embedding_provider_id`.
2. Store in `social.post.embedding`.
3. Cron job runs every 15 minutes to index any un-indexed posts.

### Similarity Threshold

Configurable per company via `social.company.ai.config.similarity_threshold`:

- Default: 0.85
- Posts above threshold → flagged as duplicate → triggers Rewrite Agent
- Posts below threshold → proceed to Quality Audit

### Manual Override

The Review Activity shows the similarity score. Administrators can override the duplicate verdict and publish anyway.

---

## 13. Quality Audit Strategy

### Audit Execution

The Quality Audit Agent receives:

1. Final draft post content
2. Brand Profile (structured)
3. Platform rules (character limits, formatting requirements)
4. Original research sources (for fact-checking)

The agent returns a JSON verdict:

```json
{
  "pass": true,
  "overall_score": 87,
  "checks": [
    {"check": "Grammar", "status": "pass", "detail": "No errors found"},
    {"check": "Brand Voice", "status": "pass", "detail": "Matches professional tone"},
    {"check": "Platform Compliance", "status": "pass", "detail": "278 chars, under 280 limit"},
    {"check": "Hashtag Quality", "status": "pass", "detail": "3 relevant hashtags"},
    {"check": "CTA Quality", "status": "pass", "detail": "Engagement question present"},
    {"check": "Originality", "status": "pass", "detail": "Not directly copied from source"},
    {"check": "Factual Claims", "status": "warning", "detail": "Claims about market share unverified"},
    {"check": "Readability", "status": "pass", "detail": "Appropriate for business audience"},
    {"check": "Language", "status": "pass", "detail": "Arabic, formal register"},
    {"check": "Inclusivity", "status": "pass", "detail": "No issues"}
  ],
  "warnings": ["Factual Claims: market share claim should cite source"]
}
```

### Audit Outcomes

| Result | Action |
|--------|--------|
| **PASS** (score ≥ 70, no failures) | Create draft post + Review Activity |
| **PASS with Warnings** (score ≥ 70, warnings exist) | Create draft + include warnings in Review Activity note |
| **FAIL** (score < 70 or any check fails) | Create "Audit Failed" Activity on company; do not create post |

### Manual Review Integration

The Review Activity note includes:

- Full post content
- Audit result summary
- Similarity score (if applicable)
- Rewrite history (if applicable)
- AI execution log link

---

## 14. Odoo Models

### Reused Models (No Changes Required)

| Model | Purpose |
|-------|---------|
| `res.company` | Company entity |
| `res.partner` | Company contact |
| `res.lang` | Language configuration |
| `res.country` | Country configuration |
| `res.users` | User entity |
| `ai.agent` | AI agent definition |
| `ai.topic` | AI topic (prompt) definition |
| `ai.topic.tool` | AI tool definition |
| `social.post` | Social media post |
| `social.account` | Social media account |
| `social.media.type` | Social media platform types |
| `social.live.post` | Published social post |
| `mail.activity` | Activity record |
| `mail.activity.type` | Activity type definition |
| `ir.cron` | Scheduled action |
| `ir.actions.server` | Server action |
| `ir.attachment` | File attachment |
| `ir.config_parameter` | System parameters |
| `base.automation` | Automation rule |
| `utm.source` | UTM tracking |

### New Models

| Model | Module | Description |
|-------|--------|-------------|
| `social.company.ai.config` | social_ai_core | Per-company AI configuration |
| `social.brand.profile` | social_ai_brand | Structured brand guidelines |
| `social.industry` | social_ai_brand | Industry definitions |
| `social.knowledge.catalog` | social_ai_knowledge | Per-company knowledge catalog |
| `social.knowledge.source` | social_ai_knowledge | Knowledge source definition |
| `social.knowledge.article` | social_ai_knowledge | Cached/synced article |
| `social.content.category` | social_ai_knowledge | Content categorization |
| `social.ai.log` | social_ai_pipeline | AI execution audit log |
| `social.pipeline.stage` | social_ai_pipeline | Per-company pipeline stage config |
| `social.post.embedding` | social_ai_dedup | Semantic embedding storage |
| `social.audit.check` | social_ai_audit | Audit check definitions |
| `social.audit.result` | social_ai_audit | Per-post audit results |
| `social.ai.cost.tracking` | social_ai_core | AI token/cost aggregation |

### Model: `social.company.ai.config`

```python
_name = 'social.company.ai.config'
_description = 'Company AI Configuration'
_inherit = ['mail.thread', 'mail.activity.mixin']

company_id = fields.Many2one('res.company', required=True, ondelete='cascade')
active = fields.Boolean(default=True)
ai_provider_id = fields.Many2one('ai.provider', string='Primary AI Provider')
ai_model = fields.Selection(related='ai_provider_id.model_ids', string='AI Model')
temperature = fields.Float(default=0.7, help='0.0 = deterministic, 1.0 = creative')
language_ids = fields.Many2many('res.lang', string='Languages')
platform_ids = fields.Many2many('social.media.type', string='Publishing Platforms')
max_posts_per_day = fields.Integer(default=3)
review_required = fields.Boolean(default=True)
auto_publish = fields.Boolean(default=False)
similarity_threshold = fields.Float(default=0.85)
embedding_provider_id = fields.Many2one('ai.provider', string='Embedding Provider')
research_agent_id = fields.Many2one('ai.agent', string='Research Agent')
generation_agent_id = fields.Many2one('ai.agent', string='Generation Agent')
dedup_agent_id = fields.Many2one('ai.agent', string='Dedup Agent')
rewrite_agent_id = fields.Many2one('ai.agent', string='Rewrite Agent')
audit_agent_id = fields.Many2one('ai.agent', string='Audit Agent')
knowledge_catalog_id = fields.Many2one('social.knowledge.catalog')
brand_profile_id = fields.Many2one('social.brand.profile')
post_count_today = fields.Integer(compute='_compute_post_count_today')

_sql_constraints = [
    ('company_uniq', 'unique(company_id)', 'Each company can have only one AI configuration.')
]
```

### Model: `social.brand.profile`

```python
_name = 'social.brand.profile'
_description = 'Company Brand Profile'

company_id = fields.Many2one('res.company', required=True, ondelete='cascade')
active = fields.Boolean(default=True)
mission = fields.Text()
vision = fields.Text()
industry_id = fields.Many2one('social.industry')
products = fields.Text()
services = fields.Text()
target_audience = fields.Text()
customer_personas = fields.Text()
brand_voice = fields.Selection([
    ('professional', 'Professional'),
    ('casual', 'Casual'),
    ('technical', 'Technical'),
    ('inspirational', 'Inspirational'),
])
tone = fields.Selection([
    ('formal', 'Formal'),
    ('friendly', 'Friendly'),
    ('authoritative', 'Authoritative'),
    ('witty', 'Witty'),
])
writing_style = fields.Text()
preferred_vocabulary = fields.Text()
forbidden_vocabulary = fields.Text()
keywords = fields.Text()
competitors = fields.Text()
unique_selling_proposition = fields.Text()
language_ids = fields.Many2many('res.lang')
cta_style = fields.Text()
hashtag_strategy = fields.Text()
image_style = fields.Text()
formatting_rules = fields.Text()
platform_preferences = fields.Text()
business_goals = fields.Text()
example_posts = fields.Text()
notes = fields.Html()

_sql_constraints = [
    ('company_uniq', 'unique(company_id)', 'Each company can have only one brand profile.')
]
```

### Model: `social.industry`

```python
_name = 'social.industry'
_description = 'Social Media Industry'

name = fields.Char(required=True)
code = fields.Char(required=True)
keywords = fields.Text(help='Keywords used for auto-detection')
default_query = fields.Text(help='Default research query for this industry')
active = fields.Boolean(default=True)
```

---

## 15. User Interface

### 15.1 Company AI Configuration (Form View)

**Path:** Social Marketing > Configuration > Company AI Config

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  Company AI Configuration              [AzeezTech] [Edit]│
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ General ──────────────────────────────────────────┐ │
│  │ Company: AzeezTech                                  │ │
│  │ Active:  [✓]                                        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ AI Provider ──────────────────────────────────────┐ │
│  │ Primary Provider: [Google Gemini ▼]                 │ │
│  │ Model:             [gemini-2.5-flash ▼]             │ │
│  │ Temperature:       [──●────────] 0.7                │ │
│  │ Embedding Provider:[Google Gemini ▼]                │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Publishing ───────────────────────────────────────┐ │
│  │ Languages: [Arabic] [English]                       │ │
│  │ Platforms: [✓ Facebook] [✓ LinkedIn] [  Instagram]   │ │
│  │ Max Posts/Day: [3]                                  │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Review Workflow ──────────────────────────────────┐ │
│  │ [✓] Require Manual Review                           │ │
│  │ [  ] Auto-Publish (skip review)                     │ │
│  │ Similarity Threshold: [──●──────] 0.85              │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ AI Agents ────────────────────────────────────────┐ │
│  │ Research:    [Social Research Agent ▼]              │ │
│  │ Generation:  [Social Post Generator ▼]              │ │
│  │ Dedup:       [Social Duplicate Reviewer ▼]          │ │
│  │ Rewrite:     [Social Post Rewriter ▼]               │ │
│  │ Audit:       [Social Quality Auditor ▼]             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Pipeline Stages ──────────────────────────────────┐ │
│  │ ┌────┬──────────────────┬─────────┐                 │ │
│  │ │ Seq│ Stage            │ Enabled │                 │ │
│  │ ├────┼──────────────────┼─────────┤                 │ │
│  │ │ 10 │ Research         │   [✓]   │                 │ │
│  │ │ 20 │ Post Generation  │   [✓]   │                 │ │
│  │ │ 30 │ Duplicate Review │   [✓]   │                 │ │
│  │ │ 40 │ Rewrite          │   [✓]   │                 │ │
│  │ │ 50 │ Quality Audit    │   [✓]   │                 │ │
│  │ └────┴──────────────────┴─────────┘                 │ │
│  │                        [Add Stage]                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 15.2 Brand Profile (Form View)

**Path:** Social Marketing > Configuration > Brand Profiles

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  Brand Profile: AzeezTech                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ Identity ─────────────────────────────────────────┐ │
│  │ Company:  AzeezTech                                 │ │
│  │ Industry: [Technology ▼]                            │ │
│  │ Mission:  [________________________________]        │ │
│  │ Vision:   [________________________________]        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Products & Services ──────────────────────────────┐ │
│  │ Products: [AI solutions, app development...]        │ │
│  │ Services: [Digital transformation consulting...]    │ │
│  │ USP:      [Enterprise AI for the Arab market]       │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Audience ─────────────────────────────────────────┐ │
│  │ Target:      [Business decision-makers in MENA]     │ │
│  │ Personas:    [CTOs, CEOs, Digital Directors...]     │ │
│  │ Competitors: [Local AI consulting firms...]         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Voice & Style ────────────────────────────────────┐ │
│  │ Brand Voice:    [Professional ▼]                    │ │
│  │ Tone:           [Authoritative ▼]                   │ │
│  │ Writing Style:  [Formal Arabic with English terms]  │ │
│  │ CTA Style:      [Thought-provoking questions]       │ │
│  │ Hashtag Stgy:   [3-5 Arabic + 1-2 English]         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Vocabulary ───────────────────────────────────────┐ │
│  │ Preferred: [الذكاء الاصطناعي, تحول رقمي, ابتكار]    │ │
│  │ Forbidden: [cheap, discount, free, guarantee]       │ │
│  │ Keywords:  [AI, digital transformation, enterprise] │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Language & Platform ──────────────────────────────┐ │
│  │ Languages: [Arabic (Primary)] [English]             │ │
│  │ Platform Prefs: [FB: long-form | LI: professional]  │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Examples ─────────────────────────────────────────┐ │
│  │ Example Posts: [Previous good post ...]             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 15.3 Knowledge Catalog (Kanban + Form)

**Path:** Social Marketing > Knowledge > Catalogs

Kanban view shows each company's catalog with source count, last sync status, and quick sync button.

Form view shows:
- Company name
- Source list (editable tree)
- Bulk actions: Sync All, Disable All, Test All
- Sync status dashboard (pie: success/error/pending)

### 15.4 Knowledge Source (Form View)

```
┌─────────────────────────────────────────────────────────┐
│  Knowledge Source: TechCrunch AI                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Name:        [TechCrunch AI Section]                    │
│  Type:        [Website ▼]                                │
│  URL:         [https://techcrunch.com/category/ai/]      │
│  Description: [Latest AI startup news and funding]       │
│                                                          │
│  ┌─ Settings ──────────────────────────────────────────┐│
│  │ Active:         [✓]                                 ││
│  │ Priority:       [70 ──●──────] 70/100               ││
│  │ Trust Score:    [80 ───●─────] 80/100               ││
│  │ Max Articles:   [10]                                ││
│  │ Timeout:        [30] seconds                        ││
│  │ Language:       [English ▼]                         ││
│  │ Country:        [United States ▼]                   ││
│  │ Categories:     [AI] [Startups] [Technology]        ││
│  │ Search Keywords:[AI startup, funding, LLM, agent]   ││
│  │ Refresh:        [Daily ▼]                           ││
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Authentication ────────────────────────────────────┐│
│  │ Type: [None ▼]                                      ││
│  │ (or: API Key, Basic Auth, OAuth2, Custom Header)    ││
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Sync Status ──────────────────────────────────────┐ │
│  │ Status:      ● Success                              │ │
│  │ Last Sync:   2026-07-20 08:00:00                    │ │
│  │ Last Success: 2026-07-20 08:00:00                   │ │
│  │ Articles:    10 fetched / 8 new / 2 updated         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Notes ────────────────────────────────────────────┐ │
│  │ [Internal notes about this source...]               │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│                      [Sync Now] [Test Connection]        │
└─────────────────────────────────────────────────────────┘
```

### 15.5 AI Execution Log (Tree + Form)

**Path:** Social Marketing > AI > Execution Logs

Tree view with filters by company, agent, stage, status, and date.

Form view shows:
- Full input/output (with syntax highlighting for JSON)
- Duration, token count, cost estimate
- Link to resulting social.post (if applicable)
- Link to resulting activity (if applicable)

### 15.6 AI Dashboard (Kanban/Graph)

**Path:** Social Marketing > AI > Dashboard

Metrics:
- Posts created today (per company)
- Success rate (passed/total)
- Duplicate detection rate
- Average similarity score
- AI cost today
- Audit pass rate
- Average pipeline duration

Charts:
- Posts per day (line chart, last 30 days)
- Audit scores distribution (bar chart)
- Token usage per agent (pie chart)
- Pipeline stage durations (Gantt)

---

## 16. Configuration Menus

```
Social Marketing
├── Posts
│   ├── Social Posts
│   ├── Scheduled Posts
│   └── Live Posts
├── Accounts
│   └── Social Accounts
├── AI
│   ├── Dashboard
│   ├── Execution Logs
│   ├── Agents
│   ├── Topics
│   └── Tools
├── Knowledge
│   ├── Catalogs
│   ├── Sources
│   └── Articles
├── Brand
│   ├── Brand Profiles
│   ├── Industries
│   └── Content Categories
├── Pipeline
│   ├── Pipeline Stages
│   └── Scheduled Actions
└── Configuration
    ├── Company AI Config
    ├── Activity Types
    └── Audit Checks
```

---

## 17. Scheduled Actions

| # | Name | Model | Interval | Purpose |
|---|------|-------|----------|---------|
| 1 | AI Social Pipeline: Run | ir.cron | Daily (configurable per company) | Triggers pipeline orchestrator |
| 2 | Knowledge Source Sync (Hourly) | ir.cron | Every hour | Syncs hourly-priority sources |
| 3 | Knowledge Source Sync (Daily) | ir.cron | Daily at 06:00 | Syncs daily-priority sources |
| 4 | Knowledge Source Sync (Weekly) | ir.cron | Weekly on Sunday 03:00 | Syncs weekly-priority sources |
| 5 | Post Embedding Indexer | ir.cron | Every 15 minutes | Indexes un-indexed published posts |
| 6 | AI Log Cleanup | ir.cron | Daily at 02:00 | Archives logs older than 90 days |
| 7 | Knowledge Article Cleanup | ir.cron | Daily at 03:00 | Purges articles older than 30 days |
| 8 | AI Cost Aggregation | ir.cron | Daily at 01:00 | Aggregates per-company cost tracking |
| 9 | Social: Publish Scheduled Posts | ir.cron | Every hour | Built-in: publishes due posts |

### Per-Company Schedule

Cron #1 can be overridden per company:

- Each `social.company.ai.config` can specify a custom `posting_schedule` (cron expression or selection: Daily 8AM, Daily 8PM, Twice Daily, etc.)
- The pipeline orchestrator only processes companies whose schedule matches the current time window.
- Companies with `max_posts_per_day` reached are skipped.

---

## 18. Activities

| Activity Type | Model | Summary Template | Trigger Condition |
|---------------|-------|------------------|-------------------|
| Review Draft | social.post | "Review: {company} post" | Post created, review_required=True |
| Rewrite Requested | social.post | "Rewrite: {company} post" | Duplicate Review returned duplicate=True |
| Audit Failed | social.company.ai.config | "Audit Failed: {company}" | Quality Audit returned FAIL |
| Research Failed | social.company.ai.config | "Research Failed: {company}" | Research Agent failed (no results, error) |
| Manual Approval | social.post | "Approve: {company} post" | Post passed audit, review_required=True |
| Publication Reminder | social.post | "Scheduled: {company} post" | Post scheduled, 1 hour before publication |
| Knowledge Sync Error | social.knowledge.source | "Sync Error: {source}" | Source sync failed |
| AI Quota Warning | social.company.ai.config | "AI Quota: {company}" | Token usage > 80% of daily limit |

All activity types shall use `mail.activity.type` with appropriate icons and default deadlines.

---

## 19. Security Groups

| Group | Category | Inherits | Purpose |
|-------|----------|----------|---------|
| Social Marketing / User | social_marketing | - | Read published posts, view accounts |
| Social Marketing / Manager | social_marketing | User | Create posts, manage accounts, review |
| Social Marketing / AI Operator | social_marketing | Manager | Configure AI, manage pipeline, view costs |
| Social Marketing / Administrator | social_marketing | AI Operator | Full access: brand profiles, knowledge catalogs, agents |

### Permissions Matrix

| Model | User | Manager | AI Operator | Admin |
|-------|------|---------|-------------|-------|
| social.post | read | create,write,unlink | create,write,unlink | all |
| social.account | read | create,write | create,write | all |
| social.company.ai.config | - | read | create,write | all |
| social.brand.profile | - | read | create,write | all |
| social.knowledge.catalog | - | read | create,write | all |
| social.knowledge.source | - | read | create,write | all |
| social.knowledge.article | - | read | read | all |
| social.ai.log | - | read (own company) | read | all |
| social.post.embedding | - | - | read | all |
| social.pipeline.stage | - | - | create,write | all |
| ai.agent | - | - | create,write | all |
| ai.topic | - | - | create,write | all |

---

## 20. Record Rules

### Multi-Company Isolation

All models with `company_id` shall have record rules ensuring:

- Users only see records belonging to their allowed companies.
- Company-less records (no `company_id` set) are visible to all (for shared configuration).

### Examples

```xml
<!-- social.company.ai.config: only own companies -->
<record id="rule_ai_config_multi_company" model="ir.rule">
    <field name="name">AI Config: multi-company</field>
    <field name="model_id" ref="model_social_company_ai_config"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>

<!-- social.ai.log: only own company logs -->
<record id="rule_ai_log_multi_company" model="ir.rule">
    <field name="name">AI Log: multi-company</field>
    <field name="model_id" ref="model_social_ai_log"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

---

## 21. Multi-company Behavior

### Company Scoping

All social AI models shall have a `company_id` field that inherits from `res.company`:

- `social.company.ai.config`
- `social.brand.profile`
- `social.knowledge.catalog`
- `social.ai.log`
- `social.post.embedding` (related via post)
- `social.pipeline.stage`

### Pipeline Execution

The pipeline orchestrator:
1. Runs as the `Administrator` user (or a dedicated system user).
2. Iterates all active `social.company.ai.config` records (regardless of company).
3. For each company, switches to that company's context before executing stages.
4. If a stage fails, continues to the next company (no cross-company contamination).

### AI Agents

AI agents are global (no `company_id`) but receive company-specific context (Brand Profile, Knowledge Sources). This prevents company data leakage through agent configuration.

---

## 22. User Flows

### Flow 1: Administrator — Initial Setup

```
1. Install social_ai_* modules
2. Google Gemini API key already configured (Settings > Parameters)
3. Navigate to Social Marketing > Configuration > Company AI Config
4. Create AI config for AzeezTech:
   a. Select provider, model, temperature
   b. Select languages (Arabic, English)
   c. Select platforms (Facebook, LinkedIn)
   d. Assign AI agents (default agents auto-created)
   e. Set max posts/day = 2
   f. Enable review_required
5. Navigate to Social Marketing > Brand > Brand Profiles
6. Create brand profile for AzeezTech:
   a. Fill industry, mission, audience
   b. Set brand voice = Professional, tone = Authoritative
   c. Specify Arabic as primary language
   d. Set hashtag strategy
7. Navigate to Social Marketing > Knowledge > Catalogs
8. Add knowledge sources for AzeezTech:
   a. TechCrunch AI section (daily)
   b. The Verge AI (daily)
   c. Hacker News (daily)
9. Wait for next cron run or manually trigger pipeline
10. Review generated draft post in Activities
11. Mark Activity Done to schedule
12. Post published automatically by scheduled action
```

### Flow 2: Administrator — Daily Review

```
1. Open Activities panel
2. See "Review: AzeezTech post" activity
3. Open activity → view post content, audit results, similarity score
4. Options:
   a. Accept → Mark Done → post scheduled
   b. Reject → Mark Done (with feedback) → new Research triggered
   c. Rewrite → Click "Rewrite" button → new draft generated
   d. Edit → Open social.post → modify content → save → Mark Done
5. Post appears in Scheduled Posts
6. Post published by built-in social cron
```

### Flow 3: AI Operator — Monitoring

```
1. Navigate to Social Marketing > AI > Dashboard
2. Review:
   - Posts per company today
   - Audit pass rate
   - Duplicate detection rate
   - AI cost
3. Click on problematic entries → drill down to AI Execution Log
4. Review full input/output of failed stages
5. Adjust configuration:
   - Increase temperature for more creative posts
   - Lower similarity threshold for stricter dedup
   - Disable problematic knowledge source
6. Re-trigger pipeline for affected company
```

### Flow 4: Adding a New Company

```
1. Create res.company with partner and social accounts
2. Navigate to Social Marketing > Configuration > Company AI Config
3. Click "Generate from Industry" → select industry
4. All fields pre-filled with industry defaults
5. Adjust language, platforms, max posts/day
6. Navigate to Brand Profile → auto-created with industry defaults
7. Customize brand voice, audience, vocabulary
8. Add knowledge sources (copy from similar company or create new)
9. Pipeline automatically discovers new company on next cron run
```

---

## 23. Sequence Diagrams

### Pipeline Execution Sequence

```
Scheduler          Orchestrator       Research Agent     Generate Agent    Dedup Agent    Rewrite Agent    Audit Agent
    │                   │                   │                  │               │               │               │
    │ Trigger cron      │                   │                  │               │               │               │
    │──────────────────→│                   │                  │               │               │               │
    │                   │                   │                  │               │               │               │
    │                   │ Load Companies    │                  │               │               │               │
    │                   │─────────────┐     │                  │               │               │               │
    │                   │             │     │                  │               │               │               │
    │                   │◄────────────┘     │                  │               │               │               │
    │                   │                   │                  │               │               │               │
    │                   │ For each company: │                  │               │               │               │
    │                   │                   │                  │               │               │               │
    │                   │ Load Config +     │                  │               │               │               │
    │                   │ Brand + Sources   │                  │               │               │               │
    │                   │                   │                  │               │               │               │
    │                   │──Stage 1: Research│                  │               │               │               │
    │                   │──────────────────→│                  │               │               │               │
    │                   │                   │ Read Sources     │               │               │               │
    │                   │                   │───────────┐      │               │               │               │
    │                   │                   │           │      │               │               │               │
    │                   │                   │◄──────────┘      │               │               │               │
    │                   │   Research Result  │                  │               │               │               │
    │                   │◄──────────────────│                  │               │               │               │
    │                   │                   │                  │               │               │               │
    │                   │──Stage 2: Generate│                  │               │               │               │
    │                   │─────────────────────────────────────→│               │               │               │
    │                   │                   │                  │ Create Post   │               │               │
    │                   │   Draft Content   │                  │───────────┐   │               │               │
    │                   │◄─────────────────────────────────────│           │   │               │               │
    │                   │                   │                  │◄──────────┘   │               │               │
    │                   │                   │                  │               │               │               │
    │                   │──Stage 3: Dedup ──────────────────────────────────────│               │               │
    │                   │──────────────────────────────────────────────────────→│               │               │
    │                   │                   │                  │   Embedding    │               │               │
    │                   │                   │                  │   search top 5 │               │               │
    │                   │   {duplicate: F}  │                  │               │               │               │
    │                   │◄──────────────────────────────────────────────────────│               │               │
    │                   │                   │                  │               │               │               │
    │                   │──Stage 5: Audit ───────────────────────────────────────────────────────────────│
    │                   │───────────────────────────────────────────────────────────────────────────────→│
    │                   │   {pass: T, 85}   │                  │               │               │               │
    │                   │◄───────────────────────────────────────────────────────────────────────────────│
    │                   │                   │                  │               │               │               │
    │                   │ Create social.post│                  │               │               │               │
    │                   │ Create Activity   │                  │               │               │               │
    │                   │ Create AI Log     │                  │               │               │               │
    │                   │                   │                  │               │               │               │
    │                   │ Next company...   │                  │               │               │               │
```

### Dedup with Rewrite Sequence

```
Orchestrator              Dedup Agent                Rewrite Agent
    │                          │                           │
    │ Stage 3: Dedup           │                           │
    │─────────────────────────→│                           │
    │                          │ Compare vs top 5 posts    │
    │                          │───────────┐               │
    │                          │◄──────────┘               │
    │  {duplicate: true,       │                           │
    │   similarity: 0.92,      │                           │
    │   reason: "Same topic:   │                           │
    │   Agentic AI in business"}                           │
    │◄─────────────────────────│                           │
    │                          │                           │
    │ Stage 4: Rewrite         │                           │
    │─────────────────────────────────────────────────────→│
    │                          │                           │ Try angle 1 (different audience)
    │                          │                           │───────────┐
    │                          │                           │◄──────────┘
    │  New Draft (angle 1)     │                           │
    │◄─────────────────────────────────────────────────────│
    │                          │                           │
    │ Stage 3: Dedup (retry)   │                           │
    │─────────────────────────→│                           │
    │  {duplicate: false}      │                           │
    │◄─────────────────────────│                           │
    │                          │                           │
    │ Continue to Stage 5...   │                           │
```

---

## 24. Error Handling

### Error Categories

| Category | Example | Response |
|----------|---------|----------|
| **AI Provider Unavailable** | Gemini API returns 503 | Skip company, create activity, retry next cycle |
| **Knowledge Source Down** | Source URL returns 404 | Log error, disable source, create activity |
| **Quota Exceeded** | Gemini returns rate_limit | Skip pipeline for all companies, create alert activity |
| **Empty Research** | No articles found | Skip company, create activity "No news today" |
| **All Angles Exhausted** | Rewrite tried 6 angles, all duplicates | Skip company, log "NO_FRESH_ANGLE" |
| **Audit Failed** | Score < 70 | Create activity "Audit Failed" with details |
| **Embedding Failed** | Embedding provider down | Fall back to text-only dedup (200-char check) |
| **Timeout** | Agent takes > 60s | Retry once, then skip + log error |

### Retry Strategy

- Transient errors (503, timeout): retry up to 3 times with exponential backoff (5s, 25s, 125s).
- Permanent errors (404, 401): do not retry — log and alert.
- Quota errors: stop pipeline entirely for the current cycle.

### Alert Activity Format

```
Summary: ⚠️ {Category}: {Company Name}
Note:
  {Error details}
  
  Possible causes:
  - {cause 1}
  - {cause 2}
  
  Recommended action:
  {action}
```

---

## 25. Performance Strategy

### Database

1. **Indexing**: Index `company_id`, `state`, `create_date` on `social.post`. Index `company_id` on all new models.
2. **pgvector**: Use PostgreSQL `pgvector` extension with IVFFlat index for cosine similarity search.
3. **Partitioning**: Partition `social.ai.log` by month for historical queries.
4. **Materialized Views**: Pre-compute daily metrics (posts per company, cost per company).

### AI Execution

1. **Batching**: Pipeline processes one company at a time (no parallel AI calls).
2. **Caching**: Brand Profile and Knowledge Sources cached per pipeline run.
3. **Embedding cache**: Don't re-embed the same content if retrying dedup.
4. **Token budget**: Per-company token budget enforced by `max_posts_per_day`.

### Background Processing

1. Knowledge source syncs run in background (separate cron from pipeline).
2. Embedding indexer runs every 15 minutes (separate from pipeline).
3. AI log creation uses deferred writes (batch insert per pipeline run).

---

## 26. Scalability Strategy

### Horizontal

- Pipeline orchestrator is stateless — multiple Odoo workers can process different companies simultaneously.
- Embedding search is PostgreSQL-native — scales with pgvector's IVFFlat index.
- Knowledge source syncs are independent — parallel processing supported.

### Vertical

- Increase PostgreSQL `work_mem` for embedding search.
- Consider pgvector HNSW index for 1M+ embeddings.
- Consider offloading embedding generation to a dedicated service.

### Bottleneck Mitigation

| Bottleneck | Mitigation |
|------------|------------|
| AI API rate limits | Queue system; per-company throttle |
| Embedding search | pgvector IVFFlat → HNSW index at scale |
| Log storage growth | Auto-archive logs > 90 days; partition by month |
| Knowledge sync volume | Incremental sync; per-source max_articles |
| Pipeline duration | Skip companies with max_posts_per_day reached |

---

## 27. Extensibility Strategy

### Adding a New AI Agent

1. Create new `ai.agent` record.
2. Create corresponding `ai.topic` record.
3. Add a `social.pipeline.stage` record pointing to the new agent.
4. Add a `social.stage.handler` that defines how input/output maps to pipeline context.

**No pipeline code changes required.**

### Adding a New Knowledge Source Type

1. Add new `source_type` selection value to `social.knowledge.source`.
2. Implement a sync handler (a Python function registered in `social.source.handler` registry).
3. Configure the handler via `source_type` → handler mapping.

### Adding a New Audit Check

1. Create a `social.audit.check` record.
2. Configure `check_type`, `severity`, `pass_threshold`.
3. Audit Agent automatically picks up new checks via its topic instructions.

### Adding a New Capability (Image Generation, SEO, etc.)

1. Register a new `ir.actions.server` that calls the agent with appropriate context.
2. Add a pipeline stage that invokes the new action.
3. If the capability should run in the main pipeline, add the stage between existing stages.
4. If the capability is standalone, create a separate cron + action.

---

## 28. Migration Strategy

### Phase 1: Foundation (Week 1-2)

1. Create new models (`social.company.ai.config`, `social.brand.profile`, `social.industry`, `social.knowledge.catalog`, `social.knowledge.source`, `social.ai.log`, `social.pipeline.stage`).
2. Install `pgvector` extension.
3. Create security groups and record rules.
4. Create default industry records (Technology, Sports, Healthcare, Finance, Education, E-commerce).
5. Create default AI agents and topics (5 agents + 5 topics).

### Phase 2: Pipeline (Week 3-4)

1. Create pipeline orchestrator (server action replacing monolithic #845).
2. Migrate existing brand guidelines from `partner.comment` → `social.brand.profile`.
3. Create knowledge sources from existing hardcoded URLs.
4. Create `social.post.embedding` model and indexer.
5. Backfill embeddings for existing published posts.

### Phase 3: Dual-Run (Week 5)

1. Run v1.0 (action #845, cron #54) and v2.0 pipeline in parallel.
2. Compare outputs: draft content, dedup decisions, audit results.
3. Validate that v2.0 produces equal or better quality posts.
4. Administrators review v2.0 posts side-by-side with v1.0.

### Phase 4: Cutover (Week 6)

1. Deactivate cron #54 (v1.0).
2. Activate cron for v2.0 pipeline.
3. Monitor for 48 hours.
4. Archive v1.0 components (keep for reference, not delete).

### Phase 5: Cleanup (Week 7)

1. Remove hardcoded industry detection from v1.0 action.
2. Remove `partner.comment` dependency from all actions.
3. Document migration in user-facing documentation.

---

## 29. Backward Compatibility Strategy

### What Is Preserved

- `social.post` model unchanged — all existing posts remain.
- `social.account` model unchanged — all accounts remain.
- `social.live.post` model unchanged.
- `mail.activity` — same Activity Types used in v1.0.
- `ir.cron` — v1.0 cron #54 deactivated but preserved.
- `ir.actions.server` — v1.0 actions (#845, #849, #850) deactivated but preserved.
- `base.automation` — v1.0 rule #2 deactivated but preserved.

### What Is Changed

- Brand guidelines move from `partner.comment` to `social.brand.profile`.
- Industry detection moves from inline code to `social.industry` model.
- Knowledge sources move from hardcoded URLs to `social.knowledge.source`.
- Dedup moves from text comparison to embedding-based semantic comparison.

### No-Break Guarantee

- Module installation does NOT modify existing models (additive only).
- v1.0 pipeline continues to function if not explicitly disabled.
- Existing posts, accounts, and published content are untouched.

---

## 30. Testing Strategy

### Unit Tests

- Model creation, validation, constraints.
- Company isolation (record rules).
- Pipeline stage execution (mock AI agents).
- Embedding CRUD operations.

### Integration Tests

- End-to-end pipeline with mock AI provider.
- Knowledge source sync with local test files.
- Duplicate detection with pre-seeded embeddings.
- Activity creation and automation triggers.
- Multi-company isolation verification.

### Test Scenarios

| Scenario | Expected Result |
|----------|-----------------|
| Company with no knowledge sources | Research returns empty → skip |
| Company with 0 max_posts_per_day | Skipped |
| Research returns 2 articles | Post generated with 2 insights |
| Duplicate detected (0.95 similar) | Rewrite Agent invoked |
| Rewrite exhausts 6 angles | NO_FRESH_ANGLE → skip |
| Audit returns score 45 | Activity "Audit Failed" created |
| AI provider returns 503 | Retry 3x, then skip + alert |
| Audit returns warnings | Draft created with warnings in note |

---

## 31. Documentation Plan

### Internal Documentation

| Document | Audience |
|----------|----------|
| Technical Architecture (this document) | Development team |
| Module API Reference | Developers extending the platform |
| Agent Prompt Engineering Guide | AI Operators |
| Deployment Guide | DevOps/System Administrators |

### User Documentation

| Document | Audience |
|----------|----------|
| AI Social Marketing User Guide | Social Marketing / Manager |
| AI Configuration Guide | AI Operator / Administrator |
| Brand Profile Best Practices | All users |
| Troubleshooting Guide | AI Operator |

---

## 32. Future Roadmap

### Phase 2 (Q3 2026)

- **Image Generation Agent**: Generate platform-optimized images using DALL-E / Imagen.
- **Multi-Platform Post Variants**: Generate unique content per platform from one research pass.
- **A/B Testing**: Generate multiple post variants and auto-select best performer.

### Phase 3 (Q4 2026)

- **Analytics Feedback Loop**: Use engagement metrics to tune generation and topics.
- **Automated Customer Replies**: AI agent that responds to comments on published posts.
- **Trend Prediction Agent**: Identify emerging topics before they trend.

### Phase 4 (2027)

- **Multilingual Pipeline**: Research in one language, generate posts in multiple languages from same research.
- **Podcast/Video Script Agent**: Generate scripts for multimedia content.
- **Cross-Company Insights**: Anonymous industry benchmarking across companies.
- **White-Label Portal**: Reseller-friendly configuration interface.

---

## Appendix A: Existing Implementation Inventory

### Currently Deployed (v1.0)

| Component | ID | Name | Status |
|-----------|----|------|--------|
| ai.agent | 14 | Social Media Agent | Active |
| ai.topic | 13 | Social Content Posting | Active |
| ir.actions.server | 845 | AI Social News: Dynamic Multi-Company | Active |
| ir.actions.server | 849 | Auto Schedule on Activity Done | Active |
| ir.actions.server | 850 | Rewrite with AI | Active |
| base.automation | 2 | Social Post: Schedule on Review Done | Active |
| mail.activity.type | 9 | Social Post Review | Active |
| ir.cron | 54 | AI Social News: Dynamic Post at 8PM | Active |

### Currently Deployed (Odoo Built-in)

| Component | ID | Name |
|-----------|----|------|
| ir.cron | 15 | Social: Publish Scheduled Posts |
| ir.actions.server | 167 | Social: Publish Scheduled Posts |

### Migration Mapping

| v1.0 Component | v2.0 Replacement |
|----------------|------------------|
| `partner.comment` (unstructured) | `social.brand.profile` (structured) |
| Hardcoded industry detection | `social.industry` model |
| Hardcoded web search URLs | `social.knowledge.source` |
| Monolithic action #845 | Pipeline orchestrator + 5 agent actions |
| Single topic #13 | 5 dedicated topics (one per agent) |
| Text-based dedup | Embedding-based semantic dedup |
| No quality check | Quality Audit Agent |
| No execution logs | `social.ai.log` |

---

**Document Status:** Complete Draft — Awaiting Review  
**Next Steps:** Stakeholder review, technical feasibility assessment, sprint planning.
