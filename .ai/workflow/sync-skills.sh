#!/usr/bin/env bash
# Mirrors this repo's skills/ into <project-root>/.agents/skills/, for
# harnesses that auto-discover skills there instead of (or in addition
# to) following workflow.md's explicit skill lookup table.
#
# Adds any skill not already present; overwrites any that already
# exist with the current version. Does NOT remove skills that were
# deleted upstream — check manually after a workflow update if that
# matters to you.
#
# Usage:
#   ./sync-skills.sh                  # assumes standard .ai/workflow/ mount
#   ./sync-skills.sh /path/to/.agents/skills   # explicit destination

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"

if [ ! -d "$SKILLS_SRC" ]; then
  echo "Error: no skills/ found at $SKILLS_SRC" >&2
  exit 1
fi

if [ "${1:-}" != "" ]; then
  SKILLS_DEST="$1"
else
  # Standard mount point is .ai/workflow/ — project root is two levels up.
  PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
  SKILLS_DEST="$PROJECT_ROOT/.agents/skills"
  echo "No destination given — assuming standard mount point."
  echo "Project root resolved to: $PROJECT_ROOT"
fi

mkdir -p "$SKILLS_DEST"

added=0
updated=0
for skill_dir in "$SKILLS_SRC"/*/; do
  skill_name="$(basename "$skill_dir")"
  dest="$SKILLS_DEST/$skill_name"
  if [ -d "$dest" ]; then
    echo "  updating  $skill_name"
    updated=$((updated + 1))
  else
    echo "  adding    $skill_name"
    added=$((added + 1))
  fi
  rm -rf "$dest"
  cp -r "$skill_dir" "$dest"
done

echo ""
echo "Done: $added added, $updated updated. Synced to $SKILLS_DEST"
echo "Remember to re-run this after every 'git submodule update' —"
echo "these are copies, not links, and will silently go stale otherwise."
