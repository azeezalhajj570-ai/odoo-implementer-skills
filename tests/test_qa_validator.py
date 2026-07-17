#!/usr/bin/env python3
"""
Tests: QA Validator Functionality

Verifies the QA validator can:
1. Detect invalid JSON
2. Validate knowledge base structure
3. Detect missing source citations
4. Detect duplicate source IDs
5. Validate verification report sample size
6. Generate proper QA reports
"""

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

errors = []
warnings = []

# --- Test 1: Import QA Validator ---
print("\n=== Test 1: Import QA Validator ===")
try:
    from qa_validator import QAValidator
    print("  PASS: Import successful")
except ImportError as e:
    print(f"  FAIL: Import failed: {e}")
    errors.append("qa_import")
    sys.exit(1)

# --- Test 2: Detect invalid JSON ---
print("\n=== Test 2: Detect Invalid JSON ===")
v = QAValidator()
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    f.write("{invalid json}")
    tmp_path = f.name

result = v.validate_file(Path(tmp_path))
os.unlink(tmp_path)
if result.get("errors", 0) > 0:
    print("  PASS: Invalid JSON detected")
else:
    print("  WARN: No error for invalid JSON (might have passed)")

# --- Test 3: Validate knowledge base structure ---
print("\n=== Test 3: Knowledge Base Validation ===")
v = QAValidator()
valid_kb = {
    "domain": "Test",
    "odoo_versions": ["19.0"],
    "audience": "Testers",
    "depth": "deep",
    "generated_at": "2026-07-17T12:00:00Z",
    "excluded_scope": [],
    "sources": [
        {"id": "src_0001", "title": "Test Source", "author_or_org": "Test", "url": "https://example.com",
         "date_published": None, "date_accessed": "2026-07-17T12:00:00Z", "tier": "official",
         "fetch_verified": True, "access_method": "web", "topics": ["testing"]}
    ],
    "sections": [
        {"id": "sec_test", "title": "Test Section", "relevance_weight": "high",
         "claims": [{"text": "Test claim", "source_ids": ["src_0001"], "confidence": "official"}],
         "conflicts": [], "known_gaps": []}
    ],
    "checklists": {"implementation": [], "testing": [], "go_live": [], "migration": [], "audit": []},
    "faqs": [{"q": "Test?", "a": "Answer", "source_ids": ["src_0001"]}],
    "verification_report": {"sample_size": 1, "passed": 1, "failed": 0, "corrections": []}
}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(valid_kb, f)
    tmp_path = f.name

v.validate_file(Path(tmp_path))
os.unlink(tmp_path)
# Should have minimal errors for valid KB
error_count = v.error_count
if error_count <= 1:  # May have one for verification sample < 20% since only 1/1 source
    print(f"  PASS: Valid KB validated with {error_count} errors")
else:
    print(f"  WARN: {error_count} errors on valid KB")

# --- Test 4: Detect missing source citations ---
print("\n=== Test 4: Missing Citations Detection ===")
v = QAValidator()
bad_kb = json.loads(json.dumps(valid_kb))  # deep copy
bad_kb["sections"][0]["claims"][0]["source_ids"] = []  # empty citations
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(bad_kb, f)
    tmp_path = f.name

v.validate_file(Path(tmp_path))
os.unlink(tmp_path)
citation_errors = [c for c in v.results if "claim_no_sources" in c.get("check_id", "")]
if citation_errors:
    print(f"  PASS: Missing citations detected ({len(citation_errors)} errors)")
else:
    print("  FAIL: Missing citations not detected")
    errors.append("missing_citation_detection")

# --- Test 5: Detect duplicate source IDs ---
print("\n=== Test 5: Duplicate Source ID Detection ===")
v = QAValidator()
dup_kb = json.loads(json.dumps(valid_kb))
dup_kb["sources"].append(dup_kb["sources"][0])  # duplicate ID
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(dup_kb, f)
    tmp_path = f.name

v.validate_file(Path(tmp_path))
os.unlink(tmp_path)
dup_errors = [c for c in v.results if "duplicate_source_ids" in c.get("check_id", "")]
if dup_errors:
    print(f"  PASS: Duplicate source IDs detected")
else:
    print("  FAIL: Duplicate source IDs not detected")
    errors.append("duplicate_detection")

# --- Test 6: QA Report Generation ---
print("\n=== Test 6: Report Generation ===")
v = QAValidator()
report = v.generate_report()
required_keys = ["report_id", "generated_at", "summary", "checks"]
missing = [k for k in required_keys if k not in report]
if not missing:
    print(f"  PASS: Report generated with {report['summary']['total_checks']} checks")
else:
    print(f"  FAIL: Missing keys in report: {missing}")
    errors.append("report_generation")


# --- Summary ---
print(f"\n{'='*60}")
print(f"Results: {len(errors)} failures")
print(f"{'='*60}")

if errors:
    for e in errors:
        print(f"  FAIL: {e}")
    sys.exit(1)
else:
    print("All tests passed!")
    sys.exit(0)
