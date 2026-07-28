# Architecture Ownership Specification — AI Social Marketing Pipeline

**Author:** Senior Odoo Enterprise Functional Solution Architect  
**Date:** 2026-07-20  
**Principle:** Every business decision has exactly one owner. Every other component consumes that decision. No business rule may be duplicated across Server Actions, AI Topics, AI Agents, or Company configuration.

---

## Ownership Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         OWNERSHIP HIERARCHY                              │
│                                                                          │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  COMPANY                                             owns identity │  │
│  │                                                                     │  │
│  │  Brand | Language | Tone | Audience | Goals | Products | Services  │  │
│  └─────────────────────────┬─────────────────────────────────────────┘  │
│                            │                                            │
│                            ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  CONTEXT BUILDER                              owns context assembly│  │
│  │                                                                     │  │
│  │  Selects relevant context | Trims to token budget | No biz rules  │  │
│  └─────────────────────────┬─────────────────────────────────────────┘  │
│                            │                                            │
│                            ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  AI CAPABILITY                                   owns capability   │  │
│  │                                                                     │  │
│  │  Research | Generate | Dedup | Audit | Rewrite | Translate        │  │
│  │  Business modules request capabilities, never Topics or Agents    │  │
│  └─────────────────────────┬─────────────────────────────────────────┘  │
│                            │                                            │
│              ┌─────────────┴─────────────┐                              │
│              ▼                           ▼                              │
│  ┌────────────────────┐    ┌────────────────────┐                       │
│  │  AI TOPIC           │    │  AI AGENT           │                      │
│  │  owns behavior      │    │  owns execution     │                      │
│  │                     │    │                     │                      │
│  │  What to do         │    │  How to do it       │                      │
│  │  Methodology        │    │  Provider/Model     │                      │
│  │  Formatting         │    │  Temperature        │                      │
│  │  Output schema      │    │  Tools/Retry        │                      │
│  └────────────────────┘    └────────────────────┘                       │
│                            │                                            │
│                            ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  SERVER ACTION                                   owns orchestration│  │
│  │                                                                     │  │
│  │  Executes pipeline | Calls capabilities | Logs results            │  │
│  │  Never contains business rules, prompts, formatting, or queries   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Single Ownership Rule

> Every business decision must have exactly one owner. Every other component consumes that decision. No business rule may be duplicated across AI Topics, AI Agents, Server Actions, or Company configuration.

### Consequences of Violations

| Violation | Drift | Example from Current System |
|-----------|-------|-----------------------------|
| Same rule in Topic + Server Action | Topic becomes stale; action diverges | Dedup rules in both topic #13 and action #845 lines 47-50 |
| Same rule in Agent + Topic | Changing one breaks consistency with the other | Post structure rules in both agent #14 prompt and topic #13 |
| Same rule in Server Action + Agent + Topic | Three-way inconsistency guaranteed | Industry detection in action keywords + agent prompt + topic |
| Different values for same rule across actions | UX inconsistency; hidden bug | Brand context length: 1500 in #845, 400 in #850 |

---

## Ownership Definitions

### Company (`res.company` / `res.partner`)

**Owns:** Business identity — immutable or slowly-changing facts about the business.

**How it participates:** Exists in the database. The Context Builder reads from it. No other component writes to it.

**Current implementation:** Brand guidelines stored in `res.partner.comment` as free-form HTML. No structured fields.

**What belongs here:**

| Decision | Current Location | Drift if Duplicated |
|----------|-----------------|---------------------|
| Brand voice, tone, language | `partner.comment` (free HTML) | Other components must parse HTML → inconsistent extraction |
| Language preferences | -- (not stored explicitly) | AI guesses from company name → wrong language for names like "NabdSportsAI" |
| Target audience | `partner.comment` (free HTML) | AI may focus on wrong audience segment |
| Business goals | `partner.comment` (free HTML) | AI topic cannot reference specific goals |
| Products/services | `partner.comment` (free HTML) | Research cannot target company-specific context |
| Content languages | -- (not stored explicitly) | Each action has different language-detection logic |

### Context Builder

**Owns:** Runtime context assembly — deciding what information to pass to an AI capability.

**Does NOT own:** Business rules, AI behavior, formatting, execution.

**How it participates:** Called by the pipeline before each capability invocation. Receives company data, returns a structured context dict.

**Critical constraint:** No hardcoded trim lengths. The Context Builder understands token budgets and selects the most relevant information dynamically.

**Current implementation:** Does not exist. Its responsibilities are scattered across action #845 (inline string concatenation of brand + dedup + query), agent #14's system prompt (tells the AI to "read partner's Notes"), and topic #13 (tells the AI to "detect industry from name and notes").

### AI Capability

**Owns:** A named business capability — Research, Content Generation, Duplicate Review, Audit, Rewrite.

**How it participates:** Business modules (Social Marketing, CRM, Helpdesk) call capabilities by name. Each capability has a Topic (what to do) and an Agent (how to execute).

**Current implementation:** Does not exist. Social Marketing directly calls agent #14 + topic #13 instead of calling a "Research" capability.

### AI Topic (`ai.topic`)

**Owns:** AI behavior — what the AI should do, think, check, and generate.

**How it participates:** Linked to a capability. The capability passes the topic instructions to the agent as the system prompt.

**What belongs here:**

| Decision | Current Location | Drift if Duplicated |
|----------|-----------------|---------------------|
| Research methodology | Agent #14 prompt + topic #13 | Partially duplicated |
| Dedup protocol | Action #845 lines 47-50 + topic #13 | Duplicated — topic is the authority |
| Post structure | Agent #14 prompt + topic #13 | Duplicated — topic is the authority |
| Tone guidance | Agent #14 prompt + topic #13 | Duplicated — topic is the authority |
| Content format | Action #845 lines 76-80 + topic #13 | Duplicated + action overrides with code |
| Output schema | -- (not defined) | Action code parses arbitrary text |
| NO_FRESH_ANGLE contract | Action #845 line 59 + topic #13 | Duplicated — topic defines, action should just check |

### AI Agent (`ai.agent`)

**Owns:** Execution — how the AI runs.

**How it participates:** Receives topic instructions + assembled context, executes via configured provider/model/tools.

**What belongs here:**

| Decision | Current Location | Drift if Duplicated |
|----------|-----------------|---------------------|
| AI provider | Agent #14.llm_model | Single source — correct |
| Tools available | Topic #13.tool_ids | Correct — Agent doesn't own tool selection |
| System prompt (role) | Agent #14.system_prompt | Partially correct — currently contains behavior rules that belong in topic |

### Server Action (`ir.actions.server`)

**Owns:** Orchestration — controlling the sequence of operations.

**Does NOT own:** Business decisions, AI instructions, prompt construction, content formatting, language detection, search queries, email templates, or any business logic.

**How it participates:** Calls the Context Builder → invokes capabilities → handles results → creates records.

**What belongs here:**

| Decision | Current Location | Drift if Duplicated |
|----------|-----------------|---------------------|
| Execution sequence | Action #845 for loop | Correct — this is orchestration |
| Company iteration | Action #845 companies loop | Correct — this is orchestration |
| Post/activity/email creation | Action #845 lines 107-140 | Correct — this is orchestration |
| Log writing | Action #845 log() calls | Correct — this is orchestration |

---

## The Ownership Matrix

Every row documents one business decision. The matrix is sorted by cleanup priority (Critical → High → Medium → Low).

### Priority Legend

| Priority | Meaning |
|----------|---------|
| **Critical** | Duplicate ownership causes incorrect behavior. Fix before any other work. |
| **High** | Duplicate ownership causes configuration drift. Fix as part of Phase 1. |
| **Medium** | Single ownership but needs a home. Fix when the owning component exists. |
| **Low** | Implementation detail. Fix if convenient. |

---

| # | Business Decision | Current Owner(s) | Correct Owner | Consumer(s) | Behavior Drift from Duplication | Migration Strategy | Priority |
|---|-------------------|-----------------|---------------|-------------|--------------------------------|-------------------|----------|
| 1 | **Dedup rules** (how to compare posts, what counts as duplicate, NO_FRESH_ANGLE signal) | **DUPLICATED**: Action #845 lines 47-50 + Topic #13 | **AI Topic** (Topic #13) | Duplicate Review Capability | Topic adds a new dedup rule but action still sends old format. Action changes how posts are numbered but topic still references old format. Both drift independently. | Remove lines 47-50 from action #845. Action only passes raw post data. Topic #13 is the sole dedup authority. Action checks NO_FRESH_ANGLE in the response but does not construct the instruction. | **Critical** |
| 2 | **Formatting rules** (header text, emoji usage, insight count, hashtag format, line length thresholds, content structuring) | **DUPLICATED**: Action #845 lines 70-80 + Agent #14 prompt + Topic #13 | **AI Topic** (Topic #13) | Content Generation Capability | Each duplication creates a slightly different format. Action hardcodes inline emoji and max 4 insights. Topic says "2-3 insights." Agent says "2-3 bullet points." Users see different formatting depending on which component's rules dominate. | Remove all post-formatting code from action #845 (lines 70-80). Move format rules exclusively to topic #13. Remove duplicate format rules from agent #14's system prompt. The AI generates the final format; the action stores it as-is. | **Critical** |
| 3 | **Search query / search objective** (what to search for: "latest AI technology news breakthroughs business" vs "AI in sports latest news") | **DUPLICATED**: Action #845 line 52 + Agent #14 prompt + Topic #13 + Action #850 line 10 | **Context Builder** (new component) | Research Capability | Every component has different query logic. #845 has two hardcoded queries. #850 has a third default query. The agent prompt says "search the web for the latest relevant news" (different). The topic says "search the web for the latest news relevant to their industry" (different again). No two components agree. | Action #845 passes company data to Context Builder. Context Builder generates a search objective from brand + context + platform. Research Capability executes the search. Remove query string from all current locations. | **Critical** |
| 4 | **Language detection** (whether the post should be Arabic, English, or bilingual) | **DUPLICATED**: Action #845 line 76 (keyword detection: 'عرب'/'نبض') + Agent #14 prompt ("Arabic brands get Arabic posts") + Topic #13 ("Arabic and/or English as per brand guidelines") | **Company** (`res.partner` with standard language fields) | Context Builder, AI Capability | Each component detects language differently. Action uses keyword matching on company name. Agent uses "follow brand guidelines." Topic also uses "as per brand guidelines." Companies with mixed-language names (NabdSportsAI) get inconsistent results. | Add `content_lang_ids` to `res.partner` as a standard many2many to `res.lang`. The company explicitly lists supported languages. Context Builder reads this. AI Capability receives the language as an explicit parameter. Remove keyword detection from action. | **Critical** |
| 5 | **Search query for rewrite** (action #850 uses "latest AI technology news" with Arabic-only header) | **DUPLICATED**: Action #850 lines 10-17 + 32 (Arabic header hardcoded) | **Context Builder** | Rewrite Capability | The rewrite action ignores the company's brand language and uses a hardcoded Arabic header. A company that posts in English gets Arabic content when regenerated. This is a functional bug — the same company gets different-quality content from the two actions. | Make the rewrite action use the same Context Builder as the main pipeline. Remove hardcoded query (line 10). Remove hardcoded Arabic header (line 32). Remove shortened brand context (400 chars vs 1500). The rewrite should be identical to the original generation except for the dedup+rewrite step. | **Critical** |

---

| # | Business Decision | Current Owner(s) | Correct Owner | Consumer(s) | Behavior Drift from Duplication | Migration Strategy | Priority |
|---|-------------------|-----------------|---------------|-------------|--------------------------------|-------------------|----------|
| 5 | **Industry detection** (determining whether a company is tech, sports, etc.) | **DUPLICATED**: Action #845 lines 35-39 (keyword list) + Agent #14 prompt + Topic #13 | **AI Capability** (Research) — the AI determines it from brand context | Research Capability | Action and Topic disagree on detection method. Action uses keyword matching with a specific list. Topic tells the AI to "detect industry from name and notes." The action's keyword approach produces `industry='tech'` or `'sport'`. The AI's approach produces any industry. They produce different results for the same company. | Remove lines 35-39 from action #845. Remove explicit industry keywords from action. The Research Capability receives brand + company context and determines industry as part of the research step. The Topic already instructs this — let it work. | **High** |
| 6 | **Supported platforms** (which social media platforms the pipeline targets) | **DUPLICATED**: Action #845 lines 22-26 (hardcoded list) + Action #850 (no platform filter) | **Company** (`res.company` using existing `social.account` records) | Context Builder, Pipeline Orchestrator | Adding a new platform requires modifying action code. The rewrite action has no platform filter at all. | Remove the hardcoded list. Query `social.account` for the company's connected accounts. Use `media_type` to determine platform-specific context. No code change needed to support new platforms — the company just connects a new account. | **High** |
| 7 | **Post structure rules** (headline, 2-3 insights, key takeaway, CTA, 3-5 hashtags) | **DUPLICATED**: Agent #14 prompt + Topic #13 | **AI Topic** (Topic #13) | Content Generation Capability | Changing "2-3 insights" to "3-5 insights" in the topic doesn't affect the agent prompt. Both must be changed in lockstep. Any edit session that forgets one creates drift. | Remove post structure rules from agent #14's system prompt. The agent's prompt should only define its role ("You are the social media content agent"). The topic owns all generation behavior. | **High** |
| 8 | **Tone guidance** ("Professional, engaging, human — never robotic or generic") | **DUPLICATED**: Agent #14 prompt + Topic #13 | **AI Topic** (Topic #13) | Content Generation Capability | Same drift problem as #7. | Remove tone guidance from agent #14 prompt. Keep only in topic #13. | **High** |
| 9 | **Error detection** (keywords that indicate AI API failure) | Action #845 lines 61-64 (hardcoded list) | **AI Capability** or **Context Builder** | Pipeline Orchestrator | Error keywords are provider-specific. If the AI provider changes, the list must be updated in action code. No single location for provider-specific error patterns. | Move error detection to the Capability layer — the capability knows what errors its provider returns. The pipeline simply checks `result.status` instead of parsing for keywords. | **High** |
| 10 | **Activity deadline** (review deadline set to 9 PM) | Action #845 lines 83, 121 (hardcoded hour=21) | **Context Builder** (derived from company preferences or admin's working hours) | Activity creation in orchestration | Fixed at 9 PM for all companies. Cannot customize. | Context Builder determines deadline: use company's configured deadline hour, or admin user's working hours, or default 9 PM. Not a company config field — a dynamic assembly decision. | **High** |
| 11 | **Schedule delay** (post scheduled 1 hour after approval) | Action #849 line 6 (hardcoded `now.hour + 1`) | **Context Builder** (derived from Company preferences or global default) | Schedule action in orchestration | Fixed at 1 hour for all companies. | Context Builder passes `schedule_delay_hours` to the orchestration. Derived from company preference if set, otherwise global default. | **High** |

---

| # | Business Decision | Current Owner(s) | Correct Owner | Consumer(s) | Behavior Drift from Duplication | Migration Strategy | Priority |
|---|-------------------|-----------------|---------------|-------------|--------------------------------|-------------------|----------|
| 12 | **Brand context: what to include and how much** | **DUPLICATED**: Action #845 line 28-31 (HTML-to-text + trim to 1500) + Action #850 line 16 (trim to 400) + Agent #14 prompt ("Read partner's Notes") | **Context Builder** | AI Capability | Two actions use different trim lengths for the same company. The Context Builder should decide, based on token budget, what brand information is most relevant. Fixed trim lengths lose the end of the notes — which often contains the most specific instructions. | Create Context Builder component. For each capability invocation, it: (a) reads all brand data, (b) estimates token budget, (c) selects the most relevant subset, (d) passes to capability. No hardcoded trim length. | **Medium** |
| 13 | **Workflow stage: Company scope** (which companies the pipeline processes) | Action #845 line 18 (`res.company.search([])`) | **Pipeline Orchestrator** (Server Action) | -- | Correct ownership already. | None needed. | **Low** |
| 14 | **Workflow stage: Account discovery** (finding social accounts per company) | Action #845 lines 19-25 (search for active social accounts) | **Pipeline Orchestrator** (Server Action) | -- | Correct ownership already. | Query becomes `accs.mapped('media_type')` for platform-specific context. | **Low** |
| 15 | **UTM source assignment** | Action #845 line 112-113 (hardcoded "Social Media" name) | **Context Builder** | Post creation | UTM source "Social Media" must exist in the database or field is false. | Context Builder determines UTM source from campaign/company context. Default remains "Social Media" but not hardcoded in action. | **Low** |
| 16 | **Email notification template** | Action #845 lines 124-140 (inline HTML) | **Server Action** (orchestration) | -- | Inline HTML is not editable from UI. | Could change to `mail.template` but this is a UI concern, not an ownership concern. Keep or change based on convenience. | **Low** |
| 17 | **Activity summary/note format** | Action #845 lines 106, 118-119 (inline strings) | **Server Action** (orchestration) | -- | UI presentation detail. No business decision. | Leave. | **Low** |
| 18 | **Log message format** | Action #845 log() calls | **Server Action** (orchestration) | -- | Debugging detail. No business decision. | Leave. | **Low** |

---

## Duplication Map (Visual)

```
                      Current State                        Desired State
                      
DEDUP RULES           TOPIC #13  ── action #845 lines 47-50         TOPIC #13
                      (same text copy-pasted)                        (sole owner)
                                                                     ▲
                      BOTH DRIFT INDEPENDENTLY                       │
                                                                     │ only data
                                                                     │
                                                                   action #845


SEARCH QUERY          action #845  ── agent #14 prompt
                      (two queries)   (vague instruction)          CONTEXT BUILDER
                                                                     (sole owner)
                      topic #13  ── action #850                      ▲
                      (vague)         (third query)                  │
                                                                     │ only data
                      ALL FOUR DIFFERENT                             │
                                                                   action #845


LANGUAGE              action #845 line 76                             
                      (keyword match)                               COMPANY res.partner
                                                                     (sole owner)
                      agent #14 prompt                                ▲
                      ("follow guidelines")                           │
                                                                      │
                      topic #13                                       │
                      ("Arabic/English as per guidelines")            ▼
                                                                   CONTEXT BUILDER
                      THREE DIFFERENT APPROACHES                      │
                                                                      ▼
                                                                    AI CAPABILITY


POST STRUCTURE        agent #14 prompt  ── topic #13                 TOPIC #13
                      (same rules copy-pasted)                       (sole owner)
                                                                     
                      BOTH DRIFT INDEPENDENTLY
```

---

## Current Duplication Count

| Component | Lines | Business Decisions Owned | Correctly Owned | Duplicated | Needs Removal |
|-----------|-------|-------------------------|-----------------|------------|---------------|
| Action #845 | ~140 | Dedup context, search query, format, industry, language, thresholds, email | 2 (orchestration, email) | 8 | Lines 35-39, 42-50, 52, 57-64, 69-80, 83-84, 97, 101, 112-113, 121 |
| Action #849 | ~10 | Schedule delay | 0 | 1 | Line 6 (schedule delay logic) |
| Action #850 | ~37 | Query, industry, format, language | 0 | 4 | Lines 10-17, 32 (plus all formatting code same as #845) |
| Agent #14 prompt | ~200 words | Role, behavior, format | Role only | Behavior, format, tone, language | Lines describing post structure, format rules, language detection |
| Topic #13 | ~500 words | Research, dedup, format, language | Everything | Duplicates agent prompt | None — topic is the correct owner for all of these |
| Total | ~387 lines + prompts | ~20 decisions | ~2 | ~18 | ~18 decisions need consolidation |

---

## Cleanup Plan: Priority Order

### Step 1: Make Topic #13 the single owner of AI behavior (Critical)

**Remove from action #845:**
- Lines 47-50 — dedup context construction (action passes raw post list instead)
- Line 59 — NO_FRESH_ANGLE string detection (action checks response for this string but topic defines it)
- Lines 70-80 — post formatting (emoji, header, insight count, hashtag)

**Remove from agent #14:**
- Post structure rules (headline, 2-3 insights, key takeaway, CTA, 3-5 hashtags)
- Tone guidance ("Professional, engaging, human")
- Language rules ("Arabic brands get Arabic posts")
- Search instruction ("Search the web for latest relevant news")

**Result:** Topic #13 is the sole authority on:
- How the AI should research
- How the AI should format posts
- How the AI should detect language
- How the AI should check duplicates
- How the AI should structure output

### Step 2: Make company the owner of business identity (High)

**Add to `res.partner`:**
- `content_lang_ids` (many2many to `res.lang`) — which languages this company posts in
- No other fields needed — brand voice, tone, audience, goals remain in `partner.comment` for now

**Remove from action #845:**
- Lines 35-39 — industry keyword detection and default `industry='tech'`
- Line 76 — language detection (`if 'عرب' in text`)

**Remove from action #850:**
- Lines 11-14 — industry keyword detection
- Line 32 — hardcoded Arabic header

**Result:** Company explicitly declares language. Industry is inferred by AI from brand context. No keyword matching anywhere.

### Step 3: Create Context Builder as a logical stage (High)

**Within action #845, add a documented "Load Context" stage:**
```python
def load_context(company):
    return {
        'company': company,
        'brand': partner.comment,  # raw — Context Builder decides what's relevant
        'languages': partner.content_lang_ids,
        'recent_posts': last_posts,  # raw post data
        'platforms': accs.mapped('media_type'),
        'schedule': {'deadline_hour': 21, 'delay_hours': 1},
        'token_budget': 4000,  # estimated available tokens
    }
```

**Action #845 calls `load_context()` and passes the result to the AI call.**

**Result:** Context assembly is isolated in one function. The AI call receives a structured context dict. No more inline string concatenation.

### Step 4: Fix action #850 to use same context as #845 (Critical)

**Changes to action #850:**
- Use `load_context()` instead of inline brand extraction
- Use `context['languages']` instead of hardcoded Arabic
- Use `context['brand']` instead of `clean_notes[:400]`
- Remove hardcoded query

**Result:** The rewrite action produces the same quality as the original generation. Inconsistency bug fixed.

### Step 5: Move thresholds to single source (Medium)

- Move line thresholds, content lengths, dedup counts to documented constants at the top of the action (or `ir.config_parameter`)
- These are implementation constants, not business decisions — but they should not be scattered

**Result:** Single location for tuning content extraction parameters.

---

## Ownership Summary After Phase 1

```
COMPANY                  CONTEXT BUILDER          AI TOPIC (#13)
owns business identity   owns context assembly    owns AI behavior
│                                                  │
│  Brand (notes)          Selects from company     Research methodology
│  Language (lang_ids)    Estimates token budget   Dedup protocol
│  Platforms (accounts)   Passes to capability     Post structure
│                                                    Formatting rules
│                                                    Output schema
│                                                    Tone guidance

AI CAPABILITY                                      AI AGENT (#14)
owns capability interface                           owns execution

  Research capability     ← topic + agent →          Provider (Gemini)
  Generate capability                                Model (2.5 Flash)
  Dedup capability                                   Temperature (0.7)
  Rewrite capability                                 Tools (web search)
                                                     
SERVER ACTIONS (#845, #849, #850)                   
owns orchestration                                   

  company loop → load_context → research → generate → create post
  Never owns business decisions
  Never owns formatting
  Never owns search queries
```

---

## Verification Checklist

After Phase 1 cleanup, the following should be true:

| Statement | Evidence |
|-----------|----------|
| Every business decision has one owner | Ownership matrix shows no duplicates |
| Action #845 contains no AI instructions | Inspect lines 47-80 — only data, no behavior |
| Agent #14 contains no content rules | Inspect system prompt — only role, no format/behavior/tone |
| Topic #13 is the sole AI behavior source | No other component defines how the AI should act |
| Language is stored on the company, not guessed | `res.partner.content_lang_ids` exists |
| Action #850 produces same quality as #845 | Both use same context builder, language, brand length |
| Industry detection is handled by the AI | No keyword lists in action code |
| Platforms are dynamic | Action reads `social.account` without hardcoded list |
| Context assembly is one function | `load_context()` is the sole entry point for AI context |

---

## Appendix: Deferred Decisions

These business decisions are recognized but deliberately deferred because they require new components that don't exist yet:

| Decision | Deferred To | Reason |
|----------|-------------|--------|
| Knowledge source selection | Context Builder (Phase 5) | Knowledge sources don't exist yet; Context Builder will eventually include them |
| Campaign context | Context Builder (Phase 3) | Campaign/UTM integration needs UTM module awareness |
| User/role overrides | Context Builder (Phase 3) | Multi-role review workflows not yet implemented |
| Token budget calculation | Context Builder (Phase 3) | Requires understanding of model context windows and token counting |
| Output schema definition | AI Topic (Phase 3) | Currently no structured output contract between AI and pipeline |
| Capability abstraction layer | AI Platform (Phase 3) | Separating Social from the AI platform requires the Capability concept |
