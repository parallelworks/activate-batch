#!/bin/bash
# =============================================================================
# Local Workflow Runner
# =============================================================================
# Run the batch submitter workflow locally without the ACTIVATE platform.
#
# Usage:
#   ./tools/run_local.sh                    # Run with defaults
#   ./tools/run_local.sh --dry-run          # Show what would execute
#   ./tools/run_local.sh -v                 # Verbose output
#   ./tools/run_local.sh --keep-work-dir    # Keep temp files for inspection
#
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKFLOW="${REPO_ROOT}/workflow.yaml"
RUNNER="${SCRIPT_DIR}/workflow_runner.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=============================================="
echo "  ACTIVATE Batch Submitter - Local Runner"
echo -e "==============================================${NC}"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found${NC}"
    exit 1
fi

# Check for PyYAML
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${YELLOW}Installing PyYAML...${NC}"
    pip3 install pyyaml --quiet
fi

# Check workflow exists
if [ ! -f "${WORKFLOW}" ]; then
    echo -e "${RED}Error: workflow.yaml not found at ${WORKFLOW}${NC}"
    exit 1
fi

# Run the workflow
echo "Running: python3 ${RUNNER} ${WORKFLOW} $@"
echo ""

python3 "${RUNNER}" "${WORKFLOW}" "$@"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}Workflow completed successfully!${NC}"
else
    echo -e "${RED}Workflow failed with exit code ${exit_code}${NC}"
fi

exit $exit_code
