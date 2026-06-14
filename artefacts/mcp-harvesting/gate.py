#!/usr/bin/env python3
"""
provenance-atom v0.1: a minimal, dependency-free validator and the DETERMINISTIC
structural grounding gate described in the article (section 6, section 10).

Two things, both with no model in the loop:

  validate_atom(atom)            -> (ok, errors)   schema-shape check
  structural_gate(atom, source)  -> (verdict, why) the deterministic half of the gate:
                                                    a quote that does not appear in the
                                                    cited source is a fabricated citation
                                                    and is rejected outright.

The SEMANTIC half of the gate (does the source actually *support* the claim, beyond the
quote merely appearing) needs an entailment/reasoning model. That half, and the evidence
that it beats a similarity gate, is in run_eval.py. The point of splitting them is the
article's point: the cheap deterministic check catches fabricated and missing quotes for
free, before any model is paid, and the model only judges what survives.

CLI:  python3 gate.py            # runs the built-in self-test
"""
import json, re, unicodedata, pathlib, sys

HERE = pathlib.Path(__file__).parent
SCHEMA = json.loads((HERE / "provenance_atom.schema.json").read_text())

_KINDS = set(SCHEMA["properties"]["kind"]["enum"])
_STRENGTHS = set(SCHEMA["properties"]["evidence_strength"]["enum"])
_VERDICTS = set(SCHEMA["properties"]["gate_verdict"]["enum"])


def validate_atom(atom):
    """Minimal shape check against provenance-atom v0.1. Returns (ok, [errors])."""
    errs = []
    if not isinstance(atom, dict):
        return False, ["atom is not an object"]
    for req in ("kind", "claim", "evidence_strength", "locator"):
        if req not in atom:
            errs.append(f"missing required field: {req}")
    if "kind" in atom and atom["kind"] not in _KINDS:
        errs.append(f"kind not in enum: {atom['kind']}")
    if "evidence_strength" in atom and atom["evidence_strength"] not in _STRENGTHS:
        errs.append(f"evidence_strength not in enum: {atom['evidence_strength']}")
    if atom.get("claim", "") == "":
        errs.append("claim is empty")
    if "gate_verdict" in atom and atom["gate_verdict"] not in _VERDICTS:
        errs.append(f"gate_verdict not in enum: {atom['gate_verdict']}")
    loc = atom.get("locator")
    if isinstance(loc, dict):
        for req in ("source", "sha256", "quote"):
            if not loc.get(req):
                errs.append(f"locator.{req} missing or empty")
        sha = loc.get("sha256", "")
        if sha and not re.fullmatch(r"[a-f0-9]{6,64}", sha):
            errs.append(f"locator.sha256 not a hex hash: {sha}")
    elif loc is not None:
        errs.append("locator is not an object")
    return (len(errs) == 0), errs


def _norm(s):
    """Lowercase, strip accents, collapse whitespace and most punctuation for a forgiving
    but still verbatim-ish quote match. The gate must tolerate a connector re-encoding
    smart quotes, not tolerate a fabricated quote."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[‘’“”]", "'", s)
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def structural_gate(atom, source_text):
    """Deterministic half of the grounding gate. No model.
    Rejects atoms whose quote is missing or does not appear in the cited source.
    Returns (verdict, reason) where verdict is 'unsupported' (hard reject) or
    'needs_semantic_check' (the quote is real; hand it to the entailment gate)."""
    ok, errs = validate_atom(atom)
    if not ok:
        return "unsupported", "invalid atom: " + "; ".join(errs)
    quote = atom["locator"]["quote"]
    if _norm(quote) and _norm(quote) in _norm(source_text):
        return "needs_semantic_check", "quote present in source; entailment check required"
    return "unsupported", "fabricated or absent citation: quote not found verbatim in source"


def _selftest():
    src = ('The data centre in Dublin reached 92 percent rack utilisation in the fourth quarter. '
           'The vendor completed a SOC 2 Type II report in March 2025.')
    good = {
        "kind": "money_figure", "claim": "Dublin rack utilisation was 92 percent in Q4.",
        "evidence_strength": "stated",
        "locator": {"source": "review.pptx", "sha256": "9f2c8a", "where": "slide 4",
                    "quote": "92 percent rack utilisation in the fourth quarter"},
        "open_questions": [], "red_flags": [],
    }
    fabricated = json.loads(json.dumps(good))
    fabricated["locator"]["quote"] = "98 percent rack utilisation in the first quarter"
    malformed = {"claim": "x", "locator": {"source": "a", "sha256": "zzz", "quote": "q"}}

    cases = [("supported quote", good, src, "needs_semantic_check"),
             ("fabricated quote", fabricated, src, "unsupported"),
             ("malformed atom", malformed, src, "unsupported")]
    allok = True
    for name, atom, source, expect in cases:
        verdict, why = structural_gate(atom, source)
        ok = verdict == expect
        allok &= ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: -> {verdict}  ({why})")
    print("self-test:", "OK" if allok else "FAILED")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(_selftest())
