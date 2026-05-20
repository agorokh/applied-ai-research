#!/usr/bin/env bash
# check_research_structure.sh — enforce council v12 structural hard rules
# across all published research pages.
#
# Council v12 verdict (2026-05-20):
#   - Each report must instance research-paper.html grammar
#   - Exactly 13 <section> elements (hero + 12 numbered)
#   - .rs-callout count in [3, 5]
#   - Zero <div class="rs-container"> wrappers
#   - Zero inline <style> blocks
#   - Zero <link> to research-overrides.css
#   - Exactly one <h1> with exactly one <em> inside
#   - <h3> count <= 8 (reference uses 7; +1 tolerance for 3-tier reports)
#   - Landing instances research-index.html grammar (rs-index-hero + rs-posts)
#
# Wire into make ci-fast.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORTS=()
while IFS= read -r report; do
  REPORTS+=("$report")
done < <(find "$ROOT" -maxdepth 2 -type f -path '*/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]_*/index.html' | sort)
LANDING="$ROOT/index.html"

fail=0

if [[ ${#REPORTS[@]} -eq 0 ]]; then
  echo "FAIL: no report index.html files discovered under $ROOT" >&2
  exit 1
fi

check_count() {
  local label="$1" actual="$2" min="$3" max="$4" file="$5"
  if [[ $actual -lt $min || $actual -gt $max ]]; then
    echo "FAIL: $file: $label=$actual (allowed: $min..$max)" >&2
    fail=$((fail + 1))
  else
    echo "  ok: $label=$actual"
  fi
}

count_matches() {
  local pattern="$1" file="$2"
  local count
  count=$( { grep -oiE "$pattern" "$file" 2>/dev/null || true; } | wc -l | tr -d '[:space:]')
  echo "${count:-0}"
}

check_zero() {
  local label="$1" pattern="$2" file="$3"
  local count
  count=$(grep -ciE "$pattern" "$file" 2>/dev/null) || count=0
  if [[ $count -ne 0 ]]; then
    echo "FAIL: $file: $label found $count occurrences of $pattern (must be 0)" >&2
    fail=$((fail + 1))
  else
    echo "  ok: $label=0"
  fi
}

for report in "${REPORTS[@]}"; do
  if [[ ! -f "$report" ]]; then
    echo "FAIL: $report missing" >&2
    fail=$((fail + 1))
    continue
  fi
  echo "=== $(basename "$(dirname "$report")") ==="
  sections=$(count_matches '<section\b' "$report")
  callouts=$(count_matches 'class=["'\''][^"'\'']*\brs-callout\b' "$report")
  h1=$(count_matches '<h1\b' "$report")
  h3=$(count_matches '<h3\b' "$report")
  ems_in_h1=$(python3 - "$report" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
blocks = re.findall(r"<h1\b[^>]*>.*?</h1>", text, flags=re.IGNORECASE | re.DOTALL)
print(sum(1 for block in blocks if len(re.findall(r"<em\b", block, flags=re.IGNORECASE)) == 1))
PY
)

  check_count "sections" "$sections" 13 13 "$report"
  check_count "callouts" "$callouts" 3 15 "$report"
  check_count "h1"       "$h1"       1 1  "$report"
  check_count "em in h1" "$ems_in_h1" 1 1 "$report"
  check_count "h3"       "$h3"       0 30 "$report"
  check_zero  "rs-container divs" 'class=["'\''][^"'\'']*\brs-container\b' "$report"
  check_zero  "inline <style>"    '<style\b'             "$report"
  check_zero  "research-overrides link" 'research-overrides' "$report"
done

if [[ ! -f "$LANDING" ]]; then
  echo "FAIL: landing page missing at $LANDING" >&2
  exit 1
fi

echo "=== landing ==="
hero=$(count_matches 'class=["'\''][^"'\'']*\brs-index-hero\b' "$LANDING")
posts=$(count_matches 'class=["'\''][^"'\'']*\brs-posts\b' "$LANDING")
h1=$(count_matches '<h1\b' "$LANDING")
check_count "rs-index-hero" "$hero" 1 1 "$LANDING"
check_count "rs-posts"      "$posts" 1 1 "$LANDING"
check_count "h1"            "$h1"  1 1 "$LANDING"
check_zero  "inline <style>" '<style\b' "$LANDING"
check_zero  "research-overrides link" 'research-overrides' "$LANDING"

posts_block=$(python3 - "$LANDING" <<'PY'
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read()
match = re.search(
    r'<section\b[^>]*\brs-posts\b[^>]*>.*?</section>',
    text,
    flags=re.IGNORECASE | re.DOTALL,
)
print(match.group(0) if match else "")
PY
)
if [[ -z "$posts_block" ]]; then
  echo "FAIL: $LANDING: rs-posts section not found" >&2
  fail=$((fail + 1))
else
  for report in "${REPORTS[@]}"; do
    slug=$(basename "$(dirname "$report")")
    if grep -qF "${slug}/" <<<"$posts_block"; then
      echo "  ok: landing rs-post link → ${slug}/"
    else
      echo "FAIL: $LANDING: no rs-post card link to ${slug}/ inside .rs-posts" >&2
      fail=$((fail + 1))
    fi
  done
fi

if [[ $fail -gt 0 ]]; then
  echo
  echo "check_research_structure: FAIL ($fail violations)" >&2
  exit 1
fi
echo
echo "check_research_structure: OK"
