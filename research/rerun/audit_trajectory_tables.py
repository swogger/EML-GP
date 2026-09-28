"""Deep audit: recompute Table 10, Table 8 and Table S2 (Regime A, EML ln/addition rows) from
the raw trajectory-harness and SSC files, and diff against the manuscript values.

    python3 research/rerun/audit_trajectory_tables.py
"""
import csv, glob, os
import numpy as np
from scipy.stats import wilcoxon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TESTS = ["1.1", "1.2", "1.3", "1.4", "2.1", "3.1", "3.2", "3.3", "3.4", "3.5", "4.1", "4.2"]
T10 = {  # test: (median A, median B, r, Holm p)
    "1.1": (0, 0, None, None), "1.2": (0.0, 8.5e-6, .92, .0014), "1.3": (8.300, 7.050, -.64, .00056),
    "1.4": (.092, .052, -.33, .559), "2.1": (.222, .288, 0.0, 1.0), "3.1": (5.700, 2.920, -.73, .00020),
    "3.2": (.406, .688, .13, 1.0), "3.3": (1.740, 2.000, .27, .905), "3.4": (.019, .027, .13, 1.0),
    "3.5": (333.5, 326.8, 0.0, 1.0), "4.1": (.436, .482, .20, 1.0), "4.2": (.361, .366, -.07, 1.0)}


def final(path):
    rows = list(csv.DictReader(open(path)))
    return float(rows[-1]["best_fitness"]), int(rows[-1]["generation"])


def traj(regime, algo, t, G=200, P=100):
    d = "standard_gp" if regime == "A" else "mutation_only"
    out = []
    for r in range(1, 31):
        f = os.path.join(ROOT, "results", d, "convergence_data", f"convergence_{t}_{algo}_{G}_{P}_{r:02d}.csv")
        out.append(final(f))
    return out


def holm(ps):
    order = np.argsort(ps); m = len(ps); out = [0.0] * m; run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * ps[i])); out[i] = run
    return out


def main():
    print("Table 10 (EML, G200/P100, trajectory harness): r > 0 means Regime A lower error")
    res, ps = {}, []
    for t in TESTS:
        A = traj("A", "eml", t); B = traj("B", "eml", t)
        a = np.array([x for x, _ in A]); b = np.array([x for x, _ in B])
        d = b - a
        nz = d[d != 0]
        if len(nz) == 0:
            res[t] = (np.median(a), np.median(b), None, 1.0); ps.append(1.0); continue
        ranks = np.argsort(np.argsort(np.abs(nz))) + 1.0
        # average ranks for ties in |d|
        absd = np.abs(nz); uniq = {}
        for v in np.unique(absd):
            idx = np.where(absd == v)[0]; ranks[idx] = ranks[idx].mean()
        r = (ranks[nz > 0].sum() - ranks[nz < 0].sum()) / ranks.sum()
        p = wilcoxon(nz).pvalue
        res[t] = (np.median(a), np.median(b), r, p); ps.append(p)
        trunc_a = sum(g < 199 and x > 1e-6 for x, g in A); trunc_b = sum(g < 199 and x > 1e-6 for x, g in B)
        res[t] += (trunc_a, trunc_b)
    hs = holm(ps)
    for t, h in zip(TESTS, hs):
        v = res[t]; w = T10[t]
        r = v[2]
        ok_med = abs(v[0] - w[0]) <= max(0.0015, 0.0015 * abs(w[0])) and abs(v[1] - w[1]) <= max(1e-6, 0.0015 * abs(w[1]) + 5e-4)
        ok_r = (w[2] is None and r is None) or (r is not None and w[2] is not None and abs(r - w[2]) < 0.006)
        ok_h = w[3] is None or abs(h - w[3]) < max(0.0006, 0.02 * w[3])
        extra = f" truncated A/B {v[4]}/{v[5]}" if len(v) > 4 else ""
        print(f"  {t}: med A {v[0]:.4g} B {v[1]:.4g}  r {'' if r is None else f'{r:+.2f}'}  Holm {h:.3g}  "
              f"paper {w}  {'OK' if (ok_med and ok_r and ok_h) else 'CHECK'}{extra}")

    print("\nTable 8 (SSC, G200/P100): medians of final best error")
    ssc = os.path.join(ROOT, "results", "ssc", "runs")
    for t in ("1.1", "1.2", "1.3", "2.1", "3.2", "3.3"):
        for algo in ("std_ssc", "eml_ssc"):
            fs = sorted(glob.glob(os.path.join(ssc, f"ssc_{t}_{algo}_*.csv")))
            vals = [final(f) for f in fs]
            trunc = sum(g < 199 and x > 1e-6 for x, g in vals)
            print(f"  {t} {algo}: n {len(vals)}  median {np.median([x for x, _ in vals]):.4g}  truncated-nonconverged {trunc}")
        for regime, algo in (("A", "std"), ("A", "eml"), ("B", "eml")):
            vals = traj(regime, algo, t)
            print(f"  {t} {algo} regime {regime} (trajectory): median {np.median([x for x, _ in vals]):.4g}")

    print("\nTable S2 spot checks (Regime A, EML, pooled over P, G in 100/200/500)")
    for t in ("1.2", "1.3"):
        for G in (100, 200, 500):
            conv, first, fail = 0, [], []
            for P in (100, 200, 500):
                for r in range(1, 31):
                    f = os.path.join(ROOT, "results", "standard_gp", "convergence_data", f"convergence_{t}_eml_{G}_{P}_{r:02d}.csv")
                    rows = list(csv.DictReader(open(f)))
                    x, g = float(rows[-1]["best_fitness"]), int(rows[-1]["generation"])
                    if x <= 1e-6:
                        conv += 1
                        first.append(next(int(q["generation"]) for q in rows if float(q["best_fitness"]) <= 1e-6))
                    else:
                        fail.append(g)
            q = lambda v: f"{np.median(v):.0f} [{np.percentile(v,25):.0f}-{np.percentile(v,75):.0f}]" if v else "-"
            print(f"  {t} G={G}: conv {conv}/90  first-conv median {np.median(first) if first else '-'} max {max(first) if first else '-'}  fail-term {q(fail)}")


if __name__ == "__main__":
    main()
