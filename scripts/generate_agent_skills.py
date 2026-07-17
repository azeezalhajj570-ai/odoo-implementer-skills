#!/usr/bin/env python3
"""
Generate OpenCode agent workflow skills from knowledge-factory skill packages.

Reads each skill package under skills/ and writes a SKILL.md under
.agents/skills/odoo-<name>/ so the agent can invoke them as workflow skills.
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
AGENTS_SKILLS_DIR = ROOT / ".agents" / "skills"


def sanitize(name: str) -> str:
    """Convert a skill directory name to a kebab-case skill folder name."""
    return name.lower().replace("_", "-").replace(" ", "-").strip("-")


def build_skill_markdown(skill_dir: Path) -> str:
    skill_json = skill_dir / "skill.json"
    prompt_md = skill_dir / "prompt.md"
    capability_json = skill_dir / "capability.json"
    knowledge_json = skill_dir / "knowledge.json"

    if not skill_json.exists():
        raise FileNotFoundError(f"No skill.json in {skill_dir}")

    with open(skill_json) as f:
        data = json.load(f)

    skill_id = data.get("skill_id", skill_dir.name)
    name = data.get("name", skill_dir.name)
    description = data.get("description", "")
    domain = data.get("domain", "")
    subdomain = data.get("subdomain", "")
    capabilities = data.get("capabilities", [])
    limitations = data.get("limitations", [])
    deps = data.get("dependencies", {}).get("skills", [])
    modules = data.get("dependencies", {}).get("odoo_modules", [])
    tags = data.get("tags", [])

    # Trigger phrases from capabilities + tags
    trigger_caps = [c["name"] for c in capabilities[:5]]
    trigger_phrases = ", ".join(trigger_caps) if trigger_caps else domain

    # Capability bullets
    cap_bullets = []
    for c in capabilities:
        cap_id = c.get("id", "")
        cap_name = c.get("name", "")
        cap_desc = c.get("description", "")
        cap_bullets.append(f"- **{cap_name}** (`{cap_id}`): {cap_desc}")
    cap_section = "\n".join(cap_bullets) if cap_bullets else "- No capabilities defined."

    # Limitations
    lim_bullets = [f"- {lim}" for lim in limitations]
    limitations_section = "\n".join(lim_bullets) if lim_bullets else "- None documented."

    # Dependencies
    dep_skills = [d.get("skill_id", "") for d in deps]
    dep_section = ""
    if dep_skills:
        dep_section = f"\n- **Depends on skills:** {', '.join(dep_skills)}"
    if modules:
        dep_section += f"\n- **Relevant modules:** {', '.join(modules)}"

    # Supported modules
    supported = data.get("supported_modules", [])
    required_modules = [m["name"] for m in supported if m.get("required")]
    optional_modules = [m["name"] for m in supported if not m.get("required")]
    module_section = ""
    if required_modules:
        module_section += f"\n- **Required modules:** {', '.join(required_modules)}"
    if optional_modules:
        module_section += f"\n- **Optional modules:** {', '.join(optional_modules)}"

    skill_folder = f"odoo-{sanitize(skill_dir.name)}"
    relative_dir = f"skills/{skill_dir.name}"

    md = f"""# Skill: {skill_folder}

{name} — {description} Use when the user asks about {trigger_phrases} in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `{relative_dir}/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `{relative_dir}/skill.json` — metadata, modules, dependencies
   - `{relative_dir}/capability.json` — detailed capability definitions
   - `{relative_dir}/knowledge.json` — key models, files, crons, security groups
   - `{relative_dir}/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

{cap_section}

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

{limitations_section}

## Context

- **Domain:** {domain}
- **Subdomain:** {subdomain}
- **Skill ID:** {skill_id}
- **Knowledge package:** `{relative_dir}/`
{module_section}
{dep_section}
"""
    return md


def generate_skill(skill_dir: Path) -> Path:
    folder_name = f"odoo-{sanitize(skill_dir.name)}"
    target_dir = AGENTS_SKILLS_DIR / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    md = build_skill_markdown(skill_dir)
    skill_file = target_dir / "SKILL.md"
    skill_file.write_text(md)
    logger.info(f"Generated {skill_file}")
    return skill_file


def main():
    if not SKILLS_DIR.exists():
        logger.error(f"Skills directory not found: {SKILLS_DIR}")
        return 1

    AGENTS_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not (skill_dir / "skill.json").exists():
            logger.warning(f"Skipping {skill_dir.name}: no skill.json")
            continue
        try:
            path = generate_skill(skill_dir)
            generated.append(path)
        except Exception as e:
            logger.error(f"Failed to generate skill for {skill_dir.name}: {e}")
            raise

    logger.info(f"Generated {len(generated)} agent workflow skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
