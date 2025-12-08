#!/bin/bash
# Environment setup script for Q&A Practice Application
# Usage: source ./scripts/setup_env.sh [environment]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENVIRONMENT=${1:-development}

echo -e "${GREEN}Setting up Q&A Practice Application environment...${NC}"

# Export common environment variables
export QAA_APP_NAME="Q&A Practice Application"
export QAA_VERSION="1.0.0"

# Environment-specific settings
case $ENVIRONMENT in
    production)
        export QAA_DEBUG=false
        export QAA_HOST=0.0.0.0
        export QAA_PORT=8000
        export QAA_LOG_LEVEL=WARNING
        export QAA_LOG_FORMAT=json
        echo -e "${GREEN}Production environment configured${NC}"
        ;;
    staging)
        export QAA_DEBUG=true
        export QAA_HOST=0.0.0.0
        export QAA_PORT=8000
        export QAA_LOG_LEVEL=INFO
        export QAA_LOG_FORMAT=json
        echo -e "${YELLOW}Staging environment configured${NC}"
        ;;
    development|*)
        export QAA_DEBUG=true
        export QAA_HOST=127.0.0.1
        export QAA_PORT=8000
        export QAA_LOG_LEVEL=DEBUG
        export QAA_LOG_FORMAT=text
        echo -e "${GREEN}Development environment configured${NC}"
        ;;
esac

# Session settings
export QAA_DEFAULT_SESSION_LENGTH=10
export QAA_MIN_SESSION_LENGTH=5
export QAA_MAX_SESSION_LENGTH=50

# File paths
export QAA_QUESTION_BANK_PATH="src/main/resources/question-bank.csv"

# Performance settings
export QAA_CSV_PARSE_TIMEOUT=2.0
export QAA_UI_RESPONSE_TIMEOUT=0.2
export QAA_TEST_COVERAGE_THRESHOLD=90

# Print current configuration
echo ""
echo "Current Configuration:"
echo "  QAA_DEBUG: $QAA_DEBUG"
echo "  QAA_HOST: $QAA_HOST"
echo "  QAA_PORT: $QAA_PORT"
echo "  QAA_LOG_LEVEL: $QAA_LOG_LEVEL"
echo "  QAA_QUESTION_BANK_PATH: $QAA_QUESTION_BANK_PATH"
echo ""
echo -e "${GREEN}Environment setup complete!${NC}"
