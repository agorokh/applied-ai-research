#!/usr/bin/env python3
"""
Gate-ablation experiment for the MCP-harvesting article (section 7).

Question: when a grounding gate must decide whether a cited SOURCE passage supports
a CLAIM, does an LLM entailment/reasoning gate catch unsupported claims better than a
similarity gate (lexical or neural embedding), and at what false-refuse cost?

Four gates over the same labelled set (dataset.jsonl):
  - lexical      : TF-IDF cosine of claim vs passage, threshold-swept       (stdlib only)
  - embedding    : neural-embedding cosine (Fireworks nomic-embed-text), swept
  - llm_entail   : an LLM gives a strict NLI label; accept iff ENTAILMENT
  - llm_reason   : an LLM reasons then outputs SUPPORTED / NOT_SUPPORTED

Decision convention: a gate ACCEPTS a claim it judges supported and REJECTS otherwise.
Ground truth: label 'supported' should be accepted; 'unsupported' and 'contradicted'
should be rejected.
  catch_rate        = P(reject | not supported)   -- the unsupported claims it stops
  false_refuse_rate = P(reject | supported)        -- the good claims it wrongly stops

Similarity gates are reported as a full catch/false-refuse frontier (every threshold),
plus the operating point matched to the LLM gate's false-refuse rate, which is the only
fair single-number comparison.

Run:  doppler run --project YOUR_PROJECT --config YOUR_CONFIG -- python3 run_eval.py
Re-runs are free: all embedding and LLM responses are cached under .cache/.
Outputs: results.json, results.md, predictions.jsonl
"""
import os, sys, json, math, re, hashlib, time, pathlib, random

HERE = pathlib.Path(__file__).parent
CACHE = HERE / ".cache"; CACHE.mkdir(exist_ok=True)
random.seed(20260613)

import httpx

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
FIREWORKS_KEY = os.environ.get("FIREWORKS_API_KEY")
LLM_MODEL = os.environ.get("EVAL_LLM_MODEL", "anthropic/claude-3.5-haiku")
LLM_MODEL_B = os.environ.get("EVAL_LLM_MODEL_B", "openai/gpt-4o-mini")  # robustness check
EMBED_MODEL = "nomic-ai/nomic-embed-text-v1.5"

STOP = set("a an the of to in on for and or is are was were be been being with as at by from "
           "its it their this that these those will would can could must may not no than then "
           "into over under about per each all any both more most".split())

# ---------- data ----------
def load_data():
    items = []
    for line in (HERE / "dataset.jsonl").read_text().splitlines():
        line = line.strip()
        if line:
            items.append(json.loads(line))
    return items

def is_supported(item):  # ground-truth "should accept"
    return item["label"] == "supported"

# ---------- lexical TF-IDF cosine ----------
def toks(s):
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP and len(t) > 1]

def tfidf_cosines(items):
    docs = []
    for it in items:
        docs.append(toks(it["passage"])); docs.append(toks(it["claim"]))
    df = {}
    for d in docs:
        for t in set(d):
            df[t] = df.get(t, 0) + 1
    N = len(docs)
    idf = {t: math.log((N + 1) / (c + 1)) + 1 for t, c in df.items()}
    def vec(tokens):
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        return {t: (c / len(tokens)) * idf.get(t, 0) for t, c in tf.items()} if tokens else {}
    def cos(a, b):
        if not a or not b: return 0.0
        dot = sum(a[t] * b.get(t, 0) for t in a)
        na = math.sqrt(sum(v * v for v in a.values())); nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0
    out = []
    for it in items:
        out.append(cos(vec(toks(it["claim"])), vec(toks(it["passage"]))))
    return out

# ---------- neural embeddings (Fireworks) ----------
def embed(text):
    h = hashlib.sha256(("emb::" + EMBED_MODEL + "::" + text).encode()).hexdigest()[:24]
    cp = CACHE / f"emb_{h}.json"
    if cp.exists():
        return json.loads(cp.read_text())
    if not FIREWORKS_KEY:
        return None
    for attempt in range(3):
        try:
            r = httpx.post("https://api.fireworks.ai/inference/v1/embeddings",
                headers={"Authorization": f"Bearer {FIREWORKS_KEY}", "Content-Type": "application/json"},
                json={"model": EMBED_MODEL, "input": [text]}, timeout=60)
            if r.status_code == 200:
                v = r.json()["data"][0]["embedding"]
                cp.write_text(json.dumps(v)); return v
            time.sleep(1.5)
        except Exception:
            time.sleep(1.5)
    raise RuntimeError("Fireworks embedding API failed after 3 retries (transport/provider error, not a no-key skip)")

def cos_dense(a, b):
    if a is None or b is None: return None
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

def embedding_cosines(items):
    out = []
    for it in items:
        ca, cb = embed(it["claim"]), embed(it["passage"])
        out.append(cos_dense(ca, cb))
    return out

# ---------- LLM gates (OpenRouter) ----------
def llm_call(model, prompt, max_tokens=120):
    h = hashlib.sha256((model + "::" + str(max_tokens) + "::" + prompt).encode()).hexdigest()[:24]
    cp = CACHE / f"llm_{h}.json"
    if cp.exists():
        return json.loads(cp.read_text())
    if not OPENROUTER_KEY:
        return {"text": "", "usage": {}}
    for attempt in range(3):
        try:
            r = httpx.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": max_tokens, "temperature": 0}, timeout=90)
            if r.status_code == 200:
                j = r.json()
                out = {"text": j["choices"][0]["message"]["content"], "usage": j.get("usage", {})}
                cp.write_text(json.dumps(out)); return out
            time.sleep(2)
        except Exception:
            time.sleep(2)
    raise RuntimeError(f"OpenRouter LLM API failed after 3 retries for model={model} (transport/provider error, not a no-key skip)")

ENTAIL_PROMPT = (
    "You check whether a SOURCE passage supports a CLAIM. Reply with exactly ONE word:\n"
    "ENTAILMENT if the source establishes the claim as true,\n"
    "CONTRADICTION if the source establishes it as false,\n"
    "NEUTRAL if the source neither establishes nor refutes it.\n\n"
    "SOURCE: {passage}\nCLAIM: {claim}\n\nOne word:"
)
REASON_PROMPT = (
    "Decide whether the SOURCE passage supports the CLAIM. A claim is SUPPORTED only if the "
    "source establishes it. A plan or intention, a recommendation, a claim attributed to someone, "
    "a different entity, a narrower or wider scope, a different quantity or date, or a direct "
    "contradiction all count as NOT_SUPPORTED.\n"
    "Reason in one or two short sentences, then end with a final line exactly: VERDICT: SUPPORTED "
    "or VERDICT: NOT_SUPPORTED.\n\nSOURCE: {passage}\nCLAIM: {claim}"
)

def llm_entail_decisions(items, model):
    dec, usage = [], []
    for it in items:
        out = llm_call(model, ENTAIL_PROMPT.format(**it), max_tokens=8)
        w = out["text"].strip().upper()
        accept = w.startswith("ENTAIL")
        dec.append(accept); usage.append(out.get("usage", {}))
    return dec, usage

def llm_reason_decisions(items, model):
    dec, usage = [], []
    for it in items:
        out = llm_call(model, REASON_PROMPT.format(**it), max_tokens=160)
        t = out["text"].upper()
        m = re.findall(r"VERDICT:\s*(SUPPORTED|NOT_SUPPORTED)", t)
        verdict = m[-1] if m else ("NOT_SUPPORTED" if "NOT_SUPPORTED" in t else ("SUPPORTED" if "SUPPORTED" in t else "NOT_SUPPORTED"))
        accept = (verdict == "SUPPORTED")
        dec.append(accept); usage.append(out.get("usage", {}))
    return dec, usage

# ---------- metrics ----------
def rates(items, accepts):
    sup = [i for i, it in enumerate(items) if is_supported(it)]
    notsup = [i for i, it in enumerate(items) if not is_supported(it)]
    # reject = not accept
    catch = sum(1 for i in notsup if not accepts[i]) / len(notsup)
    fr = sum(1 for i in sup if not accepts[i]) / len(sup)
    acc = sum(1 for i in range(len(items)) if accepts[i] == is_supported(items[i])) / len(items)
    return {"catch": catch, "false_refuse": fr, "accuracy": acc,
            "n_supported": len(sup), "n_not_supported": len(notsup)}

def per_cell_catch(items, accepts):
    cells = {}
    for i, it in enumerate(items):
        if is_supported(it): continue
        c = it["cell"]; cells.setdefault(c, [0, 0])
        cells[c][1] += 1
        if not accepts[i]: cells[c][0] += 1
    return {c: round(v[0] / v[1], 3) for c, v in sorted(cells.items())}

def sim_frontier(items, sims):
    """Sweep thresholds; reject iff sim < T. Return list of (T, catch, false_refuse, acc)."""
    valid = [s for s in sims if s is not None]
    if not valid: return []
    thr = sorted(set(round(t, 4) for t in valid)) + [max(valid) + 1e-6]
    pts = []
    for T in thr:
        accepts = [(s is not None and s >= T) for s in sims]
        r = rates(items, accepts)
        pts.append({"T": T, **r})
    return pts

def best_balanced(frontier):
    # maximise accuracy (balanced set), tie-break lower false_refuse
    return max(frontier, key=lambda p: (p["accuracy"], -p["false_refuse"]))

def catch_at_matched_fr(frontier, target_fr):
    """Highest catch achievable at false_refuse <= target_fr (the fair comparison)."""
    feasible = [p for p in frontier if p["false_refuse"] <= target_fr + 1e-9]
    if not feasible:
        return None
    return max(feasible, key=lambda p: p["catch"])

def bootstrap_ci(items, accepts, fn, n=2000):
    idx = list(range(len(items)))
    vals = []
    for _ in range(n):
        samp = [random.choice(idx) for _ in idx]
        si = [items[j] for j in samp]; sa = [accepts[j] for j in samp]
        vals.append(fn(si, sa))
    vals.sort()
    return round(vals[int(0.025 * n)], 3), round(vals[int(0.975 * n)], 3)

# ---------- main ----------
def main():
    items = load_data()
    print(f"loaded {len(items)} items; supported={sum(is_supported(i) for i in items)} "
          f"not_supported={sum(not is_supported(i) for i in items)}")
    results = {"n": len(items), "model_llm": LLM_MODEL, "model_llm_b": LLM_MODEL_B,
               "embed_model": EMBED_MODEL, "arms": {}}
    preds = [dict(id=it["id"], cell=it["cell"], label=it["label"]) for it in items]

    # similarity arms
    lex = tfidf_cosines(items)
    for i, s in enumerate(lex): preds[i]["lexical_cos"] = round(s, 4)
    emb = embedding_cosines(items)
    emb_ok = all(s is not None for s in emb)
    for i, s in enumerate(emb): preds[i]["embed_cos"] = (round(s, 4) if s is not None else None)
    print(f"embeddings available: {emb_ok}")

    # llm arms
    have_llm = bool(OPENROUTER_KEY)
    ent_dec, ent_u = llm_entail_decisions(items, LLM_MODEL) if have_llm else ([], [])
    rea_dec, rea_u = llm_reason_decisions(items, LLM_MODEL) if have_llm else ([], [])
    reb_dec, reb_u = llm_reason_decisions(items, LLM_MODEL_B) if have_llm else ([], [])
    for i in range(len(items)):
        if have_llm:
            preds[i]["llm_entail_accept"] = ent_dec[i]
            preds[i]["llm_reason_accept"] = rea_dec[i]
            preds[i]["llm_reason_b_accept"] = reb_dec[i]

    # llm metrics
    llm_arms = {}
    if have_llm:
        for name, dec in [("llm_entail", ent_dec), ("llm_reason", rea_dec), ("llm_reason_b", reb_dec)]:
            r = rates(items, dec)
            r["catch_ci"] = bootstrap_ci(items, dec, lambda si, sa: rates(si, sa)["catch"])
            r["false_refuse_ci"] = bootstrap_ci(items, dec, lambda si, sa: rates(si, sa)["false_refuse"])
            r["per_cell_catch"] = per_cell_catch(items, dec)
            llm_arms[name] = r
    results["arms"].update(llm_arms)

    # similarity metrics: frontier + best-balanced + matched-FR vs the reasoning gate
    ref_fr = llm_arms["llm_reason"]["false_refuse"] if have_llm else 0.0
    for name, sims in [("lexical", lex), ("embedding", emb)]:
        fr_pts = sim_frontier(items, sims)
        if not fr_pts:
            results["arms"][name] = {"error": "no scores"}; continue
        bb = best_balanced(fr_pts)
        matched = catch_at_matched_fr(fr_pts, ref_fr) if have_llm else None
        bb_accepts = [(s is not None and s >= bb["T"]) for s in sims]
        results["arms"][name] = {
            "best_balanced": bb,
            "best_balanced_per_cell_catch": per_cell_catch(items, bb_accepts),
            "catch_at_matched_false_refuse": matched,
            "matched_target_false_refuse": round(ref_fr, 3),
            "frontier_size": len(fr_pts),
        }

    # cost
    def tok(u):
        return sum((x.get("prompt_tokens", 0) + x.get("completion_tokens", 0)) for x in u)
    results["llm_tokens"] = {"entail": tok(ent_u), "reason": tok(rea_u), "reason_b": tok(reb_u)} if have_llm else {}

    (HERE / "results.json").write_text(json.dumps(results, indent=2))
    (HERE / "predictions.jsonl").write_text("\n".join(json.dumps(p) for p in preds) + "\n")
    write_md(results, items)
    print("wrote results.json, results.md, predictions.jsonl")
    print(json.dumps({k: (v if "frontier_size" not in str(v) else "...") for k, v in results["arms"].items()}, indent=2)[:1500])

def write_md(R, items):
    a = R["arms"]
    L = []
    L.append("# Gate-ablation result\n")
    L.append(f"N = {R['n']} labelled claim/source pairs "
             f"({sum(is_supported(i) for i in items)} supported, "
             f"{sum(not is_supported(i) for i in items)} not supported: unsupported + contradicted). "
             f"Hand-authored, generic enterprise domains. LLM gate model: `{R['model_llm']}` "
             f"(robustness check: `{R['model_llm_b']}`); embeddings: `{R['embed_model']}`.\n")
    L.append("A gate ACCEPTS a claim it judges supported and REJECTS otherwise. "
             "**catch** = fraction of not-supported claims rejected; "
             "**false-refuse** = fraction of supported claims wrongly rejected. Higher catch and lower false-refuse are better.\n")
    L.append("## Headline\n")
    L.append("| gate | catch | false-refuse | accuracy |")
    L.append("|---|---|---|---|")
    def row(name, catch, fr, acc, note=""):
        return f"| {name}{note} | {catch:.2f} | {fr:.2f} | {acc:.2f} |"
    if "llm_reason" in a:
        r = a["llm_reason"]; L.append(row(f"LLM reasoning ({R['model_llm']})", r["catch"], r["false_refuse"], r["accuracy"]))
    if "llm_reason_b" in a:
        r = a["llm_reason_b"]; L.append(row(f"LLM reasoning ({R['model_llm_b']})", r["catch"], r["false_refuse"], r["accuracy"]))
    if "llm_entail" in a:
        r = a["llm_entail"]; L.append(row("LLM entailment (NLI label)", r["catch"], r["false_refuse"], r["accuracy"]))
    for name, label in [("embedding", "embedding similarity, best threshold"), ("lexical", "lexical similarity, best threshold")]:
        if name in a and "best_balanced" in a[name]:
            bb = a[name]["best_balanced"]; L.append(row(label, bb["catch"], bb["false_refuse"], bb["accuracy"]))
    L.append("")
    # matched false-refuse comparison
    if "llm_reason" in a:
        tfr = a["llm_reason"]["false_refuse"]
        L.append(f"## The fair comparison: catch at matched false-refuse (<= {tfr:.2f}, the LLM reasoning gate's rate)\n")
        L.append("| similarity gate | best catch achievable at that false-refuse |")
        L.append("|---|---|")
        for name in ("embedding", "lexical"):
            m = a.get(name, {}).get("catch_at_matched_false_refuse")
            if m: L.append(f"| {name} | {m['catch']:.2f} (at false-refuse {m['false_refuse']:.2f}) |")
        L.append("")
    # per-cell catch
    L.append("## Catch by design cell (where the gates differ)\n")
    cells = ["unsupported_similarity_trap", "contradicted_high_overlap", "unsupported_offtopic"]
    header = "| gate | " + " | ".join(c.replace("_", " ") for c in cells) + " |"
    L.append(header); L.append("|" + "---|" * (len(cells) + 1))
    def cellrow(name, pcc):
        return "| " + name + " | " + " | ".join(f"{pcc.get(c, float('nan')):.2f}" for c in cells) + " |"
    if "llm_reason" in a: L.append(cellrow("LLM reasoning", a["llm_reason"]["per_cell_catch"]))
    if "llm_entail" in a: L.append(cellrow("LLM entailment", a["llm_entail"]["per_cell_catch"]))
    for name in ("embedding", "lexical"):
        if name in a and "best_balanced_per_cell_catch" in a[name]:
            L.append(cellrow(name + " (best thr)", a[name]["best_balanced_per_cell_catch"]))
    L.append("\nThe similarity-trap and contradicted cells are the ones with high surface overlap, where a "
             "claim looks related to its source but is not supported. That is where a similarity gate is "
             "structurally blind: it cannot separate 'related' from 'supported'.\n")
    if R.get("llm_tokens"):
        L.append(f"\nCost: {sum(R['llm_tokens'].values())} LLM tokens across {R['n']*3} calls "
                 f"(entailment + two reasoning models), plus {R['n']*2} embedding calls. Cents, not dollars.\n")
    L.append("\n_Reproduce:_ `doppler run --project YOUR_PROJECT --config YOUR_CONFIG -- python3 run_eval.py`. "
             "All API responses are cached under `.cache/`; predictions are in `predictions.jsonl`.\n")
    (HERE / "results.md").write_text("\n".join(L))

if __name__ == "__main__":
    main()
