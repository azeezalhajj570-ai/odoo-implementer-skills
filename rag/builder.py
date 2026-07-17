#!/usr/bin/env python3
"""
RAG Builder — Chunking, Embedding Metadata, and Index Generation

Prepares skill knowledge for RAG (Retrieval-Augmented Generation) indexing.
Supports multiple chunking strategies and generates embedding-compatible
metadata for vector database ingestion.

Usage:
    from rag.builder import RAGBuilder
    
    builder = RAGBuilder(chunk_strategy="by_section", max_chunk_size=512)
    chunks = builder.chunk_skill(skill_path)
    metadata = builder.build_metadata(skill, chunks)
"""

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


class RAGBuilder:
    """Builds RAG-compatible chunks, embeddings metadata, and search indexes from skills."""

    def __init__(self, chunk_strategy: str = "by_section", 
                 max_chunk_size: int = 512,
                 overlap: int = 50):
        self.chunk_strategy = chunk_strategy
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_skill(self, skill_path: Path) -> List[dict]:
        """Chunk a skill package into RAG-ready pieces."""
        chunks = []

        # Chunk skill.json
        skill_file = skill_path / "skill.json"
        if skill_file.exists():
            chunks.extend(self._chunk_file(skill_file, "skill_metadata", "skill.json"))

        # Chunk knowledge.json
        knowledge_file = skill_path / "knowledge.json"
        if knowledge_file.exists():
            chunks.extend(self._chunk_file(knowledge_file, "knowledge", "knowledge.json"))

        # Chunk capability.json
        cap_file = skill_path / "capability.json"
        if cap_file.exists():
            with open(cap_file) as f:
                data = json.load(f)
            for cap in data.get("capabilities", []):
                chunks.append({
                    "chunk_id": f"cap_{cap.get('id', 'unknown')}",
                    "content": f"Capability: {cap.get('name')}. {cap.get('description')}",
                    "source": "capability.json",
                    "section": "capabilities",
                    "metadata": {
                        "capability_id": cap.get("id"),
                        "capability_name": cap.get("name"),
                        "confidence": cap.get("confidence", "medium"),
                    }
                })

        # Chunk prompt.md
        prompt_file = skill_path / "prompt.md"
        if prompt_file.exists():
            chunks.extend(self._chunk_markdown_file(prompt_file, "prompt"))

        # Chunk evaluation files
        eval_dir = skill_path / "evaluation"
        if eval_dir.exists():
            for eval_file in sorted(eval_dir.glob("*.json")):
                with open(eval_file) as f:
                    eval_data = json.load(f)
                for item in eval_data:
                    chunks.append({
                        "chunk_id": f"eval_{item.get('id', 'unknown')}",
                        "content": f"Q: {item.get('question')}\nA: {item.get('expected_answer')}",
                        "source": eval_file.name,
                        "section": "evaluation",
                        "metadata": {
                            "eval_id": item.get("id"),
                            "type": item.get("type"),
                            "difficulty": item.get("difficulty"),
                        }
                    })

        # Chunk playbooks
        playbook_dir = skill_path / "playbooks"
        if playbook_dir.exists():
            for pb_file in sorted(playbook_dir.glob("*.md")):
                chunks.extend(self._chunk_markdown_file(pb_file, "playbook"))

        logger.info(f"Generated {len(chunks)} RAG chunks for {skill_path.name}")
        return chunks

    def _chunk_file(self, file_path: Path, section: str, source: str) -> List[dict]:
        """Chunk a JSON file by top-level keys."""
        chunks = []
        try:
            with open(file_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return chunks

        if isinstance(data, dict):
            for key, value in data.items():
                content = json.dumps({key: value}, indent=2)
                chunk_id = f"{section}_{key}_{self._hash(content[:64])}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "content": content,
                    "source": source,
                    "section": f"{section}.{key}",
                    "metadata": {"parent_key": key}
                })
        return chunks

    def _chunk_markdown_file(self, file_path: Path, section: str) -> List[dict]:
        """Chunk a markdown file by headings."""
        chunks = []
        try:
            text = file_path.read_text()
        except IOError:
            return chunks

        sections = re.split(r'(?=^# )', text, flags=re.MULTILINE)
        for i, sec_text in enumerate(sections):
            if not sec_text.strip():
                continue
            chunk_id = f"{section}_sec_{i}_{self._hash(sec_text[:64])}"
            chunks.append({
                "chunk_id": chunk_id,
                "content": sec_text.strip(),
                "source": file_path.name,
                "section": f"{section}",
                "metadata": {}
            })
        return chunks

    def build_metadata(self, skill_path: Path, chunks: List[dict]) -> dict:
        """Build complete RAG metadata for a skill."""
        skill_file = skill_path / "skill.json"
        skill_name = skill_path.name
        domain = ""
        version = ""
        
        if skill_file.exists():
            try:
                with open(skill_file) as f:
                    data = json.load(f)
                skill_name = data.get("name", skill_name)
                domain = data.get("domain", "")
                version = data.get("version", "")
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "artifact_id": f"skill_{skill_path.name}",
            "type": "skill",
            "domain": domain,
            "subdomain": "",
            "version": version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": sum(len(c["content"]) for c in chunks),
            "word_count": sum(len(c["content"].split()) for c in chunks),
            "tags": [domain.lower()] if domain else [],
            "chunking": {
                "strategy": self.chunk_strategy,
                "max_chunk_size": self.max_chunk_size,
                "overlap": self.overlap,
                "chunks": [
                    {
                        "chunk_id": c["chunk_id"],
                        "section_id": c.get("section", ""),
                        "source": c.get("source", ""),
                    }
                    for c in chunks
                ]
            },
            "embedding": {
                "model": "text-embedding-3-small",
                "dimensions": 1536,
                "distance_metric": "cosine",
            },
            "cross_references": [],
            "search_index": {
                "keywords": [domain.lower()] if domain else [],
                "key_phrases": [],
                "models_referenced": [],
                "modules_referenced": [],
            }
        }

    def build_flat_index(self, chunks: List[dict]) -> List[dict]:
        """Build a flat search index from chunks (for vector DB ingestion)."""
        return [
            {
                "id": c["chunk_id"],
                "text": c["content"],
                "source": c.get("source", ""),
                "section": c.get("section", ""),
                "metadata": c.get("metadata", {}),
            }
            for c in chunks
        ]

    def _hash(self, content: str) -> str:
        """Generate a short content hash for chunk IDs."""
        return hashlib.md5(content.encode()).hexdigest()[:8]


def build_all_skills_rag(skills_base: Optional[Path] = None) -> Dict[str, List[dict]]:
    """Build RAG index for all skills. Returns dict of {skill_id: [chunks]}."""
    base = skills_base or ROOT / "skills"
    builder = RAGBuilder()
    all_chunks = {}

    for skill_dir in sorted(base.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "skill.json"
        if not skill_file.exists():
            continue

        chunks = builder.chunk_skill(skill_dir)
        metadata = builder.build_metadata(skill_dir, chunks)
        skill_id = skill_dir.name
        all_chunks[skill_id] = {
            "chunks": chunks,
            "metadata": metadata,
            "flat_index": builder.build_flat_index(chunks),
        }
        logger.info(f"RAG index built for {skill_id}: {len(chunks)} chunks")

    return all_chunks
