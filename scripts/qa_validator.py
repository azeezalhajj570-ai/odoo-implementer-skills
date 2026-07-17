#!/usr/bin/env python3
"""
Odoo Knowledge Factory — QA Validator

Validates Knowledge Factory artifacts for integrity, consistency,
and compliance with the canonical schemas.

Usage:
    python3 qa_validator.py --path output/databases/accounting_knowledge.json
    python3 qa_validator.py --path skills/accounting/ --recursive
    python3 qa_validator.py --all --domain accounting
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent

# Schema-to-validator mapping
VALIDATORS = {}


def register_validator(schema_name: str):
    """Decorator to register validator functions."""
    def decorator(func):
        VALIDATORS[schema_name] = func
        return func
    return decorator


class QAValidator:
    """Validates Knowledge Factory artifacts."""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.results: List[dict] = []
        self.error_count = 0
        self.warning_count = 0

    def validate_file(self, path: Path) -> dict:
        """Validate a single artifact file."""
        logger.info(f"Validating {path}")
        
        if not path.exists():
            return self._fail("file_not_found", f"File not found: {path}", severity="error")

        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self._fail("invalid_json", f"Invalid JSON: {e}", severity="error")
            return {
                "path": str(path),
                "schema": None,
                "errors": self.error_count,
                "warnings": self.warning_count,
                "checks": len(self.results),
            }

        # Detect schema from filename/content
        schema_name = self._detect_schema(path, data)
        
        if schema_name:
            validator = VALIDATORS.get(schema_name)
            if validator:
                validator(self, data, path)
            else:
                self._warn("no_validator", f"No validator for schema {schema_name}")
        
        # Run cross-cutting checks
        self._check_cross_cutting(data, path)
        
        return {
            "path": str(path),
            "schema": schema_name,
            "errors": self.error_count,
            "warnings": self.warning_count,
            "checks": len(self.results),
        }

    def validate_directory(self, path: Path, recursive: bool = False):
        """Validate all JSON files in a directory."""
        pattern = "**/*.json" if recursive else "*.json"
        for json_file in sorted(path.glob(pattern)):
            self.validate_file(json_file)

    def _detect_schema(self, path: Path, data: dict) -> Optional[str]:
        """Detect schema from file path and content structure.
        
        Uses both filename heuristics and content structure analysis
        to handle temp files and in-memory data.
        """
        path_str = str(path).lower()
        
        # Content-based detection (works for temp files)
        if isinstance(data, dict):
            if "sources" in data and "sections" in data:
                return "knowledge_base"
            if "modules" in data and "dependency_graph" in data:
                return "module_catalog"
            if "models" in data and data["models"] and isinstance(data["models"], list):
                first = data["models"][0]
                if isinstance(first, dict) and "name" in first and "module" in first:
                    return "model_catalog"
            if "skill_id" in data and "prompt" in data:
                return "skill_definition"
            if "chunking" in data and "embedding" in data:
                return "metadata"
            if "summary" in data and "checks" in data:
                return "validation_report"
        
        # Filename-based detection (for production files)
        if "knowledge" in path_str:
            return "knowledge_base"
        if "module" in path_str:
            return "module_catalog"
        if "model" in path_str:
            return "model_catalog"
        if "skill" in path_str:
            return "skill_definition"
        if "rag" in path_str or "metadata" in path_str:
            return "metadata"
        if "qa" in path_str or "validation" in path_str:
            return "validation_report"
        
        return None

    def _check_cross_cutting(self, data: dict, path: Path):
        """Run checks applicable to all artifact types."""
        # Check for empty/null values in critical fields
        if isinstance(data, dict):
            for key in ["domain", "generated_at", "version"]:
                if key in data and not data[key]:
                    self._warn(f"empty_{key}", f"{path.name}: {key} is empty")

    def _fail(self, check_id: str, message: str, severity: str = "error") -> dict:
        """Record a failed check."""
        self.error_count += 1 if severity == "error" else 0
        self.warning_count += 1 if severity == "warning" else 0
        
        result = {
            "check_id": check_id,
            "severity": severity,
            "status": "failed",
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.results.append(result)
        log_fn = logger.error if severity == "error" else logger.warning
        log_fn(f"[{severity}] {check_id}: {message}")
        return result

    def _warn(self, check_id: str, message: str) -> dict:
        return self._fail(check_id, message, severity="warning")

    def _pass(self, check_id: str, message: str) -> dict:
        result = {
            "check_id": check_id,
            "severity": "info",
            "status": "passed",
            "message": message,
        }
        self.results.append(result)
        return result

    def generate_report(self) -> dict:
        """Generate the final QA report."""
        return {
            "report_id": f"qa_{datetime.now():%Y%m%d_%H%M%S}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_checks": len(self.results),
                "passed": sum(1 for r in self.results if r["status"] == "passed"),
                "failed": self.error_count,
                "warnings": self.warning_count,
            },
            "checks": self.results,
        }

    def write_report(self, output_path: Path):
        """Write QA report to file."""
        report = self.generate_report()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"QA report written to {output_path}")


# --- Schema-specific validators ---

@register_validator("knowledge_base")
def validate_knowledge_base(v: QAValidator, data: dict, path: Path):
    """Validate a knowledge base artifact."""
    # Required top-level fields
    for field in ["domain", "odoo_versions", "sources", "sections"]:
        if field not in data:
            v._fail(f"missing_field_{field}", f"Missing required field: {field}")
    
    # Source IDs must be unique
    if "sources" in data:
        ids = [s.get("id") for s in data["sources"]]
        if len(ids) != len(set(ids)):
            v._fail("duplicate_source_ids", "Duplicate source IDs found")
        
        # Source ID pattern check
        for s in data["sources"]:
            sid = s.get("id", "")
            if sid and not sid.startswith("src_"):
                v._warn(f"invalid_source_id_{sid}", f"Source ID should start with src_: {sid}")
    
    # Every claim must cite at least one source
    if "sections" in data:
        for section in data["sections"]:
            for claim in section.get("claims", []):
                if not claim.get("source_ids"):
                    v._fail("claim_no_sources", f"Claim without source_ids: {claim.get('text', '')[:80]}")

    # Conflicts must have sources on both sides
    for section in data.get("sections", []):
        for conflict in section.get("conflicts", []):
            if not conflict.get("position_a", {}).get("source_ids"):
                v._fail("conflict_no_source_a", f"Conflict without position_a sources: {conflict.get('topic')}")
            if not conflict.get("position_b", {}).get("source_ids"):
                v._fail("conflict_no_source_b", f"Conflict without position_b sources: {conflict.get('topic')}")

    # Verification report sample size must be >= 20%
    vr = data.get("verification_report", {})
    if vr.get("sample_size", 0) > 0:
        total = len(data.get("sources", []))
        ratio = vr["sample_size"] / total if total > 0 else 0
        if ratio < 0.2:
            v._warn("low_verification_sample", 
                    f"Verification sample {vr['sample_size']}/{total} ({ratio:.0%}) < 20%")


@register_validator("module_catalog")
def validate_module_catalog(v: QAValidator, data: dict, path: Path):
    """Validate a module catalog artifact."""
    for field in ["modules", "dependency_graph"]:
        if field not in data:
            v._fail(f"missing_field_{field}", f"Missing required field: {field}")
    
    # Each module should have technical_name
    for module in data.get("modules", []):
        if not module.get("technical_name"):
            v._fail("module_no_tech_name", f"Module without technical_name")


@register_validator("skill_definition")
def validate_skill_definition(v: QAValidator, data: dict, path: Path):
    """Validate a skill definition artifact."""
    for field in ["skill_id", "name", "purpose", "input", "output", "prompt", "validation"]:
        if field not in data:
            v._fail(f"missing_field_{field}", f"Missing required field: {field}")
    
    # Check source_ids if present
    if "source_ids" in data and data["source_ids"]:
        pass  # Would cross-reference against knowledge base in context


def main():
    parser = argparse.ArgumentParser(description="Odoo Knowledge Factory QA Validator")
    parser.add_argument("--path", help="Path to artifact file or directory")
    parser.add_argument("--recursive", action="store_true", help="Recurse into directories")
    parser.add_argument("--all", action="store_true", help="Validate all artifacts in output/")
    parser.add_argument("--domain", help="Domain name (for --all)")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings")
    parser.add_argument("--output", "-o", help="Output path for QA report JSON")
    
    args = parser.parse_args()
    validator = QAValidator(strict=args.strict)
    
    if args.all and args.domain:
        base = ROOT / "output" / "databases"
        validator.validate_directory(base)
        skill_dir = ROOT / "skills" / args.domain
        if skill_dir.exists():
            validator.validate_directory(skill_dir, recursive=True)
    elif args.path:
        target = Path(args.path)
        if target.is_dir():
            validator.validate_directory(target, recursive=args.recursive)
        else:
            validator.validate_file(target)
    else:
        parser.print_help()
        sys.exit(1)
    
    report = validator.generate_report()
    print(f"\nQA Summary:")
    print(f"  Total checks: {report['summary']['total_checks']}")
    print(f"  Passed:       {report['summary']['passed']}")
    print(f"  Failed:       {report['summary']['failed']}")
    print(f"  Warnings:     {report['summary']['warnings']}")
    
    if args.output:
        validator.write_report(Path(args.output))
    
    sys.exit(1 if report["summary"]["failed"] > 0 else 0)


if __name__ == "__main__":
    main()
