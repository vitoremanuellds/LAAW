#!/usr/bin/env bash
# Installs or re-syncs this repo's workflow content (workflow.md,
# skills/, templates/, reference/, README.md) into a target project's
# .ai/workflow/ — the copy-based replacement for `git submodule add`/
# `git submodule update --remote` (see adr01-plain-copy-bootstrap.md in
# the LAAW-Workspace repo).
#
# First run against a target with no .ai/workflow/ yet: fresh install.
# Any later run against the same target: re-sync — .ai/workflow/'s
# content is wholesale-replaced with the source's current state. There
# is no partial-merge logic: .ai/workflow/ is never supposed to be
# hand-edited (workflow.md §3), so there is nothing local to preserve.
#
# Every run also (re)writes a version-stamp file, .ai/workflow-version,
# as a SIBLING of .ai/workflow/ (never inside it, so .ai/workflow/
# stays a byte-for-byte mirror of the source) — see
# adr04-workflow-version-stamp.md for the format and why it lives
# there.
#
# Usage:
#   ./sync-workflow.sh                              # source = this script's own checkout, target = current directory
#   ./sync-workflow.sh /path/to/LAAW-checkout        # explicit source, target = current directory
#   ./sync-workflow.sh /path/to/LAAW-checkout /path/to/your-project   # explicit source and target

set -euo pipefail

if [ "${1:-}" != "" ]; then
  SOURCE_DIR="$1"
else
  SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [ "${2:-}" != "" ]; then
  TARGET_ROOT="$2"
else
  TARGET_ROOT="$(pwd)"
fi

if [ ! -f "$SOURCE_DIR/workflow.md" ]; then
  echo "Error: $SOURCE_DIR doesn't look like a LAAW checkout (no workflow.md found there)." >&2
  exit 1
fi

DEST="$TARGET_ROOT/.ai/workflow"
STAMP="$TARGET_ROOT/.ai/workflow-version"

WAS_EXISTING=0
if [ -d "$DEST" ]; then
  WAS_EXISTING=1
  rm -rf "$DEST"
fi

mkdir -p "$DEST"
cp -r "$SOURCE_DIR/workflow.md" "$SOURCE_DIR/skills" "$SOURCE_DIR/templates" "$SOURCE_DIR/reference" "$SOURCE_DIR/README.md" "$DEST/"

if SHA="$(git -C "$SOURCE_DIR" rev-parse HEAD 2>/dev/null)"; then
  :
else
  SHA="unknown"
  echo "Warning: $SOURCE_DIR isn't a git checkout — recording commit as \"unknown\"." >&2
fi

if SOURCE_LABEL="$(git -C "$SOURCE_DIR" remote get-url origin 2>/dev/null)"; then
  :
else
  SOURCE_LABEL="$SOURCE_DIR"
fi

mkdir -p "$(dirname "$STAMP")"
{
  echo "source=$SOURCE_LABEL"
  echo "commit=$SHA"
  echo "date=$(date -u +%Y-%m-%d)"
} > "$STAMP"

if [ "$WAS_EXISTING" -eq 1 ]; then
  echo "Re-synced .ai/workflow/ at $TARGET_ROOT"
else
  echo "Installed .ai/workflow/ at $TARGET_ROOT"
fi
echo "Stamped commit: $SHA"
