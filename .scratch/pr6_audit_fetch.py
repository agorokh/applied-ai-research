#!/usr/bin/env python3
"""Fetch complete PR #6 feedback inventory with pagination."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

OWNER, REPO, PR = "agorokh", "applied-ai-research", 6
OUT = Path(__file__).resolve().parent / "pr6_full_ledger.json"


def gh_json(*args: str) -> object:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    return json.loads(r.stdout)


def gh_graphql(query: str) -> dict:
    r = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    return json.loads(r.stdout)


def strip_html(s: str) -> str:
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.DOTALL)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fetch_threads() -> list[dict]:
    threads: list[dict] = []
    cursor: str | None = None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        q = (
            "{"
            f'  repository(owner: "{OWNER}", name: "{REPO}") {{'
            f"    pullRequest(number: {PR}) {{"
            f"      reviewThreads(first: 100{after}) {{"
            "        pageInfo { hasNextPage endCursor }"
            "        nodes {"
            "          id isResolved path line"
            "          comments(first: 50) {"
            "            nodes {"
            "              id databaseId createdAt"
            "              author { login }"
            "              body"
            "            }"
            "          }"
            "        }"
            "      }"
            "    }"
            "  }"
            "}"
        )
        data = gh_graphql(q)
        conn = data["data"]["repository"]["pullRequest"]["reviewThreads"]
        threads.extend(conn["nodes"])
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    return threads


def fetch_paginated(path: str) -> list[dict]:
    r = subprocess.run(
        ["gh", "api", "--paginate", path],
        capture_output=True,
        text=True,
        check=True,
    )
    # --paginate may emit multiple JSON arrays concatenated
    raw = r.stdout.strip()
    if not raw:
        return []
    if raw.startswith("["):
        # single array or newline-separated arrays
        items: list[dict] = []
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(raw):
            while idx < len(raw) and raw[idx] in " \n\r\t":
                idx += 1
            if idx >= len(raw):
                break
            obj, end = decoder.raw_decode(raw, idx)
            idx = end
            if isinstance(obj, list):
                items.extend(obj)
            elif isinstance(obj, dict):
                items.append(obj)
        return items
    return json.loads(raw)


def is_actionable_thread(body: str, author: str, resolved: bool) -> str:
    if resolved:
        return "RESOLVED"
    b = body.lower()
    if re.match(r"^(lgtm!?|looks good)", b):
        return "RESOLVED-LGTM"
    if "no action needed" in b[:120]:
        return "RESOLVED-LGTM"
    if author == "agorokh" and ("audit complete" in b or "ledger" in b):
        return "RESOLVED-AGOROKH-AUDIT"
    return "UNRESOLVED"


def main() -> None:
    watermark = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    threads = fetch_threads()
    issue_comments = fetch_paginated(f"repos/{OWNER}/{REPO}/issues/{PR}/comments")
    review_comments = fetch_paginated(f"repos/{OWNER}/{REPO}/pulls/{PR}/comments")
    reviews = fetch_paginated(f"repos/{OWNER}/{REPO}/pulls/{PR}/reviews")

    ledger: list[dict] = []

    for i, t in enumerate(threads, 1):
        nodes = t["comments"]["nodes"]
        if not nodes:
            continue
        c = nodes[0]
        author = (c.get("author") or {}).get("login", "?")
        body = strip_html(c.get("body") or "")
        status = is_actionable_thread(body, author, t["isResolved"])
        ledger.append(
            {
                "kind": "thread",
                "seq": i,
                "id": t["id"],
                "path": t.get("path"),
                "line": t.get("line"),
                "author": author,
                "status": status,
                "resolved_github": t["isResolved"],
                "body": body[:800],
                "url": (
                    f"https://github.com/{OWNER}/{REPO}/pull/{PR}#discussion_r{c['databaseId']}"
                    if c.get("databaseId")
                    else None
                ),
                "reply_count": len(nodes) - 1,
            }
        )

    for i, c in enumerate(issue_comments, 1):
        author = c["user"]["login"]
        body = strip_html(c.get("body") or "")
        status = "INFO"
        if author == "agorokh":
            if re.search(r"\b0\s+UNRESOLVED\b", body, re.I) or re.search(
                r"RESOLVED.*0\s+inline", body, re.I
            ):
                status = "RESOLVED-AGOROKH-AUDIT"
            elif "zero-sampling audit" in body.lower() or "exit audit" in body.lower():
                status = "RESOLVED-AGOROKH-AUDIT"
            elif "audit complete" in body.lower() or "ledger" in body.lower():
                status = "RESOLVED-AGOROKH-AUDIT"
        ledger.append(
            {
                "kind": "issue_comment",
                "seq": i,
                "id": c["id"],
                "author": author,
                "created_at": c["created_at"],
                "status": status,
                "body": body[:800],
                "url": c["html_url"],
            }
        )

    for i, c in enumerate(review_comments, 1):
        author = c["user"]["login"]
        body = strip_html(c.get("body") or "")
        ledger.append(
            {
                "kind": "review_comment",
                "seq": i,
                "id": c["id"],
                "path": c.get("path"),
                "line": c.get("line"),
                "author": author,
                "body": body[:400],
                "url": c["html_url"],
            }
        )

    for i, r in enumerate(reviews, 1):
        author = r["user"]["login"]
        body = strip_html(r.get("body") or "")
        actionable = "**Actionable comments posted:" in (r.get("body") or "")
        ledger.append(
            {
                "kind": "review",
                "seq": i,
                "id": r["id"],
                "author": author,
                "state": r["state"],
                "commit_id": r.get("commit_id"),
                "actionable_flag": actionable,
                "body": body[:600],
            }
        )

    unresolved = [x for x in ledger if x.get("status", "").startswith("UNRESOLVED")]

    out = {
        "watermark_sha": watermark,
        "counts": {
            "threads": len([x for x in ledger if x["kind"] == "thread"]),
            "threads_unresolved": len(unresolved),
            "issue_comments": len(issue_comments),
            "review_comments": len(review_comments),
            "reviews": len(reviews),
            "ledger_total": len(ledger),
        },
        "unresolved": unresolved,
        "ledger": ledger,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out["counts"], indent=2))
    print(f"written: {OUT}")
    for u in unresolved:
        print(f"UNRESOLVED: {u['kind']} {u.get('path')}:{u.get('line')} @{u.get('author')} — {u.get('body','')[:120]}")


if __name__ == "__main__":
    main()
