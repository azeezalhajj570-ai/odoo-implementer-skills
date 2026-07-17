# {{domain}} — Odoo {{version}} Knowledge Base

> Generated: {{generated_at}} | Depth: {{depth}} | Audience: {{audience}}

---

## Table of Contents

{% for section in sections %}
1. [{{section.title}}](#{{section.id}})
{% endfor %}

---

{% for section in sections %}
## {{section.title}}

**Relevance:** {{section.relevance_weight}}

{% for claim in section.claims %}
- {{claim.text}} {% for sid in claim.source_ids %}[{{sid}}]{% endfor %}
{% endfor %}

{% if section.conflicts %}
### Conflicts

{% for conflict in section.conflicts %}
**{{conflict.topic}}**
- Position A ({{conflict.position_a.source_ids|join(', ')}}): {{conflict.position_a.text}}
- Position B ({{conflict.position_b.source_ids|join(', ')}}): {{conflict.position_b.text}}
{% endfor %}
{% endif %}

{% if section.known_gaps %}
### Known Gaps

{% for gap in section.known_gaps %}
- {{gap}}
{% endfor %}
{% endif %}

{% endfor %}

---

## Checklists

### Implementation
{% for item in checklists.implementation %}
- [ ] {{item}}
{% endfor %}

### Testing
{% for item in checklists.testing %}
- [ ] {{item}}
{% endfor %}

### Go-Live
{% for item in checklists.go_live %}
- [ ] {{item}}
{% endfor %}

### Migration
{% for item in checklists.migration %}
- [ ] {{item}}
{% endfor %}

### Audit
{% for item in checklists.audit %}
- [ ] {{item}}
{% endfor %}

---

## FAQs

{% for faq in faqs %}
**Q: {{faq.q}}**
A: {{faq.a}} {% for sid in faq.source_ids %}[{{sid}}]{% endfor %}

{% endfor %}

---

## Source Index

| ID | Title | Tier | Topics |
|----|-------|------|--------|
{% for source in sources %}| {{source.id}} | {{source.title}} | {{source.tier}} | {{source.topics|join(', ')}} |
{% endfor %}

---

## Known Gaps

The following gaps remain:

{% for section in sections %}
{% if section.known_gaps %}
### {{section.title}}
{% for gap in section.known_gaps %}
- {{gap}}
{% endfor %}
{% endif %}
{% endfor %}

---

> Sources reviewed: {{sources|length}} | Subtopics covered: {{sections|length}} | Claims extracted: {{total_claims}}
