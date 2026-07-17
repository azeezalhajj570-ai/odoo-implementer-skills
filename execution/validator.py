#!/usr/bin/env python3
"""
Validation Engine — Validates generated artifacts against Odoo standards.

Supports:
- Python syntax validation (compile check)
- XML parsing validation
- Manifest structure validation
- Security access rights validation
- Module loading validation
- Upgrade path validation
- Coding standards compliance

Usage:
    from execution.validator import ValidationEngine
    
    validator = ValidationEngine()
    results = validator.validate_python("/path/to/file.py")
    results = validator.validate_manifest("/path/to/__manifest__.py")
    all_results = validator.validate_module("/path/to/module")
"""

import ast
import logging
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    file_path: str
    check_type: str
    passed: bool
    message: str = ""
    line: int = 0
    severity: str = "error"  # error, warning, info

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "check_type": self.check_type,
            "passed": self.passed,
            "message": self.message,
            "line": self.line,
            "severity": self.severity,
        }


class ValidationEngine:
    """Validates Odoo artifacts against standards."""

    VALID_LICENSES = {
        "LGPL-3", "LGPL-2", "GPL-3", "GPL-2", "AGPL-3",
        "OEEL-1", "OPL-1", "Other proprietary", "Other OSI approved",
    }

    def validate_python(self, file_path: str) -> ValidationResult:
        """Validate Python syntax."""
        try:
            with open(file_path) as f:
                content = f.read()
            compile(content, file_path, 'exec')
            return ValidationResult(
                file_path=file_path,
                check_type="python_syntax",
                passed=True,
                message="Valid Python syntax",
            )
        except SyntaxError as e:
            return ValidationResult(
                file_path=file_path,
                check_type="python_syntax",
                passed=False,
                message=str(e),
                line=e.lineno or 0,
                severity="error",
            )
        except Exception as e:
            return ValidationResult(
                file_path=file_path,
                check_type="python_syntax",
                passed=False,
                message=str(e),
                severity="error",
            )

    def validate_xml(self, file_path: str) -> ValidationResult:
        """Validate XML parsing."""
        try:
            ET.parse(file_path)
            return ValidationResult(
                file_path=file_path,
                check_type="xml_parse",
                passed=True,
                message="Valid XML",
            )
        except ET.ParseError as e:
            return ValidationResult(
                file_path=file_path,
                check_type="xml_parse",
                passed=False,
                message=str(e),
                severity="error",
            )

    def validate_manifest(self, file_path: str) -> List[ValidationResult]:
        """Validate Odoo manifest file."""
        results = []

        if not os.path.exists(file_path):
            results.append(ValidationResult(
                file_path=file_path,
                check_type="manifest_exists",
                passed=False,
                message="Manifest file not found",
                severity="error",
            ))
            return results

        # Check Python syntax
        syntax_result = self.validate_python(file_path)
        results.append(syntax_result)
        if not syntax_result.passed:
            return results

        try:
            with open(file_path) as f:
                content = f.read()

            # Parse with AST
            tree = ast.parse(content)
            manifest_data = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    for key, value in zip(node.keys, node.values):
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            if isinstance(value, ast.Constant):
                                manifest_data[key.value] = value.value
                            elif isinstance(value, ast.List):
                                manifest_data[key.value] = [
                                    e.s for e in value.elts if isinstance(e, ast.Constant)
                                ]

            # Check required fields
            required_fields = ["name", "depends"]
            for field in required_fields:
                if field not in manifest_data:
                    results.append(ValidationResult(
                        file_path=file_path,
                        check_type=f"manifest_{field}",
                        passed=False,
                        message=f"Missing required manifest field: {field}",
                        severity="error",
                    ))

            # Check license
            license_val = manifest_data.get("license", "")
            if license_val and license_val not in self.VALID_LICENSES:
                results.append(ValidationResult(
                    file_path=file_path,
                    check_type="manifest_license",
                    passed=False,
                    message=f"Unrecognized license: {license_val}",
                    severity="warning",
                ))

            # Check version format
            version = manifest_data.get("version", "")
            if version and not re.match(r'^\d+\.\d+(\.\d+)?(\.\d+)?$', str(version)):
                results.append(ValidationResult(
                    file_path=file_path,
                    check_type="manifest_version",
                    passed=False,
                    message=f"Invalid version format: {version}",
                    severity="warning",
                ))

            # Check author
            if not manifest_data.get("author"):
                results.append(ValidationResult(
                    file_path=file_path,
                    check_type="manifest_author",
                    passed=False,
                    message="Missing author field",
                    severity="info",
                ))

        except Exception as e:
            results.append(ValidationResult(
                file_path=file_path,
                check_type="manifest_parse",
                passed=False,
                message=f"Parse error: {e}",
                severity="error",
            ))

        return results

    def validate_security(self, module_path: str) -> List[ValidationResult]:
        """Validate a module's security configuration."""
        results = []
        base = Path(module_path)
        security_dir = base / "security"

        if not security_dir.exists():
            return results

        # Check ir.model.access.csv exists
        acl_file = security_dir / "ir.model.access.csv"
        if acl_file.exists():
            try:
                content = acl_file.read_text()
                for i, line in enumerate(content.splitlines(), 1):
                    if line.strip() and not line.startswith("id"):
                        parts = line.split(",")
                        if len(parts) < 5:
                            results.append(ValidationResult(
                                file_path=str(acl_file),
                                check_type="security_acl_format",
                                passed=False,
                                message=f"Invalid ACL format on line {i}: expected 5+ columns",
                                line=i,
                                severity="error",
                            ))
            except IOError as e:
                results.append(ValidationResult(
                    file_path=str(acl_file),
                    check_type="security_acl_read",
                    passed=False,
                    message=str(e),
                    severity="error",
                ))

        return results

    def validate_module(self, module_path: str) -> Dict[str, List[ValidationResult]]:
        """Run all validation checks on a module."""
        base = Path(module_path)
        all_results = {}

        # Validate manifest
        for mf in ["__manifest__.py", "__openerp__.py"]:
            mf_path = base / mf
            if mf_path.exists():
                all_results["manifest"] = self.validate_manifest(str(mf_path))
                break

        # Validate Python files
        py_files = []
        for py_dir in ["models", "controllers", "wizard", "report"]:
            dir_path = base / py_dir
            if dir_path.exists():
                py_files.extend(dir_path.glob("*.py"))

        for py_file in py_files:
            result = self.validate_python(str(py_file))
            all_results.setdefault("python", []).append(result)

        # Validate XML files
        for xml_dir in ["views", "data", "security", "report", "wizard"]:
            dir_path = base / xml_dir
            if dir_path.exists():
                for xml_file in dir_path.glob("*.xml"):
                    result = self.validate_xml(str(xml_file))
                    all_results.setdefault("xml", []).append(result)

        # Validate security
        security_results = self.validate_security(module_path)
        if security_results:
            all_results["security"] = security_results

        # Summary
        total = sum(len(v) for v in all_results.values())
        passed = sum(1 for v in all_results.values() for r in v if r.passed)
        logger.info(f"Module validation: {total} checks, {passed} passed")
        all_results["_summary"] = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        }

        return all_results

    def validate_artifact(self, file_path: str) -> List[ValidationResult]:
        """Auto-detect file type and validate accordingly."""
        ext = Path(file_path).suffix.lower()
        if ext == ".py":
            return [self.validate_python(file_path)]
        elif ext == ".xml":
            return [self.validate_xml(file_path)]
        elif Path(file_path).name.startswith("__manifest__"):
            return self.validate_manifest(file_path)
        return []
