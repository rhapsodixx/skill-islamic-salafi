#!/bin/sh
# Build the ChatGPT Project bundle (instructions.md + knowledge.md) from the skill.
# Usage: scripts/build-chatgpt.sh [OUT_DIR]   (default: <repo>/chatgpt)
set -eu
export LC_ALL=C
ROOT=$(cd "$(dirname "$0")/.." && pwd)
SKILL="$ROOT/skills/islamic-salafi"
OUT=${1:-$ROOT/chatgpt}
[ -f "$SKILL/SKILL.md" ] || { echo "build-chatgpt: missing $SKILL/SKILL.md" >&2; exit 1; }
set -- "$SKILL"/references/*.md
[ -f "$1" ] || { echo "build-chatgpt: no .md files in $SKILL/references" >&2; exit 1; }
mkdir -p "$OUT"

# Drop trailing blank lines so output ends with exactly one newline.
trim() {
  awk '/^$/ { b++; next } { while (b > 0) { print ""; b-- } print }'
}

NOTE='Reference material (aqeedah, fiqh, muamalah, tazkiyah, sources, examples) is in the uploaded file knowledge.md. Where these instructions say "read references/<file>.md", look up the section with that file name in knowledge.md.'

{
  tr -d '\r' < "$SKILL/SKILL.md" | awk '
    NR == 1 && $0 == "---" { fm = 1; next }
    fm && $0 == "---" { fm = 0; next }
    !fm { print }'
  printf '\n%s\n' "$NOTE"
} | trim > "$OUT/instructions.md"

for f in "$@"; do
  printf '# references/%s\n\n' "$(basename "$f")"
  tr -d '\r' < "$f"
  printf '\n'
done | trim > "$OUT/knowledge.md"
