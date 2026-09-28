"""Deep audit: recompute the published main-grid tables from the raw per-run CSVs and diff
against the values printed in the manuscript (transcribed below from the submitted PDF).

    python3 research/rerun/audit_grid_tables.py
"""
import csv, os, sys
from collections import defaultdict
import numpy as np
from scipy.stats import fisher_exact, mannwhitneyu

csv.field_size_limit(sys.maxsize)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TESTS = ["1.1", "1.2", "1.3", "1.4", "2.1", "3.1", "3.2", "3.3", "3.4", "3.5", "4.1", "4.2"]
CELLS = [(g, p) for g in (100, 200, 500) for p in (100, 200, 500)]


def rep(a, b, c):
    return [a, b, c] * 3


PAPER = {  # (algo, regime) -> test -> 9 cells in order G100(P100,P200,P500), G200(...), G500(...)
    ("std", "A"): {"1.1": [1] * 9, "1.2": [1] * 9, "1.3": [1] * 9, "1.4": rep(.47, .60, .77), "2.1": rep(.20, .43, .60),
                   "3.1": rep(1, 1, .97), "3.2": [1] * 9, "3.3": rep(.33, .37, .50), "3.4": rep(.17, .13, .27),
                   "3.5": rep(.93, 1, 1), "4.1": [0] * 9, "4.2": [0] * 9},
    ("eml", "A"): {"1.1": [1] * 9, "1.2": rep(.77, .80, .90), "1.3": rep(0, .03, .03), **{t: [0] * 9 for t in TESTS[3:]}},
    ("std", "B"): {"1.1": [1] * 9, "1.2": [1] * 9, "1.3": [1] * 9,
                   "1.4": [.63, .60, .83, .67, .63, .83, .67, .63, .83], "2.1": [.20, .30, .57, .33, .40, .57, .33, .40, .60],
                   "3.1": rep(.97, 1, .97), "3.2": rep(.90, 1, 1), "3.3": [.40, .47, .63, .43, .53, .67, .43, .53, .67],
                   "3.4": rep(.10, .10, .13), "3.5": rep(.93, 1, 1), "4.1": rep(.03, 0, 0), "4.2": [0] * 9},
    ("eml", "B"): {"1.1": [.97, 1, 1, 1, 1, 1, 1, 1, 1], "1.2": [.17, .33, .40, .20, .33, .40, .20, .37, .40],
                   "1.3": rep(0, .03, 0), **{t: [0] * 9 for t in TESTS[3:]}},
}
T6 = {  # test: (raw p, Holm p) at G200/P100, '<' means <0.001
    "1.1": (1.0, 1.0), "1.2": (.011, .063), "1.3": ("<", "<"), "1.4": ("<", "<"), "2.1": (.024, .119),
    "3.1": ("<", "<"), "3.2": ("<", "<"), "3.3": ("<", .006), "3.4": (.052, .209), "3.5": ("<", "<"),
    "4.1": (1.0, 1.0), "4.2": (1.0, 1.0)}
T7 = {  # test: (std median, eml median, raw p, holm p, r)
    "1.1": (2, 3, .004, .022, .400), "1.2": (2, 7, "<", "<", .844), "1.3": (5, 1, "<", "<", -.933),
    "1.4": (13.5, 273, .008, .040, .583), "2.1": (15, 295, .041, .165, .624), "3.1": (2, 1, "<", "<", -.923),
    "3.2": (2, 461, "<", "<", 1.0), "3.3": (13, 399, "<", "<", .904), "3.4": (136, 648, .115, .345, .528),
    "3.5": (43, 485, "<", "<", .953), "4.1": (321, 443, .377, .377, .259), "4.2": (228.5, 419, .184, .369, .313)}


def load(regime):
    d = "standard_gp" if regime == "A" else "mutation_only"
    data = defaultdict(list)
    for G, P in CELLS:
        for r in range(1, 31):
            for row in csv.DictReader(open(os.path.join(ROOT, "results", d, f"results_{G}_{P}_{r}.csv"))):
                for algo, pre in (("std", "Std"), ("eml", "EML")):
                    data[(algo, G, P, row["Test ID"])].append((row[f"{pre} Status"], row[f"{pre} Nodes"]))
    return data


def holm(ps):
    order = np.argsort(ps); m = len(ps); out = [0.0] * m; run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * ps[i])); out[i] = run
    return out


def fmt(p):
    return "<" if p < 0.001 else round(p, 3)


def main():
    bad = 0
    for regime in "AB":
        data = load(regime)
        for algo in ("std", "eml"):
            for t in TESTS:
                got = [sum(s == "CONVERGED" for s, _ in data[(algo, G, P, t)]) / 30 for G, P in CELLS]
                want = PAPER[(algo, regime)][t]
                diffs = [(CELLS[i], want[i], round(got[i], 2)) for i in range(9) if abs(round(got[i], 2) - want[i]) > 0.005]
                if diffs:
                    bad += 1
                    print(f"RATE MISMATCH {algo}-{regime} test {t}: (cell, paper, data) {diffs}")
        if regime == "A":
            print("\nTable 6 (G200/P100) Fisher recomputation:")
            raws = []
            for t in TESTS:
                s = sum(x == "CONVERGED" for x, _ in data[("std", 200, 100, t)])
                e = sum(x == "CONVERGED" for x, _ in data[("eml", 200, 100, t)])
                raws.append(fisher_exact([[s, 30 - s], [e, 30 - e]])[1])
            hs = holm(raws)
            for t, p, h in zip(TESTS, raws, hs):
                ok = (fmt(p), fmt(h)) == T6[t] or (isinstance(T6[t][0], float) and abs(p - T6[t][0]) < 0.0015 and abs(h - T6[t][1]) < 0.0015) \
                    or (T6[t][0] == "<" and p < .001 and (T6[t][1] == "<" and h < .001 or isinstance(T6[t][1], float) and abs(h - T6[t][1]) < .0015))
                if not ok:
                    bad += 1
                print(f"  {t}: raw {fmt(p)} Holm {fmt(h)}  paper {T6[t]}  {'OK' if ok else 'MISMATCH'}")
            print("\nTable 7 (G200/P100) Mann-Whitney recomputation over non-censored runs (r > 0: EML larger):")
            rows, raws = [], []
            for t in TESTS:
                s = [float(n) for x, n in data[("std", 200, 100, t)] if x != "TIMEOUT" and n]
                e = [float(n) for x, n in data[("eml", 200, 100, t)] if x != "TIMEOUT" and n]
                U = mannwhitneyu(e, s, alternative="two-sided")
                r = 2 * U.statistic / (len(e) * len(s)) - 1
                rows.append((t, np.median(s), np.median(e), U.pvalue, r, len(s), len(e))); raws.append(U.pvalue)
            hs = holm(raws)
            for (t, ms, me, p, r, ns, ne), h in zip(rows, hs):
                w = T7[t]
                ok = abs(ms - w[0]) < 0.01 and abs(me - w[1]) < 0.01 and abs(r - w[4]) < 0.0015
                if not ok:
                    bad += 1
                print(f"  {t}: med {ms}/{me} p {fmt(p)} Holm {fmt(h)} r {r:+.3f} (n {ns}/{ne})  paper {w}  {'OK' if ok else 'MISMATCH'}")
    print(f"\nTOTAL mismatching items: {bad}")


if __name__ == "__main__":
    main()
