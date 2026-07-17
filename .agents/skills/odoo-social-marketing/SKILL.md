# Skill: odoo-social-marketing

Odoo Social Marketing Expert — Expert-level knowledge of Odoo Social Marketing including social account management, multi-platform publishing (Facebook, Instagram, LinkedIn, X/Twitter, YouTube), post scheduling, stream monitoring, campaign tracking, media attachments, and AI-generated content integration. Use when the user asks about Social Account Management, Multi-Platform Publishing, Post Scheduling & Cron, Social Media Attachments, Stream Monitoring in Odoo 19.

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
- **AI-Generated Content** (`cap_ai_content`): Integrate social posting with ai.agent to generate post content, suggestions, and hashtags. Maintain brand voice and platform constraints.
- **Social Marketing Security** (`cap_social_security`): Configure social marketing user and manager groups, record rules for multi-company/account isolation, and access control for streams, accounts, and posts.
- **Social Analytics & Reporting** (`cap_social_analytics`): Read engagement metrics from live posts, build dashboards, and report on social campaign performance by platform, account, and campaign.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Publishing requires valid OAuth tokens and is subject to platform API rate limits
- Media validation rules vary by platform and can change without notice
- Instagram direct publishing requires Business/Creator accounts and proper Meta permissions
- YouTube posting typically requires videos, not text-only posts
- Stream monitoring is limited by platform search API availability and rate limits

## Context

- **Domain:** Marketing
- **Subdomain:** Social Marketing
- **Skill ID:** skill_social_marketing
- **Knowledge package:** `skills/social_marketing/`

- **Required modules:** social_marketing, utm
- **Optional modules:** social_facebook, social_instagram, social_linkedin, social_twitter, social_youtube

- **Depends on skills:** skill_base, skill_marketing, skill_mail
- **Relevant modules:** social_marketing, social_facebook, social_instagram, social_linkedin, social_twitter, social_youtube, utm, mail
