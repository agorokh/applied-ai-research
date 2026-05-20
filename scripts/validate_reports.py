#!/usr/bin/env python3
"""Local CI-equivalent checks for Applied AI Research HTML reports."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = [
    ROOT / "2026-05-15_claude-code-via-dial-poc/index.html",
    ROOT / "2026-05-19_choosing-memory-for-enterprise-agents/index.html",
]

MIN_TIER_CARDS: dict[str, int] = {
    "2026-05-15_claude-code-via-dial-poc/index.html": 3,
    "2026-05-19_choosing-memory-for-enterprise-agents/index.html": 2,
}

FORBIDDEN = [
    (r"rs-hero-bar", "v4 removes rs-hero-bar from report heroes"),
    (r'<nav[^>]*class="[^"]*rs-series-nav', "v4 removes rs-series-nav from heroes"),
    (r"What I got wrong before this measurement", "autobiographical callout heading"),
    (r"I wrote the substrate decision below", "first-person appendix framing"),
    (r"What I required", "first-person adoption-bar table header"),
]

TIER_OPEN = re.compile(
    r'<div\b(?=[^>]*\bclass=["\'][^"\']*\brs-tier\b)',
    re.IGNORECASE,
)
DIV_OPEN = re.compile(r"<div\b", re.IGNORECASE)
DIV_CLOSE = re.compile(r"</div\s*>", re.IGNORECASE)


def extract_rs_tier_blocks(html: str) -> list[str]:
    """Return inner HTML of each top-level .rs-tier card (nesting-aware)."""
    blocks: list[str] = []
    for opener in TIER_OPEN.finditer(html):
        start = opener.end()
        depth = 1
        pos = start
        while pos < len(html) and depth > 0:
            next_open = DIV_OPEN.search(html, pos)
            next_close = DIV_CLOSE.search(html, pos)
            if next_close is None:
                break
            if next_open is not None and next_open.start() < next_close.start():
                depth += 1
                pos = next_open.end()
            else:
                depth -= 1
                end = next_close.end()
                if depth == 0:
                    blocks.append(html[start:next_close.start()])
                    pos = end
                    break
                pos = end
    return blocks


def check_structure(text: str, path: Path) -> list[str]:
    errors: list[str] = []
    lower = text.lower()
    for tag in ("html", "body", "main"):
        opens = len(re.findall(rf"<{tag}\b", lower))
        closes = len(re.findall(rf"</{tag}\s*>", lower))
        if opens != closes:
            errors.append(f"{path}: <{tag}> open={opens} close={closes}")
        if opens != 1 or closes != 1:
            errors.append(f"{path}: expected exactly one <{tag}> wrapper, got open={opens} close={closes}")

    open_pos = {t: lower.find(f"<{t}") for t in ("html", "body", "main")}
    close_pos = {t: lower.rfind(f"</{t}>") for t in ("html", "body", "main")}
    if all(v != -1 for v in open_pos.values()):
        if not (open_pos["html"] < open_pos["body"] < open_pos["main"]):
            errors.append(f"{path}: invalid opening order (expected html < body < main)")
    if all(v != -1 for v in close_pos.values()):
        if not (close_pos["main"] < close_pos["body"] < close_pos["html"]):
            errors.append(f"{path}: invalid closing order (expected </main> < </body> < </html>)")

    return errors


def check_tier_headings(text: str, path: Path) -> list[str]:
    errors: list[str] = []
    blocks = extract_rs_tier_blocks(text)
    key = str(path.relative_to(ROOT))
    min_expected = MIN_TIER_CARDS.get(key, 1)
    if len(blocks) < min_expected:
        errors.append(
            f"{path}: expected at least {min_expected} rs-tier card(s), found {len(blocks)}"
        )
    for idx, block in enumerate(blocks, start=1):
        if not re.search(r"<h3\b", block, flags=re.IGNORECASE):
            errors.append(f"{path}: rs-tier block #{idx} missing h3 title")
    return errors


def main() -> int:
    failures: list[str] = []
    for report in REPORTS:
        if not report.is_file():
            failures.append(f"missing report: {report}")
            continue
        text = report.read_text(encoding="utf-8")
        failures.extend(check_structure(text, report))
        failures.extend(check_tier_headings(text, report))
        for pattern, reason in FORBIDDEN:
            if re.search(pattern, text):
                failures.append(f"{report}: forbidden pattern ({reason}): /{pattern}/")
    if failures:
        print("validate_reports: FAIL", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("validate_reports: OK (2 reports)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
