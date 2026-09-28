"""Third-pass ('fresh eyes') checks of manuscript claims not covered by earlier audits.
Every block prints the manuscript value next to the value recomputed from raw files.

    python3 research/rerun/fresh_eyes_checks.py
"""
import csv, glob, json, os, sys, importlib
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import wilcoxon, fisher_exact

csv.field_size_limit(sys.maxsize)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
R = os.path.join(ROOT, "results")
CELLS = [(g, p) for g in (100, 200, 500) for p in (100, 200, 500)]


def traj_final(regime, algo, t, G, P, r):
    d = "standard_gp" if regime == "A" else "mutation_only"
    rows = list(csv.DictReader(open(f"{R}/{d}/convergence_data/convergence_{t}_{algo}_{G}_{P}_{r:02d}.csv")))
    return float(rows[-1]["best_fitness"])


def holm(ps):
    order = np.argsort(ps); m = len(ps); out = [0.0] * m; run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * ps[i])); out[i] = run
    return out


def main_grid(regime):
    d = "standard_gp" if regime == "A" else "mutation_only"
    data = defaultdict(list)
    for G, P in CELLS:
        for r in range(1, 31):
            for row in csv.DictReader(open(f"{R}/{d}/results_{G}_{P}_{r}.csv")):
                data[("std", G, P, row["Test ID"])].append(row)
                data[("eml", G, P, row["Test ID"])].append(row)
    return data


print("1. Synthetic minimality: K_proven == K_construction for every target with K <= 11")
tg = list(csv.DictReader(open(f"{R}/synthetic_dense_k/synthetic_targets.csv")))
bad = [t["target_id"] for t in tg if int(t["K_construction"]) <= 11 and t["K_proven"] != t["K_construction"]]
print(f"   violations: {len(bad)} {bad[:5]}; K>11 with K_proven set: {sum(1 for t in tg if int(t['K_construction'])>11 and t['K_proven'] not in ('', 'None'))}")

print("\n2. §5.3.1 'Std-GP completes every run on exp, ln, addition, sinh at every grid cell'")
for regime in "AB":
    g = main_grid(regime)
    to = sum(r["Std Status"] == "TIMEOUT" for t in ("1.1", "1.2", "1.3", "3.1") for G, P in CELLS for r in g[("std", G, P, t)])
    print(f"   Regime {regime}: Std-GP timeouts on those four targets across the grid = {to}")

print("\n3. Fig 13 (reference cell, Regime A): addition EML sizes; arctan EML survivors")
gA = main_grid("A")
add = [r["EML Nodes"] for r in gA[("eml", 200, 100, "1.3")]]
print("   addition EML node counts:", Counter(add).most_common(4))
arc = sorted(int(r["EML Nodes"]) for r in gA[("eml", 200, 100, "3.2")] if r["EML Status"] != "TIMEOUT")
print(f"   arctan EML survivors n={len(arc)} range {arc[0]}–{arc[-1]} median {np.median(arc)} (paper: n=8, 9–1,365, median 461)")
std_add = [int(r["Std Nodes"]) for r in gA[("std", 200, 100, "1.3")]]
print(f"   Std-GP addition median {np.median(std_add)} (paper 5)")

print("\n4. §5.3.3 x^x, Std-GP Regime A vs B (trajectory harness)")
for G, P in CELLS:
    a = [traj_final("A", "std", "3.3", G, P, r) for r in range(1, 31)]
    b = [traj_final("B", "std", "3.3", G, P, r) for r in range(1, 31)]
    ma, mb = np.median(a), np.median(b)
    tag = ""
    if (G, P) == (200, 100):
        d = np.array(b) - np.array(a)
        tag = f"  seeds favour A {int(np.sum(d > 0))}, favour B {int(np.sum(d < 0))}, tied {int(np.sum(d == 0))}  (paper 11/14/5)"
    print(f"   G{G}P{P}: median A {ma:.4g}  B {mb:.4g}  ratio A/B {ma/mb if mb else float('inf'):.1f}{tag}")
print("   per-cell direction of median final error (A vs B), Std-GP, targets claimed consistent:")
for t in ("3.3", "1.4", "3.4"):
    dirs = []
    for G, P in CELLS:
        a = np.median([traj_final("A", "std", t, G, P, r) for r in range(1, 31)])
        b = np.median([traj_final("B", "std", t, G, P, r) for r in range(1, 31)])
        dirs.append("B" if b < a else ("A" if a < b else "="))
    print(f"   {t}: {''.join(dirs)} (paper: 3.3 and 1.4 favour B in all nine; 3.4 favours A)")

print("\n5. Table 9 (Phase 5 benchmarks) from results/sr_benchmarks")
summ = os.path.join(R, "sr_benchmarks", "sr_benchmark_results_summary.csv")
if os.path.exists(summ):
    for row in csv.DictReader(open(summ)):
        print("  ", {k: v for k, v in row.items()})
runs = os.path.join(R, "sr_benchmarks", "runs")
for b in ("nguyen1", "nguyen7", "keijzer6", "vladislavleva4"):
    for algo in ("std_a", "eml_a", "std_b", "eml_b"):
        fs = glob.glob(os.path.join(runs, f"*{b}*{algo}*.csv"))
        vals = []
        for f in fs:
            rows = list(csv.DictReader(open(f)))
            if rows:
                vals.append(float(rows[-1][list(rows[-1].keys())[-1]]))
        if vals:
            conv = sum(v <= 1e-6 for v in vals)
            print(f"   {b} {algo}: files {len(fs)}  converged {conv}  median {np.median(vals):.3g}")

print("\n6. §5.4 calibration against the main study (calibration_same_function.csv)")
for row in csv.DictReader(open(f"{R}/synthetic_dense_k/calibration_same_function.csv")):
    print("  ", {k: row[k] for k in ("target", "regime", "real_conv_rate", "synth_conv_rate_nmse_rule", "fisher_p_vs_real_nmse_rule",
                                    "synth_conv_rate_abs_mse_rule", "fisher_p_vs_real_abs_rule", "var_target")})

print("\n7. Reference case position among K = 7 targets (original runs, Regime A)")
syn = list(csv.DictReader(open(f"{R}/synthetic_dense_k/synthetic_runs.csv")))
per = defaultdict(list)
for r in syn:
    if r["regime"] == "A" and int(r["K_construction"]) == 7:
        per[r["target_id"]].append(r["converged"] == "true")
rates = {k: np.mean(v) for k, v in per.items()}
ref = rates["reviewer_ce"]; vals = sorted(rates.values())
pct = 100 * sum(v < ref for v in vals) / len(vals)
print(f"   ref {ref:.2f}; band median {np.median(vals):.2f}; below-ref share {pct:.0f}% (paper: 0.70, median 0.80, 45th percentile)")

print("\n8. S12 original fits, K = 3–17 transition band (budget data)")
sys.path.insert(0, os.path.join(ROOT, "research", "rerun"))
from analyze_p1 import logit  # noqa: E402


def k50_band(rows, reg, drop_cens):
    rr = [r for r in rows if r["regime"] == reg and int(r["K_construction"]) <= 17 and not (drop_cens and r["terminal_state"] == "timeout")]
    K = np.array([float(r["K_construction"]) for r in rr]); y = np.array([float(r["converged"] == "true") for r in rr])
    b = logit(K, y); return -b[0] / b[1]


main_rows = syn + list(csv.DictReader(open(f"{R}/synthetic_dense_k/synthetic_runs_lowk.csv")))
b800 = list(csv.DictReader(open(f"{R}/synthetic_dense_k/budget_pilot_g800.csv"))) + list(csv.DictReader(open(f"{R}/synthetic_dense_k/g800_lowk.csv")))
b3200 = list(csv.DictReader(open(f"{R}/synthetic_dense_k/g3200_main.csv"))) + list(csv.DictReader(open(f"{R}/synthetic_dense_k/g3200_lowk.csv")))
for lab, rows in (("200", main_rows), ("800", b800), ("3200", b3200)):
    print(f"   G={lab}: A cens-as-fail {k50_band(rows,'A',False):.2f}  A complete-case {k50_band(rows,'A',True):.2f}  B cens-as-fail {k50_band(rows,'B',False):.2f}")
print("   (paper: 200: 8.74/8.74/6.15; 800: 9.02/9.93/6.84; 3200: 8.97/10.69/7.10)")

print("\n9. S10 control vs main (Regime A), Wilcoxon on final error over pairs where both returned a value")
ctl = [r for r in csv.DictReader(open(f"{R}/fixed_set_control/control_runs.csv")) if r["arm"] == "FIX" and r["regime"] == "A"]
sys.path.insert(0, os.path.join(ROOT, "research")); from seeds import SEEDS  # noqa: E402
seed_to_run = {s: i for i, s in enumerate(SEEDS) if s}
res = []
for t in ("2.1", "3.1", "3.2", "3.3", "3.5", "4.2"):
    m = {i + 1: r for i, r in enumerate(gA[("std", 200, 100, t)])}
    pairs = []
    for c in ctl:
        if c["test_id"] != t or c["final_error"] in ("", "None"):
            continue
        run = seed_to_run[int(c["seed"])]
        mr = m.get(run)
        if mr and mr["Std Status"] != "TIMEOUT" and mr["Std Error"] not in ("", "FAIL"):
            pairs.append((float(mr["Std Error"]), float(c["final_error"])))
    a, b = np.array(pairs).T
    d = b - a
    p = wilcoxon(d[d != 0]).pvalue if np.any(d != 0) else 1.0
    res.append((t, len(pairs), np.median(a), np.median(b), p))
hs = holm([x[4] for x in res])
for (t, n, ma, mb, p), h in zip(res, hs):
    print(f"   {t}: n {n}  main median {ma:.3g}  control median {mb:.3g}  Holm {h:.3g}")
print("   (paper: 2.1 n11 9e-6/0 1.00; 3.1 n10 0/0.162 0.0078; 3.2 n13 0/0.0948 0.0015; 3.3 n9 0/0.0239 1.00; 3.5 n19 0/357.7 0.0015; 4.2 n13 0.342/0.343 1.00)")

print("\n10. Table 8 SSC effect (Wilcoxon, SSC vs standard crossover, paired by run; Holm across 6 per grammar)")
for algo in ("eml", "std"):
    ps, rows_ = [], []
    for t in ("1.1", "1.2", "1.3", "2.1", "3.2", "3.3"):
        s = [float(list(csv.DictReader(open(f"{R}/ssc/runs/ssc_{t}_{algo}_ssc_{r:02d}.csv")))[-1]["best_fitness"]) for r in range(1, 31)]
        x = [traj_final("A", algo, t, 200, 100, r) for r in range(1, 31)]
        d = np.array(s) - np.array(x)
        p = wilcoxon(d[d != 0]).pvalue if np.sum(d != 0) > 0 else 1.0
        ps.append(p); rows_.append((t, np.median(x), np.median(s), int(np.sum(d > 0)), int(np.sum(d < 0))))
    for (t, mx, ms, worse, better), h in zip(rows_, holm(ps)):
        print(f"   {algo} {t}: std-xover {mx:.3g}  SSC {ms:.3g}  SSC worse in {worse} / better in {better}  Holm {h:.3g}")
print("   (paper EML: ln 0.002 worse, arctan 0.002 worse, x^x 0.005 worse, sin+cos 0.109; Std: sin+cos 0.126, x^x 0.617)")

print("\n11. Table B.1 software versions on this machine")
import platform
for mod in ("numpy", "pandas", "scipy", "sympy"):
    try:
        print(f"   {mod} {importlib.import_module(mod).__version__}")
    except Exception as e:
        print(f"   {mod}: {e}")
print(f"   python {platform.python_version()}  (paper: Python 3.9.6, NumPy 2.0.2, Pandas 2.3.3, SciPy 1.13.1)")
