# Hardcoded Value Inventory — AI Social Posting Pipeline

**Author:** Senior Odoo Enterprise Functional Solution Architect  
**Date:** 2026-07-20  
**Scope:** All hardcoded values in actions #845, #849, #850, agent #14 system prompt, and topic #13 instructions.  
**Principle:** Every business decision encoded as a literal should be identified, classified, and assigned to its appropriate Odoo component.

---

## Classification Key

| Classification | Definition | Source of Truth |
|---------------|------------|-----------------|
| **AI Topic** | Directs AI behavior: what the AI should do, think, check, or generate | `ai.topic.instructions` |
| **AI Agent** | Controls AI execution: which agent, model, tools | `ai.agent` fields |
| **Company Field** | Varies per company; belongs on `res.company` or `res.partner` | Existing Odoo model |
| **ir.config_parameter** | Global technical constant that rarely changes | `ir.config_parameter` |
| **Dynamically Derived** | Computed at runtime from data already in the system | N/A — remove literal |
| **Action Implementation** | True constant of the implementation itself (not business logic) | Leave in server action |
| **Deprecated/Unused** | No longer called, legacy artifact | Remove or preserve as-is |

---

## Action #845 — `AI Social News: Dynamic Multi-Company`

### Constants by Line Number

│#│ Value │ Business Decision │ Classification │ Recommended Destination │
│─|───────|───────────────────|────────────────|────────────────────────|
│5│ `env['ai.agent'].browse(14)` │ Which AI agent executes the pipeline │ **AI Agent** → `ai.agent` │ The agent should be selected on the company's AI configuration. Place a `social_ai_agent_id` field on `res.company` (or use an `ir.config_parameter` with the default agent ID, overridable per company). The agent record stores everything else. |
│6│ `env['mail.activity.type'].browse(9)` │ Which activity type is used for review │ **ir.config_parameter** │ Store `social_review_activity_type_id` in `ir.config_parameter`. This is a global technical constant. |
│22-26│ `['facebook', 'linkedin', 'instagram', 'twitter']` │ Which platforms the pipeline considers "social" │ **Company Field** │ These are `social.media.type` records in the database. Query them dynamically: `'media_type', 'in', social_media_type.search([('is_social_platform', '=', True)]).mapped('name')` — this requires adding an `is_social_platform` boolean field to `social.media.type`. |
│28-30│ `<p> → \n, </p> → \n, <br/> → \n, <li> → \n- , remove </li>, <ul>, </ul>` │ How HTML is converted to plain text │ **Action Implementation** │ Leave in server action. This is a text-processing implementation detail, not a business decision. |
│31│ `clean_notes[:1500]` │ Maximum brand context length passed to the AI │ **Company Field** │ Max context length per company (some have longer brand guides). Add `brand_context_length` to `res.partner` with a default of 1500. Or keep as `ir.config_parameter` if truly global. |
│35│ `industry = 'tech'` │ Default industry when no keywords match │ **Dynamically Derived** │ Default should be `None` (not `'tech'`). The search query should only default to "tech" if the company truly has no detectable industry. This currently misclassifies every non-sport company as tech. Remove the default entirely; let it be a company field. |
│36-39│ `['sport', 'رياضة', 'نبض', 'كرة', 'athlete', 'stadium', 'esport', 'sports']` │ Which keywords indicate a sport industry │ **Dynamically Derived** → **AI Topic** │ Industry detection is a semantic task best handled by the AI, not keyword matching. Move to topic instructions: "Detect the company's industry from their name and notes. Common industries include technology, sports, finance, healthcare, etc." Remove keyword list entirely. The AI already receives company name and brand notes — it can infer industry more reliably than a keyword match. |
│42│ `limit=10` │ How many recent posts to fetch for dedup context │ **ir.config_parameter** │ Global default for dedup sample size. Store in `ir.config_parameter` as `social_dedup_posts_count`. |
│44│ `lp.message[:300]` │ Truncation length for each deduped post in the context │ **Action Implementation** │ Leave in action. This is a text-processing concern: limit context size per post so the AI doesn't overflow. Could become an `ir.config_parameter` if needed. |
│47│ `'SEMANTIC DEDUP CHECK REQUIRED. Recent posts for this company (must not repeat): '` │ Prefix text instructing the AI about dedup │ **AI Topic** │ This text should be in topic #13's instructions, not constructed in code. The topic already has the dedup protocol. The server action should pass the raw post list and let the topic define how it's framed. |
│49│ `topic[:200]` │ Truncation per post within the dedup context string │ **Action Implementation** │ Same as #44 — text-processing concern. Leave or move to `ir.config_parameter`. |
│50│ `'You MUST NOT cover the same topics...If all web news covers the same topics, respond with: NO_FRESH_ANGLE'` │ Dedup enforcement instruction │ **AI Topic** │ Move entirely to topic #13's instructions. The topic already contains this — remove duplication. The server action should not construct AI instructions. |
│52│ `'AI in sports latest news'` │ Search query for sport industry │ **Dynamically Derived** → **Company Field** │ Industry-specific search queries should not be hardcoded. Add `industry_search_query` to `res.company` (or a related model). Default can be empty — the AI can determine the best query from company context. |
│52│ `'latest AI technology news breakthroughs business'` │ Search query for non-sport industry │ **Dynamically Derived** → **Company Field** │ Same as above. Default should be empty — let the AI determine the query from brand context and company description. The AI doesn't need a query string if it has the full brand profile. |
│57│ `len(str(result)) > 50` │ Minimum AI response length to be considered valid │ **ir.config_parameter** │ Minimum valid response length. Store as `social_search_result_min_length`. |
│59│ `'NO_FRESH_ANGLE'` │ Magic string that signals "skip this company" │ **AI Topic** │ This is a contract between the AI and the pipeline. Belongs in topic #13's instructions as the expected format: "respond with NO_FRESH_ANGLE if all news covers duplicate topics." Already documented there — remove duplication from action code. |
│61-64│ `['failed', 'quota', 'rate limit', 'rate_limit', 'error', 'not available', 'try again later']` │ Keywords that indicate an AI API error │ **AI Agent** → **AI Topic** or **ir.config_parameter** │ Error keywords are AI-provider-specific. Different providers return different error patterns. Could live in `ir.config_parameter` as a comma-separated list, or in the topic instructions as "if the search returns an error message, the system will detect it." Simpler: move to `ir.config_parameter` key `social_error_keywords`. |
│69│ `len(search_results) > 200` │ Minimum content length for post generation │ **ir.config_parameter** │ Store as `social_content_min_length`. |
│70│ `search_results.replace('\r', '').replace('\\n', '\n')` │ Text normalization │ **Action Implementation** │ Leave in action. This is a string-processing detail. |
│71│ `len(l.strip()) > 30` │ Minimum line length for content extraction │ **ir.config_parameter** │ Store as `social_line_min_length`. |
│73│ `len(clean) > 40 and len(clean) < 500` │ Valid line length range │ **ir.config_parameter** │ Store as `social_line_min` and `social_line_max`. |
│72│ `line.replace('#', '').replace('*', '').replace('"', "").replace("'", "").strip()` │ Character cleanup before content extraction │ **Action Implementation** │ Leave in action. This is text processing. |
│76│ `'أحدث الأخبار'` / `'Latest News'` │ Post header text │ **AI Topic** │ The header format is a content decision. Move to topic #13: "Generate a post with the format: {Company Name} | {Relevant Header Text}". Remove hardcoded headers from the action. |
│76│ `if 'عرب' in text or 'نبض' in text` │ Language detection logic │ **Dynamically Derived** → **Company Field** │ Language should not be guessed from company name keywords. Add `default_content_language` to `res.partner` (company partner record). Default is Arabic for Arabic-named companies, else English. The AI should be told the language explicitly, not guessed. |
│78│ `organized[:4]` │ Maximum number of insights/items per post │ **AI Topic** │ Belongs in the topic instructions: "include 2-4 insights or bullet points." The action should not truncate AI output — the AI should generate the right number. |
│79-80│ `'\U0001f4cc', '\U0001f4a1'` │ Emoji style for post formatting │ **AI Topic** │ Emoji formatting is a content style decision. Move to topic instructions. The AI can choose appropriate emojis. |
│83│ `deadline = now.replace(hour=21, minute=0, second=0, microsecond=0)` │ Default review deadline time (9 PM) │ **Company Field** │ Review deadline varies by company or user preference. Add `activity_deadline_hour` to `res.company` (or use user's working hours). |
│86-94│ Full alert note text │ Error notification text │ **AI Topic** or **Action Implementation** │ The alert text format is a UI concern. Could remain in the action (it's not AI behavior). But the error categories should be more nuanced (see Phase 1 proposal). Leave for now; improve in Phase 1. |
│97│ `post_content[:200]` │ Hard dedup prefix length │ **ir.config_parameter** │ Store as `social_dedup_prefix_length`. |
│101│ `limit=10` │ How many posts to check in hard dedup │ **ir.config_parameter** │ Same as #42 — reuse `social_dedup_posts_count`. |
│106│ `summary='⚠️ Web Search Failed: ' + company.name` │ Alert activity summary format │ **Action Implementation** │ Leave in action. This is a UI presentation detail. |
│112│ `source = env['utm.source'].search([('name', '=', 'Social Media')])` │ UTM source name │ **Company Field** or **ir.config_parameter** │ UTM source is a business classification choice. Could be per-company. Default "Social Media" in `ir.config_parameter`. |
│118│ `summary='Review: ' + company.name + ' post'` │ Review activity summary format │ **Action Implementation** │ Leave in action. This is a UI convention. |
│119│ `'AI-generated post for review:\n\n' + post_content[:500]` │ Activity note content │ **Action Implementation** │ Leave in action. This is a UI convention. |
│121│ `deadline` (same 9 PM from line 83) │ Review deadline for activity │ **Company Field** │ Same as #83. |
│127│ `post_content[:300]` │ Email preview length │ **ir.config_parameter** │ Store as `social_email_preview_length`. |
│128│ `'...' if len(post_content) > 300` │ Email preview truncation marker │ **Action Implementation** │ Leave in action. Standard text convention. |
│129-136│ Full email HTML template │ Email notification content │ **Action Implementation** → **ir.actions.server** (leave) | The email template is constructed inline. For now leave it. Ideally this would use Odoo's email template engine (`mail.template`), but that requires a model change. Leave as-is until Phase 2. |
│138│ `'[Review] ' + company.name + ' Post - ' + now.strftime('%b %d')` │ Email subject line │ **Action Implementation** │ Leave in action. Standard email subject. |
│139│ `admin_user.company_id.email or ''` │ Email from address │ **Action Implementation** │ This is already dynamically derived — it uses the admin's company email. No change needed. |

---

## Action #849 — `Auto Schedule on Activity Done`

│#│ Value │ Business Decision │ Classification │ Recommended Destination │
│─|───────|───────────────────|────────────────|────────────────────────|
│2│ `activity.activity_type_id.id != 9` │ Which activity type triggers auto-schedule │ **ir.config_parameter** │ Same activity type ID as action #845, line 6. Store in `ir.config_parameter` as `social_review_activity_type_id`. |
│6│ `now.replace(hour=now.hour + 1, minute=0, second=0)` │ Schedule delay after approval (1 hour) │ **ir.config_parameter** or **Company Field** │ Schedule delay could be per-company or global. Store as `social_schedule_delay_hours` in `ir.config_parameter` with default 1. |

---

## Action #850 — `Rewrite with AI`

│#│ Value │ Business Decision │ Classification │ Recommended Destination │
│─|───────|───────────────────|────────────────|────────────────────────|
│9│ `env['ai.agent'].browse(14)` │ Which AI agent rewrites │ **AI Agent** │ Same as #845 line 5. Use the same configured agent. |
│10│ `'latest AI technology news'` │ Fallback search query for rewrite │ **Dynamically Derived** → **Company Field** │ Same as #845 line 52. Should use the company's configured default query, not a hardcoded fallback. |
│11-14│ `['sport', 'رياضة', 'نبض', 'كرة', 'athlete']` │ Industry keywords for query selection │ **Dynamically Derived** | Same as #845 lines 36-39. Remove — let the AI determine industry. Note: this list differs from #845 (missing 'stadium', 'esport', 'sports') — an inconsistency bug. |
│16│ `clean_notes[:400]` │ Brand context length for rewrite (400) │ **Company Field** │ Same as #845 line 31 but different value (400 vs 1500). This is an inconsistency — the rewrite action passes less context than the main pipeline. Should use the same configured value. |
│17│ `'Regenerate social post for '` │ Prompt prefix for rewrite │ **AI Topic** │ Belongs in a dedicated "Rewrite" AI Topic. The topic instructions should define the rewrite behavior. |

Note: Action #850 also duplicates lines 20-37 of content processing logic from #845 (cleaning text, filtering lines, building post content). Every hardcoded value there (length thresholds, emoji, etc.) is the same as #845 with one critical difference: line 32 always uses Arabic header `' | أحدث الأخبار\n\n'` with no language detection. This is a bug — the rewrite action ignores brand language preferences.

---

## Agent #14 System Prompt — `Social Media Agent`

│Text │ Business Decision │ Classification │ Recommended Destination │
|-----|───────────────────|────────────────|────────────────────────|
| `"Read the company partner's Notes (comment field) — this contains the brand voice, tone, language, and content guidelines"` │ Tells the AI to extract brand data from `partner.comment` │ **AI Agent** → stays in `ai.agent.system_prompt` (for now) │ Preserve until Phase 6 introduces a structured brand profile. Once Brand Profile exists, this line changes to: "Read the company's Brand Profile — this contains structured brand guidelines." |
| `"Detect the company's industry from their name and notes (tech, sports, general business)"` │ Tells the AI to detect industry dynamically │ **AI Agent** → stays in `ai.agent.system_prompt` │ Correct pattern — this is already what we want. The AI detects industry from context rather than keyword matching. The only improvement is adding more industry examples. |
| `"(tech, sports, general business)"` │ Industry example list │ **AI Topic** │ This should be in the topic instructions, not the agent system prompt. The agent defines the role; the topic defines the task-specific instructions. |
| `"Search the web for the latest relevant news in that industry"` │ Research instruction │ **AI Topic** │ Belongs in topic #13 together with the research steps. The agent prompt should say "Follow your assigned Topic instructions" rather than duplicating them. |
| `"Create an engaging, human-written social media post following the brand voice"` │ Generation instruction │ **AI Topic** │ Same as above. The agent prompt is currently a de facto topic because the actual topic duplicates it. |
| Post Structure (headline, insights, takeaway, CTA, hashtags) │ Content format rules │ **AI Topic** │ Currently duplicated in both agent prompt and topic instructions. Remove from agent prompt; keep only in topic. |
| `"Languages: Follow the brand guidelines. Arabic brands get Arabic posts. English or bilingual as specified."` │ Language instruction │ **Company Field** → `res.partner` │ Language should be explicitly configured on the company, not guessed by the AI from brand notes. Add a `default_content_language` field to `res.partner`. The agent receives it in context rather than parsing it from free text. |
| `"Tone: Professional, engaging, human — never robotic or generic."` │ Tone instruction │ **AI Topic** │ Belongs in topic instructions. Move there. |

**Key Finding:** The agent system prompt and topic #13 instructions overlap significantly. Every content rule is duplicated. The topic should be the single source of truth for how content is generated; the agent prompt should only define the agent's role and capabilities.

---

## Topic #13 Instructions — `Social Content Posting`

│Text │ Business Decision │ Classification │ Recommended Destination │
|-----|───────────────────|────────────────|────────────────────────|
| `"Read the partner's Notes (comment field) for brand guidelines"` │ Brand source location │ **AI Topic** → stays │ Correct location for this instruction. Will change in Phase 6 when brand becomes structured. |
| `"Detect the company's industry from their name and notes (tech, sports, etc.)"` │ Industry detection instruction │ **AI Topic** → stays │ Correct pattern. The AI detects industry from context. Remove hardcoded keyword detection from action #845. |
| `"Search the web for the latest news relevant to their industry"` │ Web search instruction │ **AI Topic** → stays │ Correct. |
| `"Create an engaging, human-written post that follows the brand voice"` │ Generation instruction │ **AI Topic** → stays │ Correct. |
| Post format rules │ Content structure │ **AI Topic** → stays │ Correct location. The hardcoded formatting in the action code (emojis, header, truncation) partially contradicts these topic instructions. Remove post-formatting from action; let the AI generate the final format. |
| Semantic Dedup Protocol │ Dedup behavior │ **AI Topic** → stays │ Correct location. The action should stop constructing AI instructions (lines 47-50 of #845) and rely entirely on the topic for this. |
| `"NO_FRESH_ANGLE"` │ Skip signal │ **AI Topic** → stays │ Correct location. However, #845 line 59 duplicates this check — should rely on topic alone. |

**Key Finding:** Topic #13 already contains most of the correct behavior. The problem is that the server action overrides or duplicates these instructions with its own formatting logic, error detection, and dedup context construction. The topic should be the sole source of AI behavior.

---

## Summary — All Hardcoded Values (52 total)

### Classification Distribution

| Destination | Count | Examples |
|-------------|-------|---------|
| **AI Topic** (belongs in `ai.topic.instructions`) | 12 | Dedup protocol, header format, emoji style, content structure, line count, language detection logic, error response format, rewrite behavior |
| **AI Agent** (belongs in `ai.agent`) | 1 | Agent ID selection (per company or global) |
| **Company Field** (`res.company` or `res.partner`) | 8 | Industry, language, platforms, brand context length, deadline time, UTM source, default query, schedule delay |
| **ir.config_parameter** | 10 | Dedup post count, min result length, error keywords, line thresholds, content min length, review prefix length, email preview length, activity type ID, schedule delay default |
| **Dynamically Derived** (remove entirely) | 5 | Industry keyword list, `industry='tech'` default, language-from-name detection, rewrite hardcoded Arabic header, rewrite shorter brand context |
| **Action Implementation** (leave in code) | 15 | HTML stripping, text cleaning, string replacements, summary/note format, email template, log messages |
| **Deprecated/Inconsistent** | 1 | Action #850 has different values than #845 for same concepts (brand context 400 vs 1500, industry keyword list shorter) |

### Inconsistencies Found

| Issue | Location |
|-------|----------|
| Action #850 passes only 400 chars of brand context; #845 passes 1500 | #850 line 16 vs #845 line 31 |
| Action #850 always uses Arabic headers; #845 detects language | #850 line 32 vs #845 line 76 |
| Action #850 industry keyword list is shorter than #845 | #850 lines 11-14 vs #845 lines 36-39 |
| Agent prompt and topic instructions duplicate content rules | Both agent #14 and topic #13 have post structure, format, language instructions |
| Action #845 constructs AI instructions inline that duplicate existing topic text | Lines 47-50 of #845 duplicate topic #13's dedup protocol |
| Error detection keywords are in action code but should be configurable | Lines 61-64 of #845 |

---

## Hardcoded Artifact Review

### Values that Should Remain in Action Code

These are text-processing constants, not business decisions:

| Value | Reason |
|-------|--------|
| HTML tag replacements (`<p>` → `\n`, etc.) | Input normalization, no business meaning |
| `text.lower()` | Case-insensitive matching implementation |
| `replace('\r', '')` | Text cleanup, no business meaning |
| `line.replace('#', '').replace('*', '').replace('"', "").replace("'", "")` | Character cleanup, no business meaning |
| Activity summary/note format strings | UI presentation conventions |
| Email HTML template structure | Until a proper `mail.template` model is used |
| Log message strings | Internal debugging |

### Values that Should Move to ir.config_parameter

| Proposed Key | Default | Business Decision |
|-------------|---------|-------------------|
| `social.dedup_posts_count` | 10 | How many recent posts to compare |
| `social.dedup_prefix_length` | 200 | How many chars to compare in hard dedup |
| `social.search_result_min_length` | 50 | Minimum AI response length |
| `social.content_min_length` | 200 | Minimum content for a valid post |
| `social.line_min_length` | 30 | Minimum line length for content extraction |
| `social.line_min` | 40 | Minimum valid insight length |
| `social.line_max` | 500 | Maximum valid insight length |
| `social.email_preview_length` | 300 | Email notification preview length |
| `social.review_activity_type_id` | 9 | Activity type for post review |
| `social.activity_preview_length` | 500 | Activity note preview length |
| `social.max_insights` | 4 | Maximum insights per post |
| `social.error_keywords` | "failed,quota,rate limit,rate_limit,error,not available,try again later" | Error detection list |
| `social.schedule_delay_hours` | 1 | Hours until scheduled post after approval |
| `social.default_utm_source` | "Social Media" | Default UTM source name |

### Values that Should Move to res.company / res.partner

| Proposed Field | Model | Default | Business Decision |
|---------------|-------|---------|-------------------|
| `industry_search_query` | `res.company` | `''` (AI infers) | What search query this company's posts should use |
| `activity_deadline_hour` | `res.company` | 21 | What time review activities are due |
| `default_content_language` | `res.partner` | Based on company name | What language to generate content in |
| `brand_context_length` | `res.partner` | 1500 | How much brand text to pass to AI |
| `is_social_platform` (add to `social.media.type`) | `social.media.type` | True/False | Which platforms the pipeline should target |
| `post_content_languages_ids` | `res.partner` | (many2many) | Which languages this company posts in |

### Values that Belong Exclusively in AI Topics

These should be removed from action code (where they currently are) and kept only in the topic:

| Topic #13 Should Control | Currently Also in Action #845 |
|-------------------------|-------------------------------|
| Dedup comparison instructions | Lines 47-50 (dedup_context construction) |
| NO_FRESH_ANGLE contract | Line 59 (string detection) |
| Post format rules | Lines 76-80 (header, emojis, insights) |
| Content structure | Lines 76-80 (header formatting logic) |
| Per-post insight count | Line 78 (`organized[:4]`) |

### Values that Should Be Dynamically Derived

These should be computed at runtime rather than stored or hardcoded:

| Value | How to Derive |
|-------|---------------|
| Industry | AI infers from company name + brand profile (topic #13 already instructs this) |
| Search query | AI infers from brand profile + industry (remove hardcoded queries) |
| Supported platforms | Query `social.media.type` with an `is_social_platform` filter |
| Language | Read from company's configured `default_content_language` |
| Header text | AI generates appropriate header per post content |
| Emoji | AI chooses appropriate emoji per post tone (casual ↔ professional) |

---

## Knowledge Sources — Existing Odoo Models Investigation

Before introducing a new `social.knowledge.source` model, here are the existing Odoo models that could represent company knowledge sources:

### Candidate: `ai.agent.source`

| Field | Current Purpose | Could Serve As |
|-------|-----------------|----------------|
| `name` | Source display name | ✅ Source name |
| `url` | Source URL | ✅ Source URL |
| `agent_id` | Linked AI agent | ❌ Not company-specific |

**Verdict:** This model exists but is linked to an AI agent, not a company. Adding a `company_id` field would make it usable, but that requires a model change. Not ideal as-is.

### Candidate: `website` (`website.model`)

| Field | Purpose | Could Serve As |
|-------|---------|----------------|
| `name` | Website name | ✅ Company source name |
| `domain` | Website URL | ✅ Source URL |
| `company_id` | Owner company | ✅ Company-specific |

**Verdict:** Only works for companies that already have a configured website in the `website` module. Doesn't cover RSS, blogs, GitHub, or generic URLs. Partial solution.

### Candidate: `documents.document`

| Field | Purpose | Could Serve As |
|-------|---------|----------------|
| `name` | Document name | ✅ Source name |
| `url` | Optional URL | ✅ Could link externally |
| `company_id` | Owner company | ✅ Company-specific |
| `tag_ids` | Categorization | ✅ Content categories |

**Verdict:** Could store links as Document records with a URL, but these are designed for internal files, not knowledge source configuration. Associating a URL with tags, trust scores, and refresh frequencies would feel like model abuse.

### Candidate: `ir.attachment`

| Field | Purpose | Could Serve As |
|-------|---------|----------------|
| `name` | File name | ✅ |
| `url` | File URL | ✅ |
| `res_model`/`res_id` | Linked record | ✅ Could link to company |

**Verdict:** Meant for file storage, not URL management. No fields for priority, trust score, refresh frequency, or categories. Would require many new fields → effectively a new model.

### Recommendation

No existing Odoo model cleanly represents a configurable knowledge source with URL, priority, trust score, refresh frequency, and company association. The closest candidate is `ai.agent.source` if modified, or a light new model could be introduced when needed.

However, for Phase 1 stabilization, knowledge sources are not needed. The AI searches the web dynamically based on company context. Knowledge sources become relevant in Phase 5 when adding curated/private sources. For now, document this position and revisit when Phase 5 scope is defined.

---

## Stabilization Priority Matrix

| Priority | Category | Effort | Impact |
|----------|----------|--------|--------|
| **P0** | Remove inconsistency between #845 and #850 (different brand context lengths, query behavior) | Very Low | High — fixes a bug where rewrite produces different quality than original |
| **P0** | Remove duplicate AI instructions from action code (lines 47-50, 59, 76-80 of #845); topic #13 already covers these | Low | High — single source of truth for AI behavior |
| **P0** | Remove `industry = 'tech'` default; let the AI detect industry from context | Very Low | High — stops misclassifying non-tech companies |
| **P1** | Move platform list to dynamic `social.media.type` query | Low | Medium — enables new platforms without code changes |
| **P1** | Move activity type ID to `ir.config_parameter` | Low | Medium — if activity type is recreated on a new instance |
| **P1** | Move language detection from keyword matching to company field | Low | Medium — more reliable language assignment |
| **P1** | Standardize agent system prompt — remove content rules that duplicate topic #13 | Low | Medium — clearer separation of agent role vs topic task |
| **P2** | Move threshold constants to `ir.config_parameter` | Medium | Low — nice-to-have but rarely changed |
| **P2** | Move schedule delay to `ir.config_parameter` | Low | Low — rarely changed |
| **P3** | Move email template to `mail.template` | High | Low — nice-to-have for email customization |
| **P3** | Introduce knowledge sources (Phase 5) | High | Low — not needed for current functionality |

---

## One-pager: What to Do, In What Order

The stabilization effort follows this sequence:

1. **Fix the inconsistencies** between actions #845 and #850 — same concepts should have same values. This takes 15 minutes and fixes a bug.

2. **Make the topic the single source of AI instructions** — remove lines 47-50 and 59-66 from #845 (the action constructing AI behavior text). The topic already has all this. The action should only pass data, not instructions.

3. **Remove `industry = 'tech'` default** — let the topic detect industry from context. Remove keyword lists. The AI is better at this than the code.

4. **Move language detection from keywords to a company field** — add a language field on the partner record, read it in the action, pass it to the AI. Stop guessing from company name.

5. **Move platforms to dynamic `social.media.type` query** — one boolean field addition, one query change in the action. Any platform becomes usable instantly.

6. **Move activity type ID to `ir.config_parameter`** — so it's not tied to a specific database ID.

7. **Clean up the agent system prompt** — remove content generation rules (move to topic), keep role definition and capability description.

8. **Move threshold constants** — this is mechanical but low value. Only do it if the action code is being refactored anyway.

Steps 1-6 can be done in a single session. Steps 7-8 are optional polish.
