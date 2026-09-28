#!/usr/bin/env python3
"""
Regenerate every figure in the manuscript as high-resolution PNG (400 dpi) and
vector PDF, into figures/ at the repository root.

    python3 make_all_figures.py

Figures 3-6, 8 and 9 reuse the aggregation and panel styling of plot_convergence.py,
so the regenerated versions match the published ones. Figure 12 is delegated to
synthetic/plot_fig12.py, which draws its own in-plot annotations.
"""
import os, sys, glob, re, subprocess
from collections import defaultdict
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT  = os.path.join(ROOT, "figures")
DPI  = 400
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE)
csv_limit = __import__("csv"); csv_limit.field_size_limit(sys.maxsize)

from plot_convergence import load_runs, aggregate_panel, plot_panel   # noqa: E402

A_DIR = os.path.join(ROOT, "results", "standard_gp", "convergence_data")
B_DIR = os.path.join(ROOT, "results", "mutation_only", "convergence_data")
CELL  = (200, 100)

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=DPI,
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved {name}.png / .pdf")

# ---------------------------------------------------------------- Fig 1
ADDITION = "eml(1, eml(eml(eml(1, eml(eml(1, eml(1, eml(x, 1))), 1)), eml(y, 1)), 1))"

def parse(expr):
    expr = expr.strip()
    if not expr.startswith("eml("):
        return {"label": expr, "leaf": True}
    inner, depth, split = expr[4:-1], 0, None
    for i, c in enumerate(inner):
        if c == "(": depth += 1
        elif c == ")": depth -= 1
        elif c == "," and depth == 0: split = i; break
    return {"label": "eml", "leaf": False,
            "l": parse(inner[:split]), "r": parse(inner[split+1:])}

def fig1():
    tree = parse(ADDITION)
    pos, counter = {}, [0]
    def layout(n, d):
        if n["leaf"]:
            counter[0] += 1; pos[id(n)] = (d, counter[0]); return
        layout(n["l"], d + 1)
        pos[id(n)] = (d, None)
        layout(n["r"], d + 1)
        pos[id(n)] = (d, (pos[id(n["l"])][1] + pos[id(n["r"])][1]) / 2)
    layout(tree, 0)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    def draw(n):
        x, y = pos[id(n)]
        if not n["leaf"]:
            for ch in (n["l"], n["r"]):
                cx, cy = pos[id(ch)]
                ax.annotate("", xy=(cx - 0.30, cy), xytext=(x + 0.30, y),
                            arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0))
                draw(ch)
            ax.add_patch(plt.Circle((x, y), 0.30, facecolor="#cfe2f3",
                                    edgecolor="0.3", lw=1.0, zorder=3))
            ax.text(x, y, "eml", ha="center", va="center", fontsize=8.5, zorder=4)
        else:
            var = n["label"] not in ("1",)
            ax.add_patch(FancyBboxPatch((x - 0.26, y - 0.26), 0.52, 0.52,
                boxstyle="round,pad=0.02", facecolor="#d9ead3" if not var else "white",
                edgecolor="0.2", lw=1.4 if var else 1.0, zorder=3))
            ax.text(x, y, n["label"], ha="center", va="center",
                    fontsize=9.5, style="italic" if var else "normal", zorder=4)
    draw(tree)
    ax.set_xlim(-0.8, max(p[0] for p in pos.values()) + 0.9)
    ax.set_ylim(0.2, counter[0] + 0.8)
    ax.axis("off"); ax.invert_yaxis()
    save(fig, "Fig01_addition_tree_K19")

# ---------------------------------------------------------------- Fig 2
def fig2():
    fig, ax = plt.subplots(figsize=(10, 7.5))
    def box(x, y, w, h, title, sub="", fc="white"):
        ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.08", facecolor=fc, edgecolor="0.25", lw=1.2, zorder=3))
        ax.text(x, y + (0.10 if sub else 0), title, ha="center", va="center",
                fontsize=10, fontweight="bold", zorder=4)
        if sub:
            ax.text(x, y - 0.16, sub, ha="center", va="center", fontsize=8.5, zorder=4)
    def arrow(x, y0, y1, label=""):
        ax.annotate("", xy=(x, y1), xytext=(x, y0),
                    arrowprops=dict(arrowstyle="->", color="0.3", lw=1.2))
        if label:
            ax.text(x + 0.12, (y0 + y1) / 2, label, fontsize=8.5, va="center")
    box(2.2, 7.4, 3.0, 0.72, "Regime A", "Crossover + mutation", "#cfe2f3")
    box(6.4, 7.4, 3.0, 0.72, "Regime B", "Mutation only", "#cfe2f3")
    ax.plot([2.2, 6.4], [7.0, 7.0], color="0.3", lw=1.2)
    ax.plot([4.3, 4.3], [7.0, 6.75], color="0.3", lw=1.2)
    arrow(4.3, 6.75, 6.30, "× 2 models")
    box(2.2, 5.9, 3.0, 0.72, "EML-GP", "Homogeneous operator")
    box(6.4, 5.9, 3.0, 0.72, "Std-GP", "Standard primitives")
    ax.plot([2.2, 6.4], [5.5, 5.5], color="0.3", lw=1.2)
    ax.plot([4.3, 4.3], [5.5, 5.28], color="0.3", lw=1.2)
    arrow(4.3, 5.28, 4.85, "× 12 tests (4 phases)")
    for i, (lbl, sub) in enumerate([("Phase 1", "Tests 1.1–1.4"), ("Phase 2", "Test 2.1"),
                                    ("Phase 3", "Tests 3.1–3.5"), ("Phase 4", "Tests 4.1–4.2")]):
        box(1.3 + i * 2.0, 4.45, 1.75, 0.70, lbl, sub)
    ax.plot([1.3, 7.3], [4.10, 4.10], color="0.3", lw=1.2)
    ax.plot([4.3, 4.3], [4.10, 3.88], color="0.3", lw=1.2)
    arrow(4.3, 3.88, 3.42, "× 9 grid × 30 runs")
    box(4.3, 3.05, 7.2, 0.80, "3 × 3 grid × 30 seeded runs",
        "Generations {100, 200, 500} × population {100, 200, 500}")
    arrow(4.3, 2.63, 2.15)
    box(4.3, 1.78, 7.2, 0.80, "2 × 2 × 12 × 9 × 30 = 12,960 trials",
        "regimes × models × tests × grid × runs", "#fce5cd")
    ax.set_xlim(0, 8.6); ax.set_ylim(1.2, 8.0); ax.axis("off")
    save(fig, "Fig02_experimental_design")

# ------------------------------------------------- Figs 3-6, 8, 9 (trajectories)
_cache = {}
def runs_for(d):
    if d not in _cache: _cache[d] = load_runs(d)
    return _cache[d]

def traj(test_id, name, dirs=(("A", A_DIR),), figsize=(6.4, 4.3), titles=None):
    n = len(dirs)
    fig, axes = plt.subplots(1, n, figsize=(figsize[0] * n, figsize[1]), squeeze=False)
    for ax, (tag, d) in zip(axes[0], dirs):
        runs = runs_for(d)[CELL]
        plot_panel(ax, aggregate_panel(runs, test_id, "std"),
                   aggregate_panel(runs, test_id, "eml"),
                   (titles or {}).get(tag, ""), *CELL)
    save(fig, name)

def multi(pairs, name):
    fig, axes = plt.subplots(1, len(pairs), figsize=(6.4 * len(pairs), 4.3), squeeze=False)
    for ax, (tid, title) in zip(axes[0], pairs):
        runs = runs_for(A_DIR)[CELL]
        plot_panel(ax, aggregate_panel(runs, tid, "std"),
                   aggregate_panel(runs, tid, "eml"), title, *CELL)
    save(fig, name)

# ---------------------------------------------------------------- Fig 7
def fig7():
    import csv as _csv
    names = {"1.1":"Exp(x)","1.2":"Ln(x)","1.3":"Addition","1.4":"Exp Comp.","2.1":"Sin+Cos",
             "3.1":"Sinh(x)","3.2":"Arctan(x)","3.3":"x$^x$","3.4":"Sigmoid",
             "3.5":"Polynomial","4.1":"Nested I","4.2":"Nested II"}
    acc = defaultdict(lambda: {"std": [], "eml": []})
    for f in glob.glob(os.path.join(ROOT, "results", "standard_gp", "results_200_100_*.csv")):
        for r in _csv.DictReader(open(f)):
            for k, col in (("std", "Std Nodes"), ("eml", "EML Nodes")):
                if r[col]:
                    try: acc[r["Test ID"]][k].append(int(r[col]))
                    except ValueError: pass
    order = list(names)
    s = [np.median(acc[t]["std"]) if acc[t]["std"] else 0 for t in order]
    e = [np.median(acc[t]["eml"]) if acc[t]["eml"] else 0 for t in order]
    x = np.arange(len(order)); w = 0.38
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x - w/2, s, w, label="Std-GP nodes", color="#6fa8dc", edgecolor="0.3", lw=0.6)
    ax.bar(x + w/2, e, w, label="EML-GP nodes", color="#b03030", edgecolor="0.3", lw=0.6)
    ax.set_yscale("log"); ax.set_ylim(0.8, 1200)
    ax.set_xticks(x); ax.set_xticklabels([names[t] for t in order], rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Median final tree size (nodes, log scale)", fontsize=10)
    ax.legend(fontsize=9, frameon=True); ax.grid(axis="y", alpha=0.25, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    save(fig, "Fig07_median_tree_size")

# ---------------------------------------------------------------- Fig 10
def fig10():
    def med(pat):
        cur = []
        for f in sorted(glob.glob(pat)):
            df = pd.read_csv(f)
            if len(df): cur.append(df.set_index("generation")["best_fitness"])
        if not cur: return None
        al = pd.concat(cur, axis=1).sort_index().ffill()
        return al.index, al.median(axis=1).clip(lower=1e-10)
    series = [
        (os.path.join(A_DIR, "convergence_1.2_std_200_100_*.csv"), "Std-GP (standard xover)", "#1f77b4", "-"),
        (os.path.join(A_DIR, "convergence_1.2_eml_200_100_*.csv"), "EML-GP (standard xover)", "#d62728", ":"),
        (os.path.join(B_DIR, "convergence_1.2_eml_200_100_*.csv"), "EML-GP (mutation only)", "#d62728", "-."),
        (os.path.join(ROOT, "results", "ssc", "runs", "ssc_1.2_std_ssc_*.csv"), "Std-GP + SSC", "#1f77b4", "--"),
        (os.path.join(ROOT, "results", "ssc", "runs", "ssc_1.2_eml_ssc_*.csv"), "EML-GP + SSC", "#d62728", "--"),
    ]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for pat, lbl, col, ls in series:
        r = med(pat)
        if r is None: print(f"    (no data: {lbl})"); continue
        blue = col == "#1f77b4"
        ax.plot(r[0], r[1], ls, color=col, lw=2.2 if blue else 1.6,
                zorder=3 if blue else 2, label=f"{lbl} (n=30)")
    ax.set_yscale("log"); ax.set_xlabel("Generation", fontsize=10); ax.set_ylabel("MSE", fontsize=10)
    ax.grid(True, which="both", alpha=0.25, lw=0.5); ax.legend(fontsize=8, loc="upper right")
    save(fig, "Fig10_ssc_ln")

# ---------------------------------------------------------------- Fig 11
def fig11():
    p = os.path.join(ROOT, "results", "sr_benchmarks", "sr_benchmark_convergence_data.csv")
    df = pd.read_csv(p); df = df[df["test_id"] == "nguyen7"]
    style = {"std_a": ("Std-GP (crossover+mut)", "#1f77b4", "-"),
             "eml_a": ("EML-GP (crossover+mut)", "#d62728", ":"),
             "std_b": ("Std-GP (mutation only)", "#1f77b4", "--"),
             "eml_b": ("EML-GP (mutation only)", "#d62728", "--")}
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for algo, (lbl, col, ls) in style.items():
        sub = df[df["algorithm"] == algo].sort_values("generation")
        if sub.empty: continue
        ax.plot(sub["generation"], sub["median_fitness"].clip(lower=1e-10), ls,
                color=col, lw=1.6, label=f"{lbl} (n={int(sub['n_runs'].iloc[0])})")
        ax.fill_between(sub["generation"], sub["q1_fitness"].clip(lower=1e-10),
                        sub["q3_fitness"].clip(lower=1e-10), color=col, alpha=0.12)
    ax.set_yscale("log"); ax.set_title("Nguyen-7:  f(x) = ln(x+1) + ln(x²+1)", fontsize=11)
    ax.set_xlabel("Generation", fontsize=10); ax.set_ylabel("MSE", fontsize=10)
    ax.grid(True, which="both", alpha=0.25, lw=0.5); ax.legend(fontsize=8, loc="upper right")
    save(fig, "Fig11_nguyen7")

# ---------------------------------------------------------------- Fig 13
def fig13():
    import csv as _csv
    acc = defaultdict(lambda: {"std": [], "eml": []})
    for f in glob.glob(os.path.join(ROOT, "results", "standard_gp", "results_200_100_*.csv")):
        for r in _csv.DictReader(open(f)):
            for k, col in (("std", "Std Nodes"), ("eml", "EML Nodes")):
                if r[col]:
                    try: acc[r["Test ID"]][k].append(int(r[col]))
                    except ValueError: pass
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    for ax, tid, title in ((axes[0], "1.3", r"Test 1.3:  $f(x_1, x_2) = x_1 + x_2$"),
                           (axes[1], "3.2", r"Test 3.2:  $f(x) = \arctan(x)$")):
        for i, (k, col, lbl) in enumerate((("std", "#6fa8dc", "Std-GP"), ("eml", "#e06666", "EML-GP"))):
            v = np.array(acc[tid][k], dtype=float)
            if not len(v): continue
            v = np.clip(v, 1, None)
            ax.violinplot([v], positions=[i], widths=0.75, showextrema=False)
            ax.scatter(np.random.default_rng(0).normal(i, 0.055, len(v)), v,
                       s=13, color=col, edgecolor="0.25", linewidth=0.4, alpha=0.85, zorder=3)
            ax.hlines(np.median(v), i - 0.3, i + 0.3, color="0.15", lw=2, zorder=4)
            ax.annotate(f"n = {len(v)}", (i, 0.02), xycoords=("data", "axes fraction"),
                        ha="center", fontsize=9, color="0.35")
        ax.set_yscale("log"); ax.set_xticks([0, 1]); ax.set_xticklabels(["Std-GP", "EML-GP"])
        ax.set_title(title, fontsize=10); ax.grid(axis="y", alpha=0.25, lw=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Final tree size (nodes, log scale)", fontsize=10)
    save(fig, "Fig13_tree_size_distribution")

if __name__ == "__main__":
    print("Fig 1 …");  fig1()
    print("Fig 2 …");  fig2()
    print("Fig 3 …");  traj("1_1", "Fig03_convergence_exp",        titles={"A": "Test 1.1 — exp(x)"})
    print("Fig 4 …");  traj("1_2", "Fig04_convergence_ln_regimes",
                            dirs=(("A", A_DIR), ("B", B_DIR)),
                            titles={"A": "(a) Regime A: crossover + mutation",
                                    "B": "(b) Regime B: mutation only"})
    print("Fig 5 …");  multi([("1_3", "(a) Test 1.3 — Addition"), ("3_1", "(b) Test 3.1 — sinh(x)")],
                             "Fig05_collapse_addition_sinh")
    print("Fig 6 …");  traj("1_4", "Fig06_convergence_exp_composite", titles={"A": "Test 1.4 — exp(x)·exp(−x²)"})
    print("Fig 7 …");  fig7()
    print("Fig 8 …");  traj("2_1", "Fig08_convergence_sin_cos",    titles={"A": "Test 2.1 — sin(x) + cos(x)"})
    print("Fig 9 …");  traj("3_2", "Fig09_convergence_arctan",     titles={"A": "Test 3.2 — arctan(x)"})
    print("Fig 10 …"); fig10()
    print("Fig 11 …"); fig11()
    print("Fig 12 …"); subprocess.run([sys.executable, os.path.join(HERE, "synthetic", "plot_fig12.py")], check=True)
    print("Fig 13 …"); fig13()
    print(f"\nAll figures -> {OUT}")
