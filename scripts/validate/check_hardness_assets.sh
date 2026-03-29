#!/bin/bash
set -euo pipefail

echo "=== Validating Hardness Engineering Assets ==="
echo ""

ERRORS=0
REQUIRED_FILES=(
  "system/HARDNESS_ENGINEERING.md"
  "agents/evaluator/AGENTS.md"
  "agents/policy-guardian/AGENTS.md"
  "evals/README.md"
  "evals/rubrics/team-hardness-rubric.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ $file"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""
echo "Validation complete: $ERRORS errors found"
exit $ERRORS
