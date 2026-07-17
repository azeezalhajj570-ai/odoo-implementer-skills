#!/usr/bin/env python3
"""
Analyze source code to detect stub implementations, hardcoded data, and keyword-based logic.

Usage:
    python analyze_source.py /path/to/project
"""

import ast
import sys
from pathlib import Path


def is_hardcoded_assignment(node):
    """Detect if a class attribute is initialized with a constant list or dict."""
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                return isinstance(node.value, (ast.List, ast.Dict, ast.Constant))
    return False


def analyze_file(path: Path) -> dict:
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return {"error": "syntax error"}

    hardcoded_count = 0
    function_count = 0
    class_count = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_count += 1
        elif isinstance(node, ast.ClassDef):
            class_count += 1
        elif is_hardcoded_assignment(node):
            hardcoded_count += 1

    return {
        "functions": function_count,
        "classes": class_count,
        "hardcoded_tables": hardcoded_count,
        "risk_flag": hardcoded_count > 3,
    }


def main(project_path: str):
    root = Path(project_path)
    if not root.exists():
        print(f"Path not found: {project_path}")
        sys.exit(1)

    total = {"functions": 0, "classes": 0, "hardcoded_tables": 0, "risk_files": 0}
    for py_file in root.rglob("*.py"):
        result = analyze_file(py_file)
        total["functions"] += result.get("functions", 0)
        total["classes"] += result.get("classes", 0)
        total["hardcoded_tables"] += result.get("hardcoded_tables", 0)
        if result.get("risk_flag"):
            total["risk_files"] += 1

    print(total)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
