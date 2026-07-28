# AzeezTech MVP — Implementation Inventory

**Principle:** Reuse existing Odoo capabilities first. Extend only when a genuine gap exists.

---

## Part 1: Inventory of Existing Capabilities

### 1.1 Existing Odoo Models We Reuse

| Model | Purpose in MVP | Status | Notes |
|-------|---------------|--------|-------|
| `knowledge.article` | Stores all AzeezTech brand, product, service, and strategy knowledge | Installed | Hierarchical articles with HTML body, parent/child structure. The "brain" of the company. |
| `knowledge.article.thread` | Discussion threads on knowledge articles | Installed | For collaboration on content |
| `ai.agent` | Defines Research Agent and Post Generation Agent | Installed | System prompt, model, style, topic assignment |
| `ai.agent.source` | Links Knowledge Articles and URL sources to agents | Installed | Supports `type='knowledge_article'` (via `article_id`) and `type='url'` (via `url`). This is the **key connector** between Knowledge and AI. |
| `ai.topic` | Defines AI behavior for research and generation | Installed | `instructions` field contains the prompt. Tools assigned via `tool_ids`. |
| `ai.topic.tool` | Links `ir.actions.server` tools to topics | Installed | Each topic can have multiple tools (web search, etc.) |
| `social.post` | Stores generated draft posts | Installed | `state` field: draft → scheduled → posted |
| `social.account` | Connected social media accounts for AzeezTech | Installed | AzeezTech has: Facebook (#11, connected), YouTube (#10, connected), Instagram (#12, disconnected), LinkedIn (#15, disconnected), TikTok (#54, disconnected) |
| `social.live.post` | Published post records per platform | Installed | Created by publishing cron |
| `social.media.type` | Social platform definitions | Installed | Facebook, Instagram, LinkedIn, YouTube, TikTok, etc. |
| `mail.activity` | Review activities on draft posts | Installed | Standard Odoo review workflow |
| `mail.activity.type` | "Social Post Review" activity type | Installed | Type #9, icon fa-check-circle, decoration warning, model social.post |
| `mail.mail` | Email notifications (optional for MVP) | Installed | Can send review notifications |
| `ir.cron` | Scheduled actions | Installed | Publishing cron already exists |
| `ir.actions.server` | Pipeline orchestration | Installed | Server action #845 will be refactored |
| `base.automation` | Triggers action on activity Done | Installed | Rule #2 already configured |
| `res.company` | AzeezTech company entity | Installed | ID #5 |
| `res.partner` | AzeezTech partner record | Installed | ID #18, linked to company |
| `ir.config_parameter` | Global system parameters | Installed | API keys, configuration |
| `utm.source` | UTM campaign tracking | Installed | For tracking social post performance |

### 1.2 Existing AI Components We Reuse

| Component ID | Name | Reuse in MVP | Notes |
|-------------|------|-------------|-------|
| Agent #14 | Social Media Agent | **System prompt may be simplified** | Currently has mixed responsibilities. For MVP, this agent could become either the Research or Generation agent. Its system prompt needs cleanup — remove content format rules, keep only role definition. |
| Topic #13 | Social Content Posting | **Split into two topics** | Current topic has both research instructions and generation instructions. Will be replaced by two dedicated topics. |
| Tool #835 | AI: Web Search | **Reused by Research Agent** | `record._tool_web_search(ai, query, retrieval_mode, context_hint)` — this is the core AI invocation method. No changes needed. |
| Tool #838 | AI Social News Generator | **Not reused** | Legacy tool using agent #9. Will be deactivated or removed. |
| Tool #664 | AI: Add Tags | **Not reused** | Document tagging tool, not relevant to social posting. |
| Agent Source URLs | 6 URL sources (TechCrunch, Hacker News, The Verge AI, BBC Sport, CBS Sports, Sky Sports) | **Reused by Research Agent** | Already indexed and active. Some may be removed (sports sources not needed for AzeezTech). |
| Action #849 | Auto Schedule on Activity Done | **Reused as-is** | No changes needed. Triggered by automation rule #2. |
| Action #850 | Rewrite with AI | **Not reused in MVP** | Inconsistency bugs make it unreliable. Will be replaced by the new pipeline or updated. |

### 1.3 Existing Workflows We Reuse

| Workflow | Reuse in MVP | Notes |
|----------|-------------|-------|
| **Agent sources → AI consumption** | Core — Knowledge Articles linked via `ai.agent.source(type='knowledge_article')` are automatically available to the agent during execution | This is the mechanism that makes Knowledge the company's brain. |
| **_tool_web_search invocation** | Core — Research Agent calls `_tool_web_search(ai, query, 'web', context_hint)` with context assembled from Knowledge | No changes to the method signature needed. |
| **Activity schedule + Done → schedule** | Core — `post.activity_schedule(activity_type_id=9)` creates review; marking Done triggers automation | Fully working today. No changes needed. |
| **Automation rule → server action** | Core — Rule #2 on `mail.activity` write triggers action #849 | Working as designed. No changes needed. |
| **Cron publish scheduled posts** | Core — Cron #15 publishes due posts hourly | Built-in Odoo functionality. No changes needed. |

### 1.4 Existing Scheduled Actions We Reuse

| Cron ID | Name | Reuse in MVP | Notes |
|---------|------|-------------|-------|
| #15 | Social: Publish Scheduled Posts | **Reused as-is** | Hourly, publishes `state='scheduled'` posts. No changes. |
| #54 | AI Social News: Dynamic Post at 8PM | **Replaced** | Will be updated to trigger the new MVP pipeline instead of action #845. |

New cron needed? The existing cron #54 can be repurposed — just change its `code` to call the new pipeline action. No new cron record needed.

### 1.5 Existing Activities We Reuse

| Activity Type ID | Name | Reuse in MVP | Notes |
|-----------------|------|-------------|-------|
| #9 | Social Post Review | **Reused as-is** | Already configured with icon, decoration, and model. Activity summary format may change slightly. |

No new activity types needed for the MVP.

### 1.6 Existing AI Capabilities We Reuse

| Capability | Mechanism | Reuse in MVP |
|------------|-----------|-------------|
| Web search via Gemini | `_tool_web_search(ai, query, 'web', context_hint)` | Core — Research Agent uses this |
| Knowledge article query (RAG) | Agent reads its `ai.agent.source` records during execution | Core — both agents automatically have access to linked articles |
| URL source indexing | URL sources are fetched, indexed, and available via agent's RAG context | Core — Research Agent reads external URL sources |
| Context hint passing | The `context_hint` parameter in `_tool_web_search` | Core — Context Builder assembles this from Knowledge articles + recent posts |
| System prompt + topic instructions | Agent combines its `system_prompt` with topic `instructions` | Core — each agent receives its dedicated topic |

---

## Part 2: Gap Analysis — What Must Be Created

### 2.1 Knowledge Content (Manual Creation)

These are **content items**, not models. They are created using the existing `knowledge.article` model through the Odoo Knowledge app UI.

| Article | Purpose | Content Type |
|---------|---------|-------------|
| **About AzeezTech** | Company overview, history, positioning | HTML (knowledge.article.body) |
| **Mission & Vision** | Company mission, vision, core values | HTML |
| **Services** | AI Automation, Odoo Development, DevOps, Cloud, Business Automation, AI Consulting | HTML |
| **Products** | Current products, upcoming products, open source projects | HTML |
| **Brand Voice** | Writing style, tone, voice guidelines, forbidden words, terminology | HTML |
| **Target Audience** | Business owners, CTOs, developers, DevOps, Odoo partners, SMEs | HTML |
| **Content Strategy** | Posting objectives, content pillars, preferred topics, CTA guidelines, hashtag strategy | HTML |
| **Technical Expertise** | AI, LLMs, Odoo, Kubernetes, Docker, DevOps, Open Source | HTML |
| **Case Studies** | Success stories, customer projects, internal projects | HTML |
| **FAQ** | Common customer questions | HTML |

### 2.2 Agent Sources (Configuration)

These are **configuration records** that link Knowledge Articles to AI agents.

| Source | Agent | Type | article_id |
|--------|-------|------|------------|
| All AzeezTech Knowledge Articles | Research Agent (new or #14) | `knowledge_article` | (one per article) |
| Selected AzeezTech Knowledge Articles (brand, audience, strategy) | Post Generation Agent | `knowledge_article` | (subset relevant to writing) |
| Existing URL sources (TechCrunch, Hacker News, The Verge AI, etc.) | Research Agent | `url` | Already exists — update as needed |

Note: The Post Generation Agent only needs brand-related articles (Brand Voice, Content Strategy, Target Audience). The Research Agent needs everything including Technical Expertise and external URL sources.

### 2.3 AI Topics (New Records)

| Topic Name | Agent | Purpose | Key Instructions |
|------------|-------|---------|------------------|
| **AzeezTech Research** | Research Agent | Discover relevant AI/tech topics | Read Knowledge Articles → identify current trends → return structured research with topic, relevance, sources. Never write marketing copy. |
| **AzeezTech Post Generation** | Post Generation Agent | Create branded posts from research | Read Research output → read Brand Knowledge → write on-brand post → follow writing style → suggest hashtags and CTA. Never perform research. |

Note: These topics replace the current Topic #13 "Social Content Posting" which combined both responsibilities.

### 2.4 AI Agents (New Records — Two Options)

**Option A: Create two new agents** (recommended for clear ownership)

| Agent Name | Topic | System Prompt Focus |
|------------|-------|---------------------|
| **AzeezTech Research Agent** | AzeezTech Research | "You are the AzeezTech research agent. Your only responsibility is discovering relevant AI and technology news. You never write marketing content." |
| **AzeezTech Post Generation Agent** | AzeezTech Post Generation | "You are the AzeezTech social media writer. Your only responsibility is creating engaging branded posts from provided research. You never perform research." |

**Option B: Use agent #14 with both topics** (simpler, fewer records)

Agent #14's system prompt would be simplified to remove content-format rules. The pipeline would call `_tool_web_search` with the appropriate topic instructions for each stage.

### 2.5 Refactored Pipeline (Modified Action)

| Component | Change |
|-----------|--------|
| Action #845 (current) | **Replace entirely** — the old monolithic action is replaced with the new pipeline |
| New pipeline action | New action or same ID with rewritten code. Stages: Load Company → Build Context → Research → Generate → Create Draft + Activity |
| Cron #54 | Update `code` to call the new pipeline action instead of #846 → #845 |

### 2.6 Tools Cleanup

| Tool ID | Name | Action |
|---------|------|--------|
| 664 | AI: Add Tags | Remove from topic tool lists (not needed) |
| 838 | AI Social News Generator | Deactivate or leave as-is (not called by pipeline) |
| 145 | AI: Adjust Search | Remove from topic tool lists (not needed) |

The only tool the MVP needs is #835 (AI: Web Search), plus internal knowledge accessible through the agent's sources.

---

## Part 3: What We Do NOT Need to Create

| Potential Component | Decision | Reason |
|--------------------|----------|--------|
| Custom Python module | **Not created** | Everything achievable with existing Odoo models + server actions |
| Custom Odoo model | **Not created** | `knowledge.article` + `ai.agent.source` cover all data storage needs |
| External service | **Not created** | Gemini via `ai.agent._tool_web_search` handles AI needs |
| New Odoo app | **Not created** | MVP is configuration of existing apps (Knowledge + AI + Social Marketing) |
| New activity type | **Not created** | Activity type #9 (Social Post Review) works for MVP |
| New automation rule | **Not created** | Rule #2 (Social Post: Schedule on Review Done) works as-is |
| New cron record | **Not created** | Cron #54 can be repurposed for the new pipeline |
| Custom UI view | **Not created** | Knowledge app provides article management; social.post provides post management |
| Email template | **Not created** | Email notification can be simplified or removed for MVP |
| Context Builder model | **Not created** | Context assembly is a logical pipeline stage within the server action |

---

## Part 4: Build Order

```
Step 1: Create Knowledge Articles
  └── 10 articles in AzeezTech workspace
  └── ~30 minutes (content creation)

Step 2: Create Research Topic
  └── New ai.topic record with research instructions
  └── Tool: #835 (AI: Web Search) only
  └── ~5 minutes

Step 3: Create Post Generation Topic
  └── New ai.topic record with generation instructions
  └── Tools: none needed (consumes context, no external tools)
  └── ~5 minutes

Step 4: Configure AI Agents
  └── Create Research Agent + link to Knowledge Articles
  └── Create Post Generation Agent + link to Brand articles
  └── Or: simplify agent #14 + assign both topics
  └── ~10 minutes

Step 5: Refactor Pipeline Action
  └── Create new pipeline with stages:
       Load Context → Research → Generate → Create Draft → Create Activity
  └── Replace action #845 code
  └── Update cron #54 to call new action
  └── ~30 minutes

Step 6: Clean Up Old Components
  └── Remove unused tools from topics
  └── Deactivate old action #846 wrapper
  └── ~5 minutes

Total: ~1.5 hours of configuration
```

---

## Part 5: Agent Source Decision — One Agent or Two

This is the final open question before implementation.

### Single Agent (Simpler)

```
Agent #14 "Social Media Agent"

  Topics:
    - AzeezTech Research
    - AzeezTech Post Generation

  Sources (ai.agent.source):
    - All Knowledge Articles (brand, services, products, strategy)
    - URL sources (TechCrunch, Hacker News, etc.)

  Pipeline calls:
    agent._tool_web_search(ai, query, 'web', context)  ← with research topic
    agent._tool_web_search(ai, query, 'web', context)  ← with generation topic
```

- Fewer records to create and maintain
- All Knowledge in one place
- Pipeline logic stays simple

### Two Agents (Clearer Ownership)

```
Agent A "AzeezTech Research Agent"

  Topic: AzeezTech Research
  Sources: All Knowledge Articles + URL sources
  System prompt: "You research. You never write."

Agent B "AzeezTech Post Generation Agent"

  Topic: AzeezTech Post Generation
  Sources: Only brand-related Knowledge Articles
  System prompt: "You write branded content. You never research."
```

- Clean separation of concerns
- Each agent has only the knowledge it needs
- Easier to swap models/providers per agent
- More natural for future AI Platform evolution

Both are valid. The single-agent approach is faster to implement. The two-agent approach is more architecturally sound and matches the Ownership Specification.

---

## Summary: Reuse vs. Create

| Category | Reuse | Create |
|----------|-------|--------|
| Odoo models | 20 | 0 |
| AI components | 4 (agent, topic, tool, sources) | 2 topics, ~2 agents/sources |
| Workflows | 4 | 0 (logical stage only) |
| Scheduled actions | 1 (publish) | 0 (repurpose cron #54) |
| Activities | 1 | 0 |
| Content | 0 | ~10 knowledge articles |

The MVP is **~90% reuse**, **~10% new configuration**.

No new models, no custom modules, no external services.
