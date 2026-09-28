"""Run the findings suite: instrument self-tests first, then every finding.

    python3 research/findings/run_findings.py                          # evidence only
    python3 research/findings/run_findings.py --manuscript paper.pdf --manuscript supplement.pdf
    python3 research/findings/run_findings.py --skip-slow --online     # skip the SSC re-run; refresh DOI cache

Text status per finding (needs --manuscript):
  OPEN  the erroneous wording is still present, or required wording is missing
  FIXED neither
"""
import argparse, json, os, sys, time, traceback
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import instruments as I
from findings import F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", action="append", default=[])
    ap.add_argument("--online", action="store_true")
    ap.add_argument("--skip-slow", action="store_true")
    ap.add_argument("--baseline", action="store_true",
                    help="manuscript is the UNEDITED submission: every error phrase must be found (else PATTERN_FAIL)")
    ap.add_argument("--out", default=os.path.join(I.ROOT, "revision", "FINDINGS_REPORT.md"))
    a = ap.parse_args()

    t0 = time.time()
    st = I.self_tests()
    failed = [x for x in st if not x[1]]
    print("instrument self-tests:"); [print(f"  {'PASS' if ok else 'FAIL'}  {n} {d}") for n, ok, d in st]
    raw = "\n".join(I.read_document(p) for p in a.manuscript) if a.manuscript else None
    text = (I.normalise(raw) + " || " + I.normalise(raw, keep_line_hyphens=True)) if raw else None
    if text is not None and not ("phase-space brittleness" in text and "genetic programming" in text):
        print("  FAIL  manuscript text extraction: sentinel phrases not found")
        text_ok = False
    else:
        text_ok = True

    results = []
    for f in F:
        if failed:
            status, detail = "NOT RUN", "instrument self-test failed"
        elif a.skip_slow and f["id"] == "A7":
            status, detail = "SKIPPED", "slow check skipped (--skip-slow)"
        else:
            try:
                status, detail = f["evidence"]()
            except Exception as e:
                status, detail = "CHECK_ERROR", f"{type(e).__name__}: {e}"
        if text is None or (not f["present"] and not f["require"]):
            ts = "—"
        elif not text_ok:
            ts = "EXTRACTION_FAIL"
        else:
            found = [p for p in f["present"] if p in text]
            bad = found + [f"missing: {p}" for p in f["require"] if p not in text]
            ts = "OPEN" if bad else "FIXED"
            if a.baseline and f["present"] and not found:        # alternatives: at least one must match the submission
                ts = "PATTERN_FAIL: none of " + "; ".join(f["present"])
        results.append(dict(id=f["id"], sev=f["sev"], kind=f["kind"], title=f["title"], status=status, detail=detail, text=ts))
        print(f"{f['id']:5s} {status:14s} {ts:6s} {f['title'][:70]}")

    from collections import Counter
    c = Counter(r["status"] for r in results)
    lines = [f"# Findings report", "",
             f"Generated {time.strftime('%Y-%m-%d %H:%M')} by `research/findings/run_findings.py` in {time.time()-t0:.0f} s.",
             f"Manuscript(s): {', '.join(os.path.basename(p) for p in a.manuscript) or 'none (evidence only)'}.", "",
             "## Instrument self-tests", "", "| Test | Result |", "|---|---|"]
    lines += [f"| {n} | {'PASS' if ok else '**FAIL** ' + d} |" for n, ok, d in st]
    lines += ["", f"## Findings ({', '.join(f'{k} {v}' for k, v in sorted(c.items()))})", "",
              "Status: CONFIRMED = the error exists; FACT = undocumented implementation fact; UNREPRODUCIBLE = published value "
              "cannot be reproduced; REFUTED = evidence contradicts the finding (drop it); SUGGESTION = wording. "
              "Text: OPEN = erroneous wording still in the manuscript (or required wording missing); FIXED = not.", "",
              "| ID | Sev | Status | Text | Finding | Evidence |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['sev']} | {r['status']} | {r['text']} | {r['title']} | {r['detail'].replace('|', '/')} |" for r in results]
    open(a.out, "w").write("\n".join(lines) + "\n")
    json.dump(results, open(a.out.replace(".md", ".json"), "w"), indent=1)
    print(f"\n{dict(c)}  -> {a.out}")
    sys.exit(1 if failed or c.get("CHECK_ERROR") else 0)


if __name__ == "__main__":
    main()
