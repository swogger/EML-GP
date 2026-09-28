"""Supplementary Tables S1.x (per-cell Std-GP vs EML-GP, Regime A) with the ln(x) EML-GP rows taken from the
rerun without the size term (P6 for eight cells, P2 for the reference cell); every other row is the original grid.
Prints only the rows that differ from the original analysis, and the Table 3 significance counts.

    python3 research/rerun/make_tables_s1.py > results_rerun/tables_S1_ln.md
"""
import csv, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research"))
from eml_gp_stats import load_all_runs, compare_convergence, compare_tree_size, apply_holm, fmt_p, fmt_effect  # noqa

orig = load_all_runs(os.path.join(ROOT, "results", "standard_gp"))
rr = [r for r in csv.DictReader(open(os.path.join(ROOT, "results_rerun", "P6_native_grid.csv")))] + \
     [r for r in csv.DictReader(open(os.path.join(ROOT, "results_rerun", "P2_bench_ref.csv"))) if r["test_id"] == "1.2"]
ln = {(int(r["G"]), int(r["P"]), int(r["run"])): r for r in rr if r["algo"] == "eml" and r["regime"] == "A" and r["test_id"] == "1.2"}
assert len(ln) == 270, len(ln)
new = orig.copy()
mask = (new["test_id"] == 1.2) | (new["test_id"] == "1.2")
for i in new[mask & (new["algorithm"] == "EML-GP")].index:
    r = ln[(int(new.at[i, "gens"]), int(new.at[i, "pop"]), int(new.at[i, "run"]))]
    new.at[i, "converged"] = r["status"] == "converged"
    new.at[i, "nodes"] = float(r["final_nodes"]) if r["status"] in ("converged", "budget", "plateau") else np.nan


def analyse(df, G, P):
    cell = df[(df["gens"] == G) & (df["pop"] == P)]
    tids = sorted(cell["test_id"].unique(), key=lambda x: float(x))
    conv = apply_holm([compare_convergence(cell[(cell.test_id == t) & (cell.algorithm == "Std-GP")]["converged"],
                                           cell[(cell.test_id == t) & (cell.algorithm == "EML-GP")]["converged"]) for t in tids])
    size = apply_holm([compare_tree_size(cell[(cell.test_id == t) & (cell.algorithm == "Std-GP")]["nodes"],
                                         cell[(cell.test_id == t) & (cell.algorithm == "EML-GP")]["nodes"]) for t in tids])
    return tids, conv, size


crow = lambda r: f"{r['std_rate']:.2f} | {r['eml_rate']:.2f} | {r['delta']:+.2f} | {fmt_p(r['p_value'])} | {fmt_p(r['p_corrected'])} | {'Yes' if r['significant'] else 'No'}"
def srow(r):
    if r.get("insufficient"):
        return f"{r['std_median']:.1f} | {'-' if np.isnan(r['eml_median']) else f'{r[chr(101)+chr(109)+chr(108)+chr(95)+chr(109)+chr(101)+chr(100)+chr(105)+chr(97)+chr(110)]:.1f}'} | insufficient data | - | - | -"
    return f"{r['std_median']:.1f} | {r['eml_median']:.1f} | {fmt_p(r['p_value'])} | {fmt_p(r['p_corrected'])} | {fmt_effect(r['effect_size'])} | {'Yes' if r['significant'] else 'No'}"

cells = [(g, p) for g in (100, 200, 500) for p in (100, 200, 500)]
print("# Table 3 significance counts (convergence / tree size): original -> with ln rerun\n")
tabnum = {c: (2 * i + 1, 2 * i + 2) for i, c in enumerate(cells)}
changes = []
for G, P in cells:
    t0, c0, s0 = analyse(orig, G, P); t1, c1, s1 = analyse(new, G, P)
    nc0, nc1 = sum(r["significant"] for r in c0), sum(r["significant"] for r in c1)
    ns0, ns1 = sum(r["significant"] for r in s0), sum(r["significant"] for r in s1)
    print(f"- {G}×{P}: convergence {nc0} -> {nc1}; tree size {ns0} -> {ns1}")
    for t, a, b in zip(t1, c0, c1):
        if crow(a) != crow(b): changes.append((f"S1.{tabnum[(G, P)][0]}", G, P, t, "conv", crow(a), crow(b)))
    for t, a, b in zip(t1, s0, s1):
        if srow(a) != srow(b): changes.append((f"S1.{tabnum[(G, P)][1]}", G, P, t, "size", srow(a), srow(b)))
print("\n# Rows that change (Std-GP | EML-GP | ... as in each table)\n")
for tab, G, P, t, kind, a, b in changes:
    print(f"- Table {tab} ({G}×{P}), test {t}: {a}  ->  **{b}**")
