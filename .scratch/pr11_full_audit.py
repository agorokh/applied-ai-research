#!/usr/bin/env python3
"""Fetch complete PR #11 comment inventory (zero sampling)."""
import json
import re
import subprocess
from datetime import datetime, timezone

OWNER = "agorokh"
REPO = "applied-ai-research"
PR = 11
WATERMARK = "10e758a3b1fc4fa81da35f936700edefa4800686"


def gh_graphql(query: str, variables: dict) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        if isinstance(v, int):
            cmd += ["-F", f"{k}={v}"]
        else:
            cmd += ["-f", f"{k}={v}"]
    return json.loads(subprocess.check_output(cmd, text=True))


def paginate_threads() -> list:
    nodes = []
    cursor = None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        q = f"""
        query($owner:String!,$repo:String!,$number:Int!) {{
          repository(owner:$owner,name:$repo) {{
            pullRequest(number:$number) {{
              reviewThreads(first:100{after}) {{
                pageInfo {{ hasNextPage endCursor }}
                nodes {{
                  id
                  isResolved
                  path
                  line
                  comments(first:50) {{
                    nodes {{
                      id
                      databaseId
                      url
                      author {{ login }}
                      body
                      createdAt
                      updatedAt
                      commit {{ oid }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}"""
        data = gh_graphql(q, {"owner": OWNER, "repo": REPO, "number": PR})
        block = data["data"]["repository"]["pullRequest"]["reviewThreads"]
        nodes.extend(block["nodes"])
        if not block["pageInfo"]["hasNextPage"]:
            break
        cursor = block["pageInfo"]["endCursor"]
    return nodes


def paginate_reviews() -> list:
    nodes = []
    cursor = None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        q = f"""
        query($owner:String!,$repo:String!,$number:Int!) {{
          repository(owner:$owner,name:$repo) {{
            pullRequest(number:$number) {{
              reviews(first:100{after}) {{
                pageInfo {{ hasNextPage endCursor }}
                nodes {{
                  id
                  databaseId
                  author {{ login }}
                  body
                  state
                  submittedAt
                  commit {{ oid }}
                }}
              }}
            }}
          }}
        }}"""
        data = gh_graphql(q, {"owner": OWNER, "repo": REPO, "number": PR})
        block = data["data"]["repository"]["pullRequest"]["reviews"]
        nodes.extend(block["nodes"])
        if not block["pageInfo"]["hasNextPage"]:
            break
        cursor = block["pageInfo"]["endCursor"]
    return nodes


def paginate_issue_comments() -> list:
    out = subprocess.check_output(
        [
            "gh",
            "api",
            f"/repos/{OWNER}/{REPO}/issues/{PR}/comments",
            "--paginate",
            "--slurp",
        ],
        text=True,
    )
    pages = json.loads(out)
    comments = []
    for page in pages:
        if isinstance(page, list):
            comments.extend(page)
        elif isinstance(page, dict):
            comments.append(page)
    return comments


def wm_time() -> datetime:
    out = subprocess.check_output(
        ["gh", "api", f"/repos/{OWNER}/{REPO}/commits/{WATERMARK}", "-q", ".commit.committer.date"],
        text=True,
    ).strip()
    return datetime.fromisoformat(out.replace("Z", "+00:00"))


def parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def main() -> None:
    threads = paginate_threads()
    reviews = paginate_reviews()
    issue_comments = paginate_issue_comments()
    wm_dt = wm_time()

    ledger = []
    seq = 0

    for t in threads:
        for c in t["comments"]["nodes"]:
            seq += 1
            updated = parse_ts(c.get("updatedAt"))
            after_wm = updated is not None and updated > wm_dt
            actionable = needs_action(c["body"], c["author"]["login"] if c["author"] else "")
            status = "RESOLVED" if t["isResolved"] else ("UNRESOLVED" if actionable else "RESOLVED")
            ledger.append(
                {
                    "seq": seq,
                    "kind": "inline_thread",
                    "id": c["id"],
                    "thread_id": t["id"],
                    "url": c["url"],
                    "author": (c["author"] or {}).get("login", "ghost"),
                    "path": t.get("path"),
                    "line": t.get("line"),
                    "thread_resolved": t["isResolved"],
                    "commit_oid": (c.get("commit") or {}).get("oid"),
                    "updatedAt": c.get("updatedAt"),
                    "after_watermark": after_wm,
                    "status": status,
                    "actionable": actionable,
                    "body": c["body"] or "",
                }
            )

    for r in reviews:
        if not (r.get("body") or "").strip():
            continue
        seq += 1
        author = (r["author"] or {}).get("login", "ghost")
        actionable = needs_action(r["body"], author)
        status = "UNRESOLVED" if actionable else "RESOLVED"
        ledger.append(
            {
                "seq": seq,
                "kind": "review_summary",
                "id": r["id"],
                "author": author,
                "state": r.get("state"),
                "commit_oid": (r.get("commit") or {}).get("oid"),
                "submittedAt": r.get("submittedAt"),
                "after_watermark": False,
                "status": status,
                "actionable": actionable,
                "body": r["body"] or "",
            }
        )

    for c in issue_comments:
        seq += 1
        author = c["user"]["login"]
        updated = parse_ts(c.get("updated_at"))
        after_wm = updated is not None and updated > wm_dt
        actionable = needs_action(c["body"], author)
        status = "UNRESOLVED" if actionable else "RESOLVED"
        ledger.append(
            {
                "seq": seq,
                "kind": "issue_comment",
                "id": c["id"],
                "url": c["html_url"],
                "author": author,
                "updated_at": c.get("updated_at"),
                "after_watermark": after_wm,
                "status": status,
                "actionable": actionable,
                "body": c["body"] or "",
            }
        )

    unresolved = [x for x in ledger if x["status"] == "UNRESOLVED"]
    after_wm_items = [x for x in ledger if x.get("after_watermark")]

    out = {
        "watermark": WATERMARK,
        "watermark_commit_date": wm_dt.isoformat(),
        "inventory_counts": {
            "review_threads": len(threads),
            "inline_comments": sum(len(t["comments"]["nodes"]) for t in threads),
            "reviews": len(reviews),
            "issue_comments": len(issue_comments),
            "ledger_entries": len(ledger),
        },
        "summary": {
            "resolved": sum(1 for x in ledger if x["status"] == "RESOLVED"),
            "unresolved": len(unresolved),
            "after_watermark_count": len(after_wm_items),
        },
        "unresolved": unresolved,
        "after_watermark": after_wm_items,
        "ledger": ledger,
    }

    path = "/Users/arseny_gorokh/Projects/applied-ai-research/.scratch/pr11_comment_ledger.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"path": path, **out["inventory_counts"], **out["summary"]}, indent=2))


def needs_action(body: str, author: str) -> bool:
    """Heuristic: bot/agorokh feedback requiring code changes."""
    if author == "agorokh":
        # user comments - check for explicit requests
        lower = body.lower()
        if any(
            w in lower
            for w in [
                "please fix",
                "must fix",
                "change request",
                "needs to",
                "should fix",
                "address this",
                "resolve",
            ]
        ):
            return True
        return False
    bot_authors = {
        "sourcery-ai",
        "coderabbitai",
        "copilot-pull-request-reviewer",
        "cursor",
        "bugbot",
        "github-actions",
    }
    if author.lower() in bot_authors or "bot" in author.lower():
        lower = body.lower()
        # skip pure LGTM / informational
        if "lgtm" in lower and len(body) < 200:
            return False
        if "no actionable comments" in lower or "no issues found" in lower:
            return False
        if "rate limit" in lower or "quota limit" in lower:
            return False
        # sourcery high-level suggestions
        if "consider scoping" in lower or "ensure any references" in lower:
            return True
        if "⚠️" in body or "critical" in lower or "bug" in lower:
            return True
        if "please address" in lower or "suggestion" in lower:
            return True
        if "<!--" in body and "review" in lower:
            # long bot templates - parse for actionable
            if "consider scoping" in lower or "ensure any references" in lower:
                return True
    return False


if __name__ == "__main__":
    main()
