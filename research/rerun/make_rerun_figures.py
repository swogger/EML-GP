"""Figures 3-10 and 13 from the corrected-fitness rerun at the reference cell, drawn with the
published plotting code (research/make_all_figures.py, research/plot_convergence.py).

    python3 research/rerun/make_rerun_figures.py

1. Converts the rerun logs (results_rerun/logs/P2_bench_ref, P4_ssc_uy) into trajectory CSVs in the
   original format, under results_rerun/trajectories/.
2. Draws the figures into figures/ with the suffix _rerun, and prints the numbers the captions quote.
"""
import csv, glob, os, re, sys
from collections import defaultdict
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research"))
import make_all_figures as MF          # noqa: E402
from plot_convergence import load_runs, aggregate_panel   # noqa: E402
import matplotlib.pyplot as plt        # noqa: E402

RR = os.path.join(ROOT, "results_rerun")
TR = os.path.join(RR, "trajectories")
GEN = re.compile(r"^GEN (\d+) BEST (\S+)(?: VAL \S+ NODES \d+ MEDIAN (\d+))?")


def convert():
    rows = list(csv.DictReader(open(os.path.join(RR, "P2_bench_ref.csv"))))
    for reg in "AB":
        os.makedirs(os.path.join(TR, reg), exist_ok=True)
    for r in rows:
        out = os.path.join(TR, r["regime"], f"convergence_{r['test_id']}_{r['algo']}_200_100_{int(r['run']):02d}.csv")
        with open(out, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["generation", "best_fitness", "median_tree_size"])
            last = None
            for line in open(os.path.join(ROOT, r["log"])):
                m = GEN.match(line)
                if m:
                    last = [m.group(1), m.group(2), m.group(3) or ""]
                    w.writerow(last)
            # a run that stopped by converging or on a plateau keeps its best-so-far to the end of the budget;
            # runs stopped by the CPU limit or a crash are left as they are (as in the original harness)
            if last and r["status"] in ("converged", "plateau") and int(last[0]) < int(r["G"]) - 1:
                w.writerow([int(r["G"]) - 1, last[1], last[2]])
    os.makedirs(os.path.join(TR, "ssc"), exist_ok=True)
    for r in csv.DictReader(open(os.path.join(RR, "P4_ssc_uy.csv"))):
        log = os.path.join(RR, "logs", "P4_ssc_uy", f"{r['test_id']}_{r['algo']}_{int(r['run']):02d}.log")
        with open(os.path.join(TR, "ssc", f"ssc_{r['test_id']}_{r['algo']}_ssc_{int(r['run']):02d}.csv"), "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["generation", "best_fitness"])
            for line in open(log):
                m = GEN.match(line)
                if m:
                    w.writerow([m.group(1), m.group(2)])


def save_suffix(fig, name):
    MF.save.__wrapped__(fig, name + "_rerun") if hasattr(MF.save, "__wrapped__") else _orig_save(fig, name + "_rerun")


_orig_save = MF.save


def p2_nodes():
    acc = defaultdict(lambda: {"std": [], "eml": []})
    for r in csv.DictReader(open(os.path.join(RR, "P2_bench_ref.csv"))):
        if r["regime"] == "A" and r["status"] in ("converged", "budget", "plateau"):
            acc[r["test_id"]][r["algo"]].append(int(r["final_nodes"]))
    return acc


def fig7():
    names = {"1.1": "Exp(x)", "1.2": "Ln(x)", "1.3": "Addition", "1.4": "Exp Comp.", "2.1": "Sin+Cos",
             "3.1": "Sinh(x)", "3.2": "Arctan(x)", "3.3": "x$^x$", "3.4": "Sigmoid",
             "3.5": "Polynomial", "4.1": "Nested I", "4.2": "Nested II"}
    acc = p2_nodes(); order = list(names)
    s = [np.median(acc[t]["std"]) if acc[t]["std"] else 0 for t in order]
    e = [np.median(acc[t]["eml"]) if acc[t]["eml"] else 0 for t in order]
    x = np.arange(len(order)); w = 0.38
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x - w/2, s, w, label="Std-GP nodes", color="#6fa8dc", edgecolor="0.3", lw=0.6)
    ax.bar(x + w/2, e, w, label="EML-GP nodes", color="#b03030", edgecolor="0.3", lw=0.6)
    ax.set_yscale("log"); ax.set_ylim(0.8, 1200)
    ax.set_xticks(x); ax.set_xticklabels([names[t] for t in order], rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Median final tree size (nodes, log scale)", fontsize=10)
    ax.legend(fontsize=9, frameon=True); ax.grid(axis="y", alpha=0.25, lw=0.6); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    _orig_save(fig, "Fig07_median_tree_size_rerun")
    print("Fig 7 medians (Std/EML):", {t: (s[i], e[i]) for i, t in enumerate(order)})


def fig10():
    def med(pat):
        cur = [pd.read_csv(f).set_index("generation")["best_fitness"] for f in sorted(glob.glob(pat))]
        cur = [c for c in cur if len(c)]
        if not cur:
            return None
        mx = max(c.index.max() for c in cur)
        al = pd.concat([c.reindex(np.arange(mx + 1)).ffill() for c in cur], axis=1)
        return al.index, al.median(axis=1).clip(lower=1e-10), len(cur)
    series = [
        (os.path.join(TR, "A", "convergence_1.2_std_200_100_*.csv"), "Std-GP (standard xover)", "#1f77b4", "-"),
        (os.path.join(TR, "A", "convergence_1.2_eml_200_100_*.csv"), "EML-GP (standard xover)", "#d62728", ":"),
        (os.path.join(TR, "B", "convergence_1.2_eml_200_100_*.csv"), "EML-GP (mutation only)", "#d62728", "-."),
        (os.path.join(TR, "ssc", "ssc_1.2_std_ssc_*.csv"), "Std-GP + SSC", "#1f77b4", "--"),
        (os.path.join(TR, "ssc", "ssc_1.2_eml_ssc_*.csv"), "EML-GP + SSC", "#d62728", "--"),
    ]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for pat, lbl, col, ls in series:
        r = med(pat)
        blue = col == "#1f77b4"
        ax.plot(r[0], r[1], ls, color=col, lw=2.2 if blue else 1.6, zorder=3 if blue else 2, label=f"{lbl} (n={r[2]})")
        g0 = next((int(g) for g, v in zip(r[0], r[1]) if v <= 1e-10), None)
        print(f"Fig 10 {lbl}: median reaches the plot floor (<=1e-10) at generation {g0}; final median {r[1].iloc[-1]:.3g}")
    ax.set_yscale("log"); ax.set_xlabel("Generation", fontsize=10); ax.set_ylabel("MSE", fontsize=10)
    ax.grid(True, which="both", alpha=0.25, lw=0.5); ax.legend(fontsize=8, loc="upper right")
    _orig_save(fig, "Fig10_ssc_ln_rerun")


def fig13():
    acc = p2_nodes()
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    for ax, tid, title in ((axes[0], "1.3", r"Test 1.3:  $f(x_1, x_2) = x_1 + x_2$"),
                           (axes[1], "3.2", r"Test 3.2:  $f(x) = \arctan(x)$")):
        for i, (k, col) in enumerate((("std", "#6fa8dc"), ("eml", "#e06666"))):
            v = np.clip(np.array(acc[tid][k], dtype=float), 1, None)
            ax.violinplot([v], positions=[i], widths=0.75, showextrema=False)
            ax.scatter(np.random.default_rng(0).normal(i, 0.055, len(v)), v, s=13, color=col,
                       edgecolor="0.25", linewidth=0.4, alpha=0.85, zorder=3)
            ax.hlines(np.median(v), i - 0.3, i + 0.3, color="0.15", lw=2, zorder=4)
            ax.annotate(f"n = {len(v)}", (i, 0.02), xycoords=("data", "axes fraction"), ha="center", fontsize=9, color="0.35")
            print(f"Fig 13 {tid} {k}: n={len(v)} median={np.median(v):g} min={v.min():g} max={v.max():g} "
                  f"single-node={int((v == 1).sum())}")
        ax.set_yscale("log"); ax.set_xticks([0, 1]); ax.set_xticklabels(["Std-GP", "EML-GP"])
        ax.set_title(title, fontsize=10); ax.grid(axis="y", alpha=0.25, lw=0.6); ax.set_axisbelow(True)
    axes[0].set_ylabel("Final tree size (nodes, log scale)", fontsize=10)
    _orig_save(fig, "Fig13_tree_size_distribution_rerun")


def caption_numbers():
    runs = {reg: load_runs(os.path.join(TR, reg))[(200, 100)] for reg in "AB"}
    for tid, gens in (("1_1", (0, 5)), ("1_2", (5, 7, 10, 25, 199)), ("1_3", (0, 199)), ("3_1", (0, 199)),
                      ("1_4", (0, 25, 199)), ("2_1", (0, 25, 199)), ("3_2", (0, 25, 199))):
        for reg in "AB":
            for algo in ("std", "eml"):
                a = aggregate_panel(runs[reg], tid, algo)
                vals = {g: float(a["median"].iloc[min(g, len(a["median"]) - 1)]) for g in gens}
                first0 = next((int(g) for g, v in zip(a["generations"], a["median"]) if v <= 1e-6), None)
                print(f"{tid} {reg} {algo}: n={a['n_runs']} median at {vals}; median first <= 1e-6 at gen {first0}; "
                      f"IQR at end [{float(a['q1'].iloc[-1]):.3g}, {float(a['q3'].iloc[-1]):.3g}]")


if __name__ == "__main__":
    convert()
    MF.A_DIR, MF.B_DIR = os.path.join(TR, "A"), os.path.join(TR, "B")
    MF._cache.clear()
    # traj() binds its default data folder at definition time, so every call passes dirs explicitly
    MF.save = lambda fig, name: _orig_save(fig, name + "_rerun")
    MF.traj("1_1", "Fig03_convergence_exp", dirs=(("A", MF.A_DIR),), titles={"A": "Test 1.1 — exp(x)"})
    MF.traj("1_2", "Fig04_convergence_ln_regimes", dirs=(("A", MF.A_DIR), ("B", MF.B_DIR)),
            titles={"A": "(a) Regime A: crossover + mutation", "B": "(b) Regime B: mutation only"})
    MF.multi([("1_3", "(a) Test 1.3 — Addition"), ("3_1", "(b) Test 3.1 — sinh(x)")], "Fig05_collapse_addition_sinh")
    MF.traj("1_4", "Fig06_convergence_exp_composite", dirs=(("A", MF.A_DIR),), titles={"A": "Test 1.4 — exp(x)·exp(−x²)"})
    MF.traj("2_1", "Fig08_convergence_sin_cos", dirs=(("A", MF.A_DIR),), titles={"A": "Test 2.1 — sin(x) + cos(x)"})
    MF.traj("3_2", "Fig09_convergence_arctan", dirs=(("A", MF.A_DIR),), titles={"A": "Test 3.2 — arctan(x)"})
    fig7(); fig10(); fig13()
    caption_numbers()

def fig11():
    """Nguyen-7 trajectories from the benchmark rerun (P10), in the published Fig 11 style. All 30 runs per arm;
    runs stopped by convergence or plateau keep their best-so-far to the end, runs stopped by the CPU limit end early."""
    rows = list(csv.DictReader(open(os.path.join(RR, "P10_sr_bench.csv"))))
    out = []
    for algo in ("std", "eml"):
        for reg in "AB":
            series = []
            for r in rows:
                if r["bench"] != "nguyen7" or r["algo"] != algo or r["regime"] != reg:
                    continue
                log = os.path.join(RR, "logs", "P10_sr_bench", f"nguyen7_{algo}_{reg}_{int(r['run']):02d}.log")
                g = {int(m.group(1)): float(m.group(2)) for m in (GEN.match(l) for l in open(log)) if m}
                if not g:
                    continue
                s = pd.Series(g)
                if r["status"] in ("converged", "plateau", "budget"):
                    s = s.reindex(np.arange(200)).ffill()
                series.append(s)
            mx = max(x.index.max() for x in series)
            al = pd.concat([x.reindex(np.arange(mx + 1)).ffill() for x in series], axis=1)
            for gen in al.index:
                v = al.loc[gen]
                out.append(dict(test_id="nguyen7", generations_config=200, pop_size=100, algorithm=f"{algo}_{reg.lower()}",
                                generation=int(gen), median_fitness=v.median(), q1_fitness=v.quantile(0.25),
                                q3_fitness=v.quantile(0.75), n_runs=len(series)))
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(RR, "sr_benchmark_convergence_data_rerun.csv"), index=False)
    style = {"std_a": ("Std-GP (crossover+mut)", "#1f77b4", "-"), "eml_a": ("EML-GP (crossover+mut)", "#d62728", ":"),
             "std_b": ("Std-GP (mutation only)", "#1f77b4", "--"), "eml_b": ("EML-GP (mutation only)", "#d62728", "--")}
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for algo, (lbl, col, ls) in style.items():
        sub = df[df["algorithm"] == algo].sort_values("generation")
        ax.plot(sub["generation"], sub["median_fitness"].clip(lower=1e-10), ls, color=col, lw=1.6,
                label=f"{lbl} (n={int(sub['n_runs'].iloc[0])})")
        ax.fill_between(sub["generation"], sub["q1_fitness"].clip(lower=1e-10), sub["q3_fitness"].clip(lower=1e-10),
                        color=col, alpha=0.12)
        print(f"Fig 11 {algo}: final median {sub['median_fitness'].iloc[-1]:.3g}")
    ax.set_yscale("log"); ax.set_title("Nguyen-7:  f(x) = ln(x+1) + ln(x²+1)", fontsize=11)
    ax.set_xlabel("Generation", fontsize=10); ax.set_ylabel("MSE", fontsize=10)
    ax.grid(True, which="both", alpha=0.25, lw=0.5); ax.legend(fontsize=8, loc="upper right")
    _orig_save(fig, "Fig11_nguyen7_rerun")


if __name__ == "__main__" and "--fig11" in sys.argv:
    fig11()
