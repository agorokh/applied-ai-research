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

FORBIDDEN = [
    (r"rs-hero-bar", "v4 removes rs-hero-bar from report heroes"),
    (r'<nav[^>]*class="[^"]*rs-series-nav', "v4 removes rs-series-nav from heroes"),
    (r"What I got wrong before this measurement", "autobiographical callout heading"),
    (r"I wrote the substrate decision below", "first-person appendix framing"),
    (r"What I required", "first-person adoption-bar table header"),
]


def check_structure(text: str, path: Path) -> list[str]:
    errors: list[str] = []
    for tag in ("html", "body", "main"):
        opens = len(re.findall(rf"<{tag}[\s>]", text))
        closes = len(re.findall(rf"</{tag}>", text))
        if opens != closes:
            errors.append(f"{path}: <{tag}> open={opens} close={closes}")
    return errors


def main() -> int:
    failures: list[str] = []
    for report in REPORTS:
        if not report.is_file():
            failures.append(f"missing report: {report}")
            continue
        text = report.read_text(encoding="utf-8")
        failures.extend(check_structure(text, report))
        for pattern, reason in FORBIDDEN:
            if re.search(pattern, text):
                failures.append(f"{report}: forbidden pattern ({reason}): /{pattern}/")
        if "rs-tier" in text and "<h3>" not in text:
            failures.append(f"{report}: rs-tier blocks without h3 titles")
    if failures:
        print("validate_reports: FAIL", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("validate_reports: OK (2 reports)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
