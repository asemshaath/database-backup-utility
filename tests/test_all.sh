#!/bin/bash

cd "$(dirname "$0")"

echo "======================================"
echo "Afterchive Test Suite"
echo "======================================"
echo ""

# Track results
PASSED=0
FAILED=0

run_test() {
    local test_script=$1
    local test_name=$2
    
    echo "Running test: $test_name"
    echo "----------------------------------------"
    # Run test, capture all output
    if bash "$test_script" > /tmp/afterchive_testing.log 2>&1; then
        echo "✓ $test_name - PASSED"
        echo ""
        PASSED=$((PASSED + 1))
    else
        echo "✗ $test_name - FAILED"
        echo ""
        echo "Error details:"
        tail -20 /tmp/test_output.log  # Show last 20 lines of errors
        echo ""
        FAILED=$((FAILED + 1))
    fi
}

# Run all tests (each rebuilds containers)
run_test "postgres_local_test.sh" "Postgres --> Local"
run_test "postgres_gcp_test.sh" "Postgres --> GCP"

# Final summary
echo ""
echo "Summary"
echo "======================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

echo "Detailed logs available in /tmp/afterchive_testing.log"

if [ $FAILED -gt 0 ]; then
    echo "✗ SOME TESTS FAILED"
    exit 1
fi

echo "✓ ALL TESTS PASSED"
exit 0