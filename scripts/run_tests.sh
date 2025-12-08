#!/bin/bash
# Test runner script for Q&A Practice Application
# Usage: ./scripts/run_tests.sh [test_type] [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TEST_TYPE=${1:-all}
COVERAGE_THRESHOLD=90

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Q&A Practice Application Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to run unit tests
run_unit_tests() {
    echo ""
    echo -e "${GREEN}Running Unit Tests...${NC}"
    uv run pytest tests/unit/ -v --override-ini="addopts=" --tb=short
}

# Function to run contract tests
run_contract_tests() {
    echo ""
    echo -e "${GREEN}Running Contract Tests...${NC}"
    uv run pytest tests/contract/ -v --override-ini="addopts=" --tb=short
}

# Function to run integration tests
run_integration_tests() {
    echo ""
    echo -e "${GREEN}Running Integration Tests...${NC}"
    uv run pytest tests/integration/ -v --override-ini="addopts=" --tb=short
}

# Function to run quality tests
run_quality_tests() {
    echo ""
    echo -e "${GREEN}Running Quality Tests...${NC}"
    uv run pytest tests/quality/ -v --override-ini="addopts=" --tb=short
}

# Function to run all tests with coverage
run_all_tests_with_coverage() {
    echo ""
    echo -e "${GREEN}Running All Tests with Coverage...${NC}"
    uv run pytest tests/unit tests/contract tests/integration \
        --cov=src \
        --cov-report=term \
        --cov-report=html:coverage_html \
        --override-ini="addopts=" \
        -v --tb=short
    
    echo ""
    echo -e "${GREEN}Coverage report generated at: coverage_html/index.html${NC}"
}

# Function to run quick smoke tests
run_smoke_tests() {
    echo ""
    echo -e "${GREEN}Running Smoke Tests...${NC}"
    uv run pytest tests/unit/test_models/test_question.py \
        tests/unit/test_services/test_question_service.py \
        -v --override-ini="addopts=" --tb=short -x
}

# Function to run performance tests
run_performance_tests() {
    echo ""
    echo -e "${GREEN}Running Performance Tests...${NC}"
    uv run pytest tests/quality/test_performance.py -v --override-ini="addopts=" --tb=short
}

# Function to run security tests
run_security_tests() {
    echo ""
    echo -e "${GREEN}Running Security Tests...${NC}"
    uv run pytest tests/quality/test_security.py -v --override-ini="addopts=" --tb=short
}

# Print test summary
print_summary() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Test Types Available:"
    echo "  all        - Run all tests with coverage"
    echo "  unit       - Run unit tests only"
    echo "  contract   - Run contract tests only"
    echo "  integration- Run integration tests only"
    echo "  quality    - Run quality tests only"
    echo "  smoke      - Run quick smoke tests"
    echo "  performance- Run performance tests"
    echo "  security   - Run security tests"
    echo ""
    echo "Usage: ./scripts/run_tests.sh [test_type]"
}

# Main execution
case $TEST_TYPE in
    unit)
        run_unit_tests
        ;;
    contract)
        run_contract_tests
        ;;
    integration)
        run_integration_tests
        ;;
    quality)
        run_quality_tests
        ;;
    smoke)
        run_smoke_tests
        ;;
    performance)
        run_performance_tests
        ;;
    security)
        run_security_tests
        ;;
    coverage|all)
        run_all_tests_with_coverage
        ;;
    help|--help|-h)
        print_summary
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        print_summary
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Tests completed!${NC}"
