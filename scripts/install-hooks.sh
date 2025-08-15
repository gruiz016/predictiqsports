#!/usr/bin/env bash
set -euo pipefail

# Set local hooks path to .githooks
git config core.hooksPath .githooks

# Ensure executable
chmod +x .githooks/commit-msg || true

echo "Local git hooks installed (core.hooksPath=.githooks)."
echo "The commit-msg hook will REMIND you to attach a Dev Journal (non-blocking)."
