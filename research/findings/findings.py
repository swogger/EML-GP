"""Registry of review findings. Each finding is an executable check.

evidence() returns (status, detail) where status is one of
  CONFIRMED       the error exists in data/code/external source
  REFUTED         the evidence contradicts the finding -> drop it from the list
  UNREPRODUCIBLE  the published value cannot be reproduced by any available method
  FACT            an undocumented implementation fact, verified in code (document it)
present: normalised substrings of the *erroneous* manuscript text (found -> OPEN)
require: normalised substrings a correct fix must contain (missing -> OPEN)
"""
import csv, math, os, re, subprocess
import numpy as np
from scipy.stats import binomtest
from instruments import (ROOT, RES, RERUN, CELLS, TESTS, BLOAT, main_grid, grid_rate, traj, traj_final,
                         rows, synth_orig, synth_rerun, control, read_code, holm, wilcoxon_p, fisher_p,
                         logit_k50, equivalent, odrz, crossref)

F = []


def finding(fid, sev, kind, title, present=(), require=()):
    def deco(fn):
        F.append(dict(id=fid, sev=sev, kind=kind, title=title, evidence=fn, present=present, require=require))
        return fn
    return deco


def ok(cond, yes, no, status="CONFIRMED"):
    return (status, yes) if cond else ("REFUTED", no)


def _patience_min():
    from test_suite import TEST_MATRIX, eml_plateau_mult
    return min(eml_plateau_mult(TEST_MATRIX[t]["std_ops"]) for t in TESTS) * 50


def _p1(path):
    return rows(os.path.join(RERUN, path))


# ============================================================ A. implementation
@finding("A1", "M", "error", "Size term below MSE 1e-5 + convergence checked on training winner blocks convergence",
         present=["doesn't apply parsimony pressure", "does not apply parsimony pressure"])
def _():
    code = read_code("research/deduce_formula.py") + read_code("research/synthetic/eml_synth_core.py")
    has = "mse < 1e-5" in code and "count_nodes(tree) * 0.0001" in code and "f < 1e-5" in code
    o = [r for r in synth_orig() if r["regime"] == "B" and r["K_construction"] == "7"]
    n = [r for r in synth_rerun() if r["regime"] == "B" and r["K_construction"] == "7"]
    ko, kn = sum(r["converged"] == "true" for r in o), sum(r["converged"] == "true" for r in n)
    p = fisher_p(ko, len(o), kn, len(n))
    rec = {(r["target_id"], r["regime"], r["seed"]): r for r in synth_rerun()}
    far = [r for r in synth_orig() if r["converged"] == "false" and float(r["final_nmse"]) > 1e-3]
    same = sum(float(rec[(r["target_id"], r["regime"], r["seed"])]["final_nmse"]) == float(r["final_nmse"]) for r in far)
    return ok(has and p < 1e-6 and same / len(far) > 0.95,
              f"term in code; K=7 Regime B {ko}/{len(o)} -> {kn}/{len(n)} without it (Fisher p={p:.1e}); "
              f"far-from-target failures identical {same}/{len(far)}",
              f"code={has}, p={p:.2g}, identical {same}/{len(far)}")


@finding("A2", "M", "error", "Trajectory harness records no censoring; 170/240 EML runs truncated at the reference cell",
         present=["censors no run at this cell"])
def _():
    pm = _patience_min()
    n = sum(1 for t in BLOAT for r in range(1, 31)
            if traj("A", "eml", t, r=r)[-1][0] < 199 and traj("A", "eml", t, r=r)[-1][1] > 1e-6)
    code = read_code("research/run_convergence_data.py")
    records_status = "returncode" in code or "wait4" in code or "status" in code.split("w.writerow([")[1].split("]")[0]
    return ok(pm > 200 and n >= 100 and not records_status,
              f"EML patience >= {pm} gens (cannot early-stop), yet {n}/240 bloat-target EML runs end before gen 199; harness has no status field",
              f"patience {pm}, truncated {n}")


@finding("A3", "M", "error", "S5 dagger cells / S3 footnote: artefacts of interrupted trajectory files, absent from the main grid",
         present=["truncated by the 600 s cpu-time limit rather than terminated by the algorithm"])
def _():
    e, l = grid_rate("B", "eml", 100, 100, "1.1"), grid_rate("B", "eml", 100, 100, "1.2")
    return ok(abs(e - 1.0) < 1e-9 and abs(l - 0.2) < 1e-9,
              f"main grid Regime B G100/P100: exp {e:.2f}, ln {l:.2f} (S5 prints 0.97†, 0.17†)", f"exp {e}, ln {l}")


@finding("A4", "M", "error", "Depth cap applies to mutation only; known constructions for 9+ targets exceed it (unreachable in Regime B)",
         require=["applied to mutation only"])
def _():
    code = read_code("research/deduce_formula.py")
    import json
    d = json.load(open(os.path.join(RES, "target_k_dump.json")))
    deep = [k for k, v in {**d["targets"], **d["sr_benchmarks"]}.items() if (v.get("depth") or 0) > 9]
    return ok("crossover(parent1, parent2, max_depth=None)" in code and "absolute_max_depth=MAX_DEPTH" in code and len(deep) >= 9,
              f"crossover uncapped, mutation capped at 10 levels; constructions deeper than the cap: {', '.join(deep)}", "code/depths differ")


@finding("A5", "m", "error", "EML-GP gets no point mutation (leaf swaps are not a no-op); Std-GP gets it in both regimes",
         present=["introduces a point mutation operator that regime a does not use"])
def _():
    code = read_code("research/deduce_formula.py"); evo = read_code("ga-lib/evolution.py")
    c = ("use_point_mutate = len(operators) > 1 or not all(op == 'eml'" in code
         and "elif use_point_mutate and evo_rng.random() < 0.05" in code and "Swap terminal/variable" in evo)
    return ok(c, "EML: use_point_mutate=False; point_mutate swaps leaves; Std Regime A applies it with p=0.8*0.05", "code differs")


@finding("A6", "M", "error", "Control grammars contain EML (-, exp, log over C): every target is expressible",
         present=["cease to be exactly expressible", "approximation-only"])
def _():
    from instruments import _parse_formula
    I = "exp((log(((1.0 - 1.0) - 1.0)) / (1.0 + 1.0)))"                        # i, from -, /, +, exp, log and 1
    arctan = f"(({I} / (1.0 + 1.0)) * log((({I} + x) / ({I} - x))))"
    ln = "(exp(1.0) - log((exp((exp(1.0) - log(x))) - log(1.0))))"             # eml(1, eml(eml(1,x),1)) with eml(a,b)=exp(a)-log(b)
    size = lambda f: (lambda t: _count(t))(_parse_formula(f))
    return ok(equivalent(arctan, "3.2") and equivalent(ln, "1.2"),
              f"{size(arctan)}-node arctan and the EML ln tree, written in {{+,-,*,/,exp,log}}, are exact to 1e-9", "not exact")


def _count(t):
    return 1 if not t.is_operator else 1 + _count(t.left) + (_count(t.right) if t.right else 0)


@finding("A7", "M", "error", "SSC selects min-distance pair with no lower bound: most swaps exchange identical subtrees",
         present=["rather than to a specific crossover operator"])
def _():
    import random, run_ssc_baseline as S
    from seeds import SEEDS
    cnt = {"n": 0, "zero": 0}
    real = S.ssc_crossover

    def wrapped(t1, t2, variables, sem, max_nodes=S.MAX_NODES, rng=None, mode="min"):
        n1, n2 = S._all_nodes(t1), S._all_nodes(t2); st = rng.getstate()
        c1 = rng.choices(n1, k=min(S.N_CANDIDATES, len(n1))); c2 = rng.choices(n2, k=min(S.N_CANDIDATES, len(n2)))
        rng.setstate(st)
        v1 = [S._eval_subtree(n, variables, sem) for n, _, _ in c1]; v2 = [S._eval_subtree(n, variables, sem) for n, _, _ in c2]
        cnt["n"] += 1; cnt["zero"] += min(S._subtree_mse(a, b) for a in v1 for b in v2) == 0.0
        return real(t1, t2, variables, sem, max_nodes, rng, mode=mode)
    base = S.run_ssc("1.2", True, SEEDS[1], generations=12)            # control: uninstrumented
    S.ssc_crossover = wrapped
    inst = S.run_ssc("1.2", True, SEEDS[1], generations=12)
    S.ssc_crossover = real
    same = base == inst
    share = cnt["zero"] / max(1, cnt["n"])
    if not same:
        return "INSTRUMENT_FAIL", "instrumentation changed the evolution"
    return ok(share > 0.9, f"{cnt['zero']}/{cnt['n']} SSC events swap zero-distance subtrees (instrumented run identical to control)",
              f"zero-distance share {share:.2f}")


@finding("A8", "m", "error", "Complex-vs-real arithmetic offered as a cost difference, but both arms evaluate over C",
         present=["complex-domain arithmetic is inherently more expensive per node than real-domain arithmetic"])
def _():
    n = read_code("ga-lib/node.py")
    return ok("cmath.log(left_val)" in n and "cmath.sin(left_val)" in n, "Std-GP operators use cmath", "real arithmetic found")


@finding("A9", "m", "error", "'Collapse' = Regime A never improving on the seeded single-variable leaf",
         present=["defaulting to a single leaf node as a safer local optimum"])
def _():
    g = read_code("ga-lib/generator.py"); m = main_grid("A")
    one = [n for t in ("1.3", "3.1") for s, n, _ in m[("eml", 200, 100, t)] if n == "1"]
    csvs = [os.path.join(RES, "standard_gp", f"results_200_100_{r}.csv") for r in range(1, 31)]
    forms = {row["EML Formula"] for f in csvs for row in csv.DictReader(open(f))
             if row["Test ID"] in ("1.3", "3.1") and row["EML Nodes"] == "1"}
    return ok("one depth-1 tree per variable" in g and forms <= {"x", "x1", "x2"},
              f"initialiser seeds variable leaves; all {len(one)} single-node EML results are {sorted(forms)}", f"forms {forms}")


# ============================================================ B. claims contradicted by the data
@finding("B1", "M", "error", "'Every EML-GP convergence is a functional recovery'",
         present=["every eml-gp convergence reported here is a functional recovery",
                  "every eml-gp convergence reported in this paper is therefore a functional recovery"])
def _():
    loose = sum(r["converged"] == "true" and r["exact_hash_match"] != "true" for r in synth_orig())
    p2 = [r for r in _p1("P2_bench_ref.csv") if r["test_id"] == "1.2" and r["algo"] == "eml" and r["regime"] == "B" and r["status"] == "converged"]
    bad = 0
    for r in p2:
        tree = next(l[11:].strip() for l in open(os.path.join(ROOT, r["log"])) if l.startswith("FINAL_TREE "))
        bad += not equivalent(tree, "1.2")
    return ok(loose > 0 and bad > 0, f"original synthetic: {loose} loose convergences; rerun ln Regime B: {bad}/{len(p2)} converged runs not equivalent",
              f"loose {loose}, bad {bad}")


@finding("B2", "M", "error", "'Crossover never destructive' vs Regime B significantly better on addition and sinh",
         present=["not observed to be destructive at any complexity level", "rather than destructive:"])
def _():
    out = []
    for t in ("1.3", "3.1"):
        a = np.array([traj_final("A", "eml", t, r=r) for r in range(1, 31)]); b = np.array([traj_final("B", "eml", t, r=r) for r in range(1, 31)])
        out.append((t, int(np.sum(b < a)), int(np.sum(a < b)), wilcoxon_p(b - a)))
    return ok(all(x[1] > x[2] and x[3] < 0.01 for x in out),
              "; ".join(f"{t}: B lower in {x} vs {y} pairs, p={p:.1e}" for t, x, y, p in out), str(out))


def _disc(data, k):
    by = {}
    for r in data:
        if r["K_construction"] == str(k):
            by.setdefault((r["target_id"], r["seed"]), {})[r["regime"]] = r["converged"] == "true"
    a = sum(v.get("A") and not v.get("B") for v in by.values()); b = sum(v.get("B") and not v.get("A") for v in by.values())
    return a, b


@finding("B3", "m", "error", "Synthetic experiment said to 'agree' with benchmark B-advantage at K=19-81",
         present=["the size-controlled experiment of section 5.4 agrees"])
def _():
    r = [(k, *_disc(synth_orig(), k)) for k in (19, 21)]
    noB = all(not (b > a and binomtest(b, a + b).pvalue < 0.05) for k, a, b in r)
    return ok(noB, "no significant B advantage at K=19/21 in the synthetic data: " + ", ".join(f"K={k} A-only {a} B-only {b}" for k, a, b in r), str(r))


@finding("B4", "m", "error", "'Regime A exceeds Regime B at every level at which anything converges'",
         present=["regime a exceeds regime b at every level at which anything converges"])
def _():
    a, b = _disc(synth_orig(), 21)
    return ok(b > a, f"original data K=21: A-only {a} < B-only {b}", f"A {a} B {b}")


@finding("B5", "m", "error", "Regime B EML-GP budget invariance ('exactly one additional success') fails under the corrected fitness",
         present=["yields exactly one additional eml-gp success"])
def _():
    p = _p1("P6_native_grid.csv") + _p1("P2_bench_ref.csv")
    rate = lambda G: sum(r["status"] == "converged" for r in p if r["test_id"] == "1.2" and r["algo"] == "eml" and r["regime"] == "B"
                         and r["G"] == str(G) and r["P"] == "100") / 30
    return ok(rate(500) - rate(100) > 0.1, f"corrected ln Regime B, P=100: G100 {rate(100):.2f} -> G200 {rate(200):.2f} -> G500 {rate(500):.2f}",
              f"{rate(100)} {rate(500)}")


@finding("B6", "m", "error", "x^x 'ablation beneficial' and sigmoid dilution are not significant",
         present=["removing it raises convergence from 0.33 to 0.43", "adding surplus primitives harms regardless"])
def _():
    c = control()
    k = lambda arm, t, reg: sum(r["status"] == "CONVERGED" for r in c if r["arm"] == arm and r["test_id"] == t and r["regime"] == reg)
    tl = lambda t, reg: round(grid_rate(reg, "std", 200, 100, t) * 30)
    ps = {"x^x A tailored vs ablation": fisher_p(tl("3.3", "A"), 30, k("ABL", "3.3", "A"), 30),
          "x^x B tailored vs ablation": fisher_p(tl("3.3", "B"), 30, k("ABL", "3.3", "B"), 30),
          "sigmoid A tailored vs fixed": fisher_p(tl("3.4", "A"), 30, k("FIX", "3.4", "A"), 30),
          "sigmoid B tailored vs fixed": fisher_p(tl("3.4", "B"), 30, k("FIX", "3.4", "B"), 30)}
    return ok(all(v > 0.05 for v in ps.values()), "; ".join(f"{k_}: p={v:.2f}" for k_, v in ps.items()), str(ps))


@finding("B7", "m", "error", "Tree inflation from surplus primitives appears only in the censored Regime A",
         present=["inflating the median tree from 192 to 936"])
def _():
    c = control()
    med = lambda arm, t, reg: np.median([int(r["nodes"]) for r in c if r["arm"] == arm and r["test_id"] == t and r["regime"] == reg and r["nodes"] not in ("", "None")])
    cens = lambda arm, t, reg: sum(r["status"] == "CPU_TIMEOUT" for r in c if r["arm"] == arm and r["test_id"] == t and r["regime"] == reg)
    return ok(med("ABL", "3.1", "B") > med("FIX", "3.1", "B"),
              f"sinh Regime B (uncensored): ablation {med('ABL','3.1','B')} vs fixed {med('FIX','3.1','B')} nodes; "
              f"Regime A censored ablation {cens('ABL','3.1','A')} vs fixed {cens('FIX','3.1','A')}", "B inflates too")


@finding("B8", "m", "error", "Exponential composite said to favour mutation-only 'at all nine cells'",
         present=["two targets favour mutation alone at all nine cells"])
def _():
    n = sum(np.median([traj_final("B", "std", "1.4", G, P, r) for r in range(1, 31)]) <
            np.median([traj_final("A", "std", "1.4", G, P, r) for r in range(1, 31)]) for G, P in CELLS)
    return ok(n < 9, f"exp composite favours Regime B in {n}/9 cells (others tied)", f"{n}/9")


@finding("B9", "m", "error", "'EML-GP is unaffected by population size'",
         present=["its performance is unaffected by population size"])
def _():
    a, b = grid_rate("A", "eml", 200, 100, "1.2"), grid_rate("A", "eml", 200, 500, "1.2")
    return ok(b - a > 0.1, f"ln EML Regime A G200: P100 {a:.2f} vs P500 {b:.2f}", f"{a} {b}")


@finding("B10", "w", "error", "'8 of 240' censored at G100/P100", present=["8 of 240 runs on the eight bloat-prone targets"])
def _():
    n = sum(s == "TIMEOUT" for t in BLOAT for s, _, _ in main_grid("A")[("eml", 100, 100, t)])
    return ok(n != 8, f"main grid: {n}/240 (Table 1's 4% is right)", f"{n}")


@finding("B11", "w", "error", "'Essentially uncensored up to (G200, P200)' in Regime B",
         present=["essentially uncensored up to (generations: 200, population: 200)"])
def _():
    n = sum(s == "TIMEOUT" for t in BLOAT for s, _, _ in main_grid("B")[("eml", 200, 200, t)])
    return ok(n / 240 > 0.1, f"Regime B G200/P200: {n}/240 = {n/240:.0%}", f"{n}")


@finding("B12", "w", "error", "'Early stopping intervened' (Figs 5, 13) although EML patience never fires",
         present=["before early stopping intervened", "before early stopping intervenes"])
def _():
    pm = _patience_min()
    return ok(pm > 500, f"minimum EML patience = {pm} generations > largest budget 500", f"{pm}")


@finding("B13", "w", "error", "'Essentially no run is censored at any budget' (sinh)",
         present=["essentially no run is censored at any budget"])
def _():
    n = sum(1 for P in (100, 200, 500) for r in range(1, 31)
            if traj("A", "eml", "3.1", 200, P, r)[-1][0] < 199 and traj("A", "eml", "3.1", 200, P, r)[-1][1] > 1e-6)
    return ok(n / 90 > 0.2, f"sinh EML Regime A G200: {n}/90 runs killed before the budget", f"{n}")


@finding("B14", "w", "suggestion", "'which we did not anticipate' beside 'anticipated in Section 1'", present=["which we did not anticipate"])
def _():
    return "SUGGESTION", "wording tension (magnitude vs direction)"


@finding("B15", "w", "error", "Table 5 caption: 0.00 on every target outside the native domain",
         present=["fails to converge (rate = 0.00) on every target outside the native exponential domain"])
def _():
    v = grid_rate("A", "eml", 200, 200, "1.3")
    return ok(v > 0, f"addition EML Regime A G200/P200 = {v:.2f}", f"{v}")


@finding("B16", "w", "error", "Addition and polynomial said to gain only exp and log", present=["addition and the cubic polynomial gain exp and log"])
def _():
    from test_suite import TEST_MATRIX
    gain = set("+,-,*,/,exp,log,sin,cos".split(",")) - set(TEST_MATRIX["1.3"]["std_ops"])
    return ok({"sin", "cos"} <= gain, f"uniform set adds {sorted(gain)} to addition", str(gain))


@finding("B17", "w", "error", "sinh '1.00 to 0.00 under both regimes'", present=["from 1.00 to 0.00 under both regimes"])
def _():
    v = grid_rate("B", "std", 200, 100, "3.1")
    return ok(v < 1.0, f"Std-GP sinh Regime B tailored = {v:.2f}", f"{v}")


@finding("B18", "w", "error", "SSC 'nearly doubles' the x^x error", present=["ssc nearly doubles eml-gp's final error"])
def _():
    s = np.median([float(list(csv.DictReader(open(os.path.join(RES, "ssc", "runs", f"ssc_3.3_eml_ssc_{r:02d}.csv"))))[-1]["best_fitness"]) for r in range(1, 31)])
    x = np.median([traj_final("A", "eml", "3.3", r=r) for r in range(1, 31)])
    return ok(s / x < 1.8, f"x^x: {x:.3f} -> {s:.3f} ({s/x:.2f}x); arctan is the one near 2x", f"{s/x:.2f}")


@finding("B19", "w", "suggestion", "'Universality is necessary but not sufficient'", present=["representational universality is necessary but not sufficient"])
def _():
    return "SUGGESTION", "Std-GP succeeds without universality; universality is not necessary"


@finding("B20", "w", "suggestion", "'The single remaining limitation'", present=["the single remaining limitation"])
def _():
    return "SUGGESTION", "other limitations remain (uniform-set choice, censoring, n=30)"


# ============================================================ C. tables and figures
A1A2 = {("std", 200, 100, "2.1"): 14, ("std", 500, 100, "2.1"): 10, ("std", 100, 200, "4.1"): 529, ("std", 200, 200, "4.1"): 309,
        ("std", 500, 200, "4.1"): 309, ("eml", 200, 100, "1.4"): 243, ("eml", 100, 100, "3.3"): 177, ("eml", 100, 100, "4.1"): 365}


@finding("B21", "m", "error", "Censoring on exp/ln/addition/sinh called none or negligible; main grid shows EML-GP timeouts on addition and sinh at larger budgets (Regime B up to 30/30)",
         present=["no run of either algorithm is censored on exp, ln or addition", "none at all on exp, ln and addition"])
def _():
    out = {}
    for reg in "AB":
        mg = main_grid(reg)
        for t in ("1.1", "1.2", "1.3", "3.1"):
            out[(reg, t)] = max(sum(s[0] == "TIMEOUT" for s in mg[("eml", G, P, t)]) for G, P in CELLS)
        std = sum(s[0] == "TIMEOUT" for t in ("1.1", "1.2", "1.3", "3.1") for G, P in CELLS for s in mg[("std", G, P, t)])
        out[(reg, "std")] = std
    return ok(out[("A", "1.3")] > 0 and out[("B", "1.3")] >= 20 and out[("B", "3.1")] >= 20,
              "max EML-GP timeouts per cell (of 30): " + ", ".join(f"{r} {t}: {v}" for (r, t), v in out.items() if t != "std")
              + f"; Std-GP timeouts on these targets: {out[('A','std')] + out[('B','std')]}", str(out))


@finding("C1", "m", "error", "Appendix A.1/A.2 medians stale")
def _():
    bad = []
    for (algo, G, P, t), printed in A1A2.items():
        v = np.median([int(n) for s, n, _ in main_grid("A")[(algo, G, P, t)] if s != "TIMEOUT" and n])
        if abs(v - printed) > 0.5:
            bad.append(f"{algo} {t} G{G}P{P}: printed {printed}, data {v:g}")
    return ok(len(bad) == 8, "; ".join(bad), f"{len(bad)} of 8 differ")


@finding("C2", "w", "error", "Table 3: 200x200 has 5 testable tree-size comparisons, not 4")
def _():
    m = main_grid("A")
    n = sum(1 for t in TESTS if min(sum(s != "TIMEOUT" for s, _, _ in m[(a, 200, 200, t)]) for a in ("std", "eml")) >= 3)
    return ok(n == 5, f"{n} targets have >= 3 survivors in both arms", f"{n}")


@finding("C3", "m", "error", "Table 9 rates use completed runs as denominator; EML Nguyen-1 A has n=3", present=["0.41 (n=27)"])
def _():
    s = {r["benchmark"]: r for r in csv.DictReader(open(os.path.join(RES, "sr_benchmarks", "sr_benchmark_results_summary.csv")))}
    import glob
    n_std = len(glob.glob(os.path.join(RES, "sr_benchmarks", "runs", "sr_nguyen1_std_a_*.csv")))
    n_eml = len(glob.glob(os.path.join(RES, "sr_benchmarks", "runs", "sr_nguyen1_eml_a_*.csv")))
    v = float(s["nguyen1"]["std_a_convergence"])
    return ok(abs(v - 11 / 27) < 1e-3 and n_std == 27 and n_eml == 3, f"Nguyen-1 Std A rate {v:.3f} = 11/27 (n={n_std}); EML A n={n_eml}", f"{v} {n_std} {n_eml}")


T10 = {"1.2": .92, "1.3": -.64, "1.4": -.33, "2.1": 0.0, "3.1": -.73, "3.2": .13, "3.3": .27, "3.4": .13, "3.5": 0.0, "4.1": .20, "4.2": -.07}


@finding("C4", "m", "error", "Table 10 'rank-biserial r' is the paired sign statistic", present=["with rank-biserial effect size r and holm correction"])
def _():
    from scipy.stats import rankdata
    sign_ok, rb_off = 0, 0
    for t, pr in T10.items():
        a = np.array([traj_final("A", "eml", t, r=r) for r in range(1, 31)]); b = np.array([traj_final("B", "eml", t, r=r) for r in range(1, 31)])
        d = b - a; sign_ok += abs((np.sum(d > 0) - np.sum(d < 0)) / 30 - pr) < 0.006
        nz = d[d != 0]; rk = rankdata(np.abs(nz)); rb = (rk[nz > 0].sum() - rk[nz < 0].sum()) / rk.sum() if len(nz) else 0
        rb_off += abs(rb - pr) > 0.05
    return ok(sign_ok >= 8 and rb_off >= 5, f"sign statistic reproduces {sign_ok}/11 printed r; rank-biserial differs by >0.05 in {rb_off}/11", f"{sign_ok} {rb_off}")


@finding("C5", "w", "error", "Table 16 shows dashes for Regime B values that exist")
def _():
    s, x = grid_rate("B", "std", 200, 100, "3.1"), grid_rate("B", "std", 200, 100, "3.3")
    return ok(True, f"Regime B tailored: sinh {s:.2f}, x^x {x:.2f}", "")


@finding("C6", "w", "error", "Fig 6 caption values", present=["descends to ~10-2 within 25 generations"])
def _():
    g25 = np.median([traj("A", "std", "1.4", r=r)[min(25, len(traj("A", "std", "1.4", r=r)) - 1)][1] for r in range(1, 31)])
    s, e = np.median([traj_final("A", "std", "1.4", r=r) for r in range(1, 31)]), np.median([traj_final("A", "eml", "1.4", r=r) for r in range(1, 31)])
    return ok(g25 < 5e-3 and e / s > 100, f"Std-GP median at gen 25 = {g25:.1e}; final gap EML/Std = {e/s:.0f}x", f"{g25} {e/s}")


@finding("C7", "w", "error", "Fig 9 caption has a literal LaTeX '$\\arctan$'", present=["$\\arctan$"])
def _():
    return "CONFIRMED", "text-only (visible in the submitted PDF)"


@finding("C8", "w", "error", "Tables 6/7 said to correspond to Figure 6 (tree sizes are Figure 7)", present=["correspond to figure 6"])
def _():
    return "CONFIRMED", "text-only"


@finding("C9", "w", "error", "S1 header: Holm across 12, but family is the testable subset", present=["holm-bonferroni corrected across the 12 target functions per cell"])
def _():
    c = read_code("research/eml_gp_stats.py")
    return ok("valid_idx = [i for i, r in enumerate(results) if not np.isnan(r[\"p_value\"])]" in c, "apply_holm corrects over non-NaN tests only", "code differs")


@finding("C10", "w", "error", "S4 (Std-GP table) caption quotes EML-GP censoring", present=["1% against 72% of bloat-prone eml-gp runs"])
def _():
    return "CONFIRMED", "text-only (supplement)"


@finding("C11", "w", "error", "S12 complete-case K50 not reproducible (other columns reproduce)", present=["9.93 [9.02, 10.95]", "10.69 [9.46, 13.46]"])
def _():
    R = os.path.join(RES, "synthetic_dense_k")
    rr = lambda *fs: [r for f in fs for r in csv.DictReader(open(os.path.join(R, f)))]

    def k(rows_, drop):
        x = [r for r in rows_ if r["regime"] == "A" and int(r["K_construction"]) <= 17 and not (drop and r["terminal_state"] == "timeout")]
        return logit_k50([float(r["K_construction"]) for r in x], [r["converged"] == "true" for r in x])
    b8, b32 = rr("budget_pilot_g800.csv", "g800_lowk.csv"), rr("g3200_main.csv", "g3200_lowk.csv")
    ctrl = abs(k(b8, False) - 9.02) < 0.01 and abs(k(b32, False) - 8.97) < 0.01
    if not ctrl:
        return "INSTRUMENT_FAIL", "censored-as-failure column does not reproduce either"
    return ("UNREPRODUCIBLE", f"censored-as-failure reproduces (9.02, 8.97); complete-case gives {k(b8, True):.2f}, {k(b32, True):.2f} vs printed 9.93, 10.69")


@finding("C12", "w", "error", "Table 11 design effect: the published method (one-way ANOVA ICC) reproduces, but '4.4 to 5.7 over K = 7-17' omits K = 13 and 15",
         present=["design effect is approximately 4.4 to 5.7"])
def _():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "research", "rerun"))
    from make_tables_p1 import design_effect, wilson
    orig = list(synth_orig())
    de = design_effect(orig)                                        # one-way ANOVA ICC(1), Regime A
    rr = [r for r in orig if r["regime"] == "A" and int(r["K_construction"]) == 7]
    c, n = sum(r["converged"] == "true" for r in rr), len(rr); ne = n / de[7]
    lo, hi = wilson(c / n * ne, ne)
    reproduces = abs(lo - 0.513) < 0.002 and abs(hi - 0.759) < 0.002
    outside = {k: round(v, 1) for k, v in de.items() if not 4.35 <= v <= 5.75}
    return ok(reproduces and outside, f"ANOVA estimator reproduces the published K = 7 interval [{lo:.3f}, {hi:.3f}]; "
              f"levels outside 4.4-5.7: {outside}", f"reproduces={reproduces}, outside={outside}")


@finding("C13", "w", "error", "A.3 caption promises the full grid, shows one cell", present=["across the 3×3 grid, by target"])
def _():
    return "CONFIRMED", "text-only"


@finding("C14", "w", "error", "Deviance '859' mixes Regime A-only with pooled AUCs", present=["859 deviance points"])
def _():
    import analysis_ncrit_vs_k as M
    tg = {t["target_id"]: t for t in csv.DictReader(open(os.path.join(RES, "synthetic_dense_k", "synthetic_targets.csv")))}
    data = [{"target_id": r["target_id"], "regime": r["regime"], "y": float(r["converged"] == "true"), "K": float(r["K_construction"]),
             "n_crit": float(tg[r["target_id"]]["n_crit"])} for r in synth_orig()]
    dev = lambda rr, cols: M.fit(rr, cols, groups=[r["target_id"] for r in rr])
    import io, contextlib
    def deviance(rr, cols):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.show("x", dev(rr, cols))
        return float(re.search(r"dev=\s*([0-9.]+)", buf.getvalue()).group(1))
    pooled = deviance(data, ["n_crit"]) - deviance(data, ["K"])
    A = [r for r in data if r["regime"] == "A"]; a_only = deviance(A, ["n_crit"]) - deviance(A, ["K"])
    return ok(abs(pooled - 859) > 100 and abs(a_only - 859) < 2, f"pooled difference {pooled:.0f}; Regime A-only {a_only:.0f}", f"{pooled} {a_only}")


# ============================================================ D. attribution and references
@finding("D1", "m", "error", "sin/cos/tan/arctan K values attributed to [9] are not in [9]", present=["corresponding figures in odrzywołek [9] for sin", "k-complexities as published in [9] versus"])
def _():
    text = odrz("main") + " " + odrz("SI")
    ctrl = "x+y 27 19" in odrz("main") and "448 attempts" in odrz("main")
    absent = not re.search(r"\b(471|373|443|915)\b", text)
    w = read_code("eml-skill/eml-skill/skills/_shared/eml_core/witnesses.py")
    if not ctrl:
        return "INSTRUMENT_FAIL", "cached [9] text lacks known strings"
    return ok(absent and "K=471" in w and "closure" in w, "471/373/443/915 absent from [9] main+SI; present in eml-skill witnesses (closure-page provenance)", "found in [9]")


@finding("D2", "m", "error", "[9] reports sqrt direct-search K=43 < 59 used; 'reciprocal is the sole case' is false", present=["the reciprocal is the sole case"])
def _():
    t = odrz("main")
    from test_suite import EML_K
    return ok("139 43" in t and EML_K["sqrt"] == 59, "[9] Table 4: sqrt compiler 139, direct 43; this study uses 59", "not found")


@finding("D3", "m", "error", "eml-skill witness library not cited", require=["eml-skill"])
def _():
    return ok(os.path.exists(os.path.join(ROOT, "eml-skill", "CITATION.cff")), "eml-skill (Golan, MIT) CITATION.cff requests citation", "no CITATION.cff")


@finding("D4", "M", "error", "[9]'s gradient-based recovery-by-depth results uncited (corroborating evidence)", require=["448"])
def _():
    t = odrz("main")
    return ok("100% of runs at depth 2" in t and "448 attempts" in t, "[9]: blind recovery 100% (d=2), ~25% (d=3-4), <1% (d=5), 0/448 (d=6)", "not found")


@finding("D5", "m", "error", "Reference [6] merges two Langdon & Poli papers", present=["pp. 13-22. https://doi.org/10.1007/bfb0055926"])
def _():
    m = crossref("10.1007/BFb0055926")
    return ok(m["page"] == "37-48" and "mutation" in m["title"].lower(), f"DOI -> '{m['title']}', pp. {m['page']}", str(m))


@finding("D6", "m", "error", "Reference [14] DOI resolves to another paper", present=["978-3-540-24855-2_7 "])
def _():
    wrong, right = crossref("10.1007/978-3-540-24855-2_7"), crossref("10.1007/978-3-540-24855-2_76")
    return ok("fitness clouds" not in wrong["title"].lower() and "fitness clouds" in right["title"].lower(),
              f"_7 -> '{wrong['title']}'; _76 -> '{right['title']}'", "")


@finding("D7", "w", "suggestion", "Addition K=19 'exhaustive search': cite [9]'s direct search")
def _():
    return ok("x+y 27 19" in odrz("main"), "[9] Table 4: x+y compiler 27, direct search 19", "not found", status="SUGGESTION")


# ============================================================ E. reproducibility
@finding("E1", "m", "error", "No repository code for Table 10 / Table 8 / S10 tests, §5.3.3 bootstrap, design effect")
def _():
    hits = subprocess.run(["grep", "-rl", "wilcoxon\\|bootstrap", os.path.join(ROOT, "research")], capture_output=True, text=True).stdout.splitlines()
    hits = [h for h in hits if "/rerun/" not in h and "/findings/" not in h]
    return ok(not hits, "no committed script computes these (only new rerun/audit scripts do)", str(hits))


@finding("E2", "m", "error", "Control and budget-sweep data untracked in git (data statement untrue)", present=["results/fixed_set_control/"])
def _():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "results/fixed_set_control", "research/run_control_fixedset.py",
                          "results/synthetic_dense_k/g3200_main.csv"], capture_output=True, text=True).stdout.strip()
    return ok(out == "", "none of these files is tracked", out)


@finding("E3", "w", "error", "Trajectory logs rounded to 6 decimals ('8.5e-6' is a midpoint of rounded values)")
def _():
    return ok("Best Error: {best_val_error:.6f}" in read_code("research/deduce_formula.py"), "per-generation log uses :.6f", "format differs")


# ============================================================ F. undocumented facts (for Table B.2 / methods)
FACTS = [
    ("F1a", "Training sample (75 points) is re-drawn every generation", "research/deduce_formula.py", "for gen in range(args.generations):\n        batch = ["),
    ("F1b", "Elite = best-so-far individual by validation error", "research/deduce_formula.py", "new_pop = [best_tree.copy()]  # elitism"),
    ("F1c", "Convergence is checked only on the training-fitness winner", "research/deduce_formula.py", "gen_val_err   = validation_error(gen_best_tree)"),
    ("F1d", "Initial population: ramped depths 2..10 (full depth-10 EML trees exceed the node cap)", "ga-lib/generator.py", "depths = list(range(2, max_depth + 1))"),
    ("F1e", "Mutation subtree depth = round(sqrt(10)) = 3, not <= 2", "research/deduce_formula.py", "mut_depth   = max(2, round(math.sqrt(MAX_DEPTH)))"),
    ("F1f", "Protected division x/0 -> 1", "ga-lib/node.py", "left_val / right_val if right_val != 0j else 1.0 + 0j"),
    ("F1g", "Tree-size tests require >= 3 surviving runs per group", "research/eml_gp_stats.py", "if len(std_clean) < 3 or len(eml_clean) < 3:"),
    ("F1h", "Synthetic validation: N=100 points, the same draw for every target", "research/synthetic/run_synthetic.py", "C.validation_sample(20260721 + 1)"),
    ("F1i", "SSC similarity uses the modulus of complex outputs", "research/run_ssc_baseline.py", "out.append(abs(v))"),
    ("F1j", "Synthetic timeout measured in wall-clock seconds (legacy runs)", "research/synthetic/eml_synth_core.py", "(time.time() - t0)) > timeout_seconds"),
    ("F1k", "Synthetic patience fixed at 600 generations regardless of budget", "research/synthetic/eml_synth_core.py", "PLATEAU_GENS     = max(50, GENERATIONS // 10) * PLATEAU_MULT"),
]
for fid, title, path, needle in FACTS:
    def make(path=path, needle=needle):
        def _():
            return ok(needle in read_code(path), f"{path}: `{needle.strip()[:70]}`", "pattern not found", status="FACT")
        return _
    F.append(dict(id=fid, sev="w", kind="fact", title=title, evidence=make(), present=(), require=()))


# ============================================================ S. setup caveats of the reruns (found 26 Sep)
@finding("S1", "M", "error", "Uy-bounded SSC (P4) rarely finds a pair inside (1e-4, 0.4) for EML: it falls back to random crossover")
def _():
    import run_ssc_baseline as S
    from seeds import SEEDS
    real = S._uy_pick; n = {"t": 0, "a": 0}

    def counted(*args):
        r = real(*args); n["t"] += 1; n["a"] += r is not None; return r
    S._uy_pick = counted
    try:
        S.run_ssc("3.2", True, SEEDS[1], generations=8, size_penalty=False, ssc_mode="uy")
    finally:
        S._uy_pick = real
    share = n["a"] / max(1, n["t"])
    return ok(share < 0.15, f"EML arctan: window hit in {n['a']}/{n['t']} SSC events ({share:.0%}); the rest are random crossover", f"{share:.0%}")


@finding("S2", "m", "fact", "Harnesses run at about the same speed on uninterrupted pairs; every large gap is an original file ending in the same second as >=2 others (burst). Compare censoring only within the rerun")
def _():
    # Relies on original file mtimes (intact in this working copy; a fresh clone would reset them).
    d = {"A": "standard_gp", "B": "mutation_only"}
    stamp = lambda reg, fn: int(os.path.getmtime(os.path.join(RES, d[reg], "convergence_data", fn)))
    burst, clean = [], []
    for r in rows(os.path.join(RERUN, "P2_bench_ref.csv")):
        if r["status"] != "cpu_limit" or r["algo"] != "eml":
            continue
        fn = f"convergence_{r['test_id']}_eml_200_100_{int(r['run']):02d}.csv"
        cdir = os.path.join(RES, d[r["regime"]], "convergence_data")
        peers = sum(stamp(r["regime"], f) == stamp(r["regime"], fn) for f in os.listdir(cdir) if f.endswith(".csv"))
        ratio = int(r["last_gen"]) / traj(r["regime"], "eml", r["test_id"], r=int(r["run"]))[-1][0]
        (burst if peers >= 3 else clean).append(ratio)
    clean_med = float(np.median(clean)) if clean else float("nan")
    rng = lambda v: f"{min(v):.2f}-{max(v):.2f}" if v else "none"
    return ok(clean and 0.9 < clean_med < 1.1,
              f"rerun/original last-generation ratio for CPU-killed EML runs: uninterrupted originals n={len(clean)} "
              f"median {clean_med:.2f} (range {rng(clean)}); burst-ended originals n={len(burst)} range {rng(burst)}",
              f"uninterrupted median {clean_med:.2f} (n={len(clean)})", status="FACT")


@finding("S3", "w", "fact", "EML point mutation (leaf swaps) has no significant effect on synthetic convergence (P5 vs P1, Holm)")
def _():
    p1 = {(r["target_id"], r["regime"], r["seed"]): r for r in synth_rerun()}
    cells = {}
    for r in rows(os.path.join(RERUN, "P5_synth_pointmut.csv")):
        c = cells.setdefault((r["K_construction"], r["regime"]), [0, 0, 0])
        c[0] += 1; c[1] += p1[(r["target_id"], r["regime"], r["seed"])]["converged"] == "true"; c[2] += r["converged"] == "true"
    ps = [fisher_p(a, n, b, n) for n, a, b in cells.values()]
    return ok(min(holm(ps)) > 0.05, f"8 K×regime cells, smallest Holm-adjusted p = {min(holm(ps)):.2f}", f"{min(holm(ps)):.3f}", status="FACT")
