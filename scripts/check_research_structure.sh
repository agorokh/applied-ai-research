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

check_zero() {
  local label="$1" pattern="$2" file="$3"
  local count
  count=$(grep -c "$pattern" "$file" 2>/dev/null) || count=0
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
  sections=$(grep -c '^<section ' "$report")
  callouts=$(grep -c 'class="rs-callout' "$report")
  h1=$(grep -c '<h1>' "$report")
  h3=$(grep -c '<h3>' "$report")
  ems_in_h1=$(grep -oE '<h1>[^<]*<em>' "$report" | wc -l | awk '{print $1}')

  check_count "sections" "$sections" 13 13 "$report"
  check_count "callouts" "$callouts" 3 5 "$report"
  check_count "h1"       "$h1"       1 1  "$report"
  check_count "em in h1" "$ems_in_h1" 1 1 "$report"
  check_count "h3"       "$h3"       0 8  "$report"
  check_zero  "rs-container divs" 'class="rs-container"' "$report"
  check_zero  "inline <style>"    '<style>'              "$report"
  check_zero  "research-overrides link" 'research-overrides' "$report"
done

if [[ -f "$LANDING" ]]; then
  echo "=== landing ==="
  hero=$(grep -c 'class="rs-index-hero"' "$LANDING")
  posts=$(grep -c 'class="rs-post"' "$LANDING")
  h1=$(grep -c '<h1>' "$LANDING")
  check_count "rs-index-hero" "$hero" 1 1 "$LANDING"
  check_count "rs-post articles" "$posts" "${#REPORTS[@]}" 9999 "$LANDING"
  check_count "h1"            "$h1"  1 1 "$LANDING"
  check_zero  "inline <style>" '<style>' "$LANDING"
  check_zero  "research-overrides link" 'research-overrides' "$LANDING"
fi

if [[ $fail -gt 0 ]]; then
  echo
  echo "check_research_structure: FAIL ($fail violations)" >&2
  exit 1
fi
echo
echo "check_research_structure: OK"
