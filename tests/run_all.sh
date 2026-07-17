#!/usr/bin/env bash
# Odoo Knowledge Factory — Run All Tests
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAILURES=0

echo "=========================================="
echo " Odoo Knowledge Factory — Test Suite"
echo "=========================================="
echo ""

run_test() {
    local test_name="$1"
    local test_script="$2"
    echo ""
    echo "--- $test_name ---"
    if python3 "$test_script"; then
        echo "  >>> $test_name: PASSED"
    else
        echo "  >>> $test_name: FAILED"
        FAILURES=$((FAILURES + 1))
    fi
}

# Test 1: Schema validity
run_test "Schema Validity" "$ROOT/tests/test_schema_validity.py"

# Test 2: QA Validator
run_test "QA Validator" "$ROOT/tests/test_qa_validator.py"

# Test 3: Orchestrator (requires PyYAML)
if python3 -c "import yaml" 2>/dev/null; then
    run_test "Orchestrator" "$ROOT/tests/test_orchestrator.py"
else
    echo ""
    echo "--- Orchestrator Tests ---"
    echo "  SKIPPED: PyYAML not installed"
fi

# Test 4: Platform Integration
run_test "Platform Integration" "$ROOT/tests/test_platform_integration.py"

echo ""
echo "=========================================="
if [ $FAILURES -eq 0 ]; then
    echo " All tests passed!"
    exit 0
else
    echo " $FAILURES test(s) failed"
    exit 1
fi
