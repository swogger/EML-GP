"""Validation of the benchmark-style rerun phases (P2, P3, P6, P8).

1. Integrity: every expected key present once, no crashes, statuses consistent with logs.
2. Functional-equivalence audit (Section 3.3): each converged run's FINAL_TREE is re-parsed and
   evaluated on a dense grid distinct from the validation sample; equivalent iff
   |pred - f| <= 1e-9 * max(1, |f|) at every point.
3. Bit-identity check: EML runs whose original final error was far from the tolerance should
   reproduce it exactly (the size term never activates for them).

    python3 research/rerun/validate_bench.py P2_bench_ref [P6_native_grid ...]
"""
import csv, math, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research")); sys.path.insert(0, os.path.join(ROOT, "ga-lib"))
from node import Node                    # noqa: E402
from test_suite import TEST_MATRIX       # noqa: E402

UNARY = Node.UNARY_OPS


def parse_formula(s):
    """Inverse of Node.to_formula: '(a op b)', 'op(a)', leaves '1.0' / 'x'."""
    s = s.strip()
    pos = 0

    def expr():
        nonlocal pos
        if s[pos] == "(":
            pos += 1
            left = expr()
            pos += 1                       # space
            j = s.index(" ", pos)
            op = s[pos:j]; pos = j + 1
            right = expr()
            assert s[pos] == ")"; pos += 1
            return Node(op, left, right, True)
        j = pos
        while j < len(s) and s[j] not in "() ":
            j += 1
        tok = s[pos:j]
        if j < len(s) and s[j] == "(" and tok in UNARY:
            pos = j + 1
            child = expr()
            assert s[pos] == ")"; pos += 1
            return Node(tok, child, None, True)
        pos = j
        try:
            return Node(float(tok))
        except ValueError:
            return Node(tok)

    t = expr()
    assert pos == len(s), f"trailing text at {pos}"
    return t


def dense_grid(tid, n=1000):
    # golden-ratio offset: the grid never lands exactly on 0 or other rational points, where
    # protected division (x/0 -> 1) creates removable-singularity artefacts
    lo, hi = TEST_MATRIX[tid]["range"]
    vs = TEST_MATRIX[tid]["vars"]
    if len(vs) == 1:
        return [{vs[0]: lo + (hi - lo) * (i + 0.6180339887) / n} for i in range(n)]
    m = 40
    # different irrational offsets per axis, so the grid never lands on x1 == x2 either
    # (a tree such as x1 + x2 + 0/(x2 - x1) is the target everywhere except on that diagonal)
    pa = [lo + (hi - lo) * (i + 0.6180339887) / m for i in range(m)]
    pb = [lo + (hi - lo) * (i + 0.4142135624) / m for i in range(m)]
    return [{vs[0]: a, vs[1]: b} for a in pa for b in pb]


def equivalent(tree_str, tid):
    tree = parse_formula(tree_str)
    f = TEST_MATRIX[tid]["func"]
    vs = TEST_MATRIX[tid]["vars"]
    worst = 0.0
    for kw in dense_grid(tid):
        y = f(*[kw[v] for v in vs])
        try:
            p = tree.evaluate(**kw)
        except Exception:
            return False, float("inf")
        err = abs(p - y) / max(1.0, abs(y))
        if math.isnan(err) or math.isinf(err):
            return False, float("inf")
        worst = max(worst, err)
    return worst <= 1e-9, worst


def bit_identity(rows):
    """EML/Std runs at the reference cell vs the original trajectory harness (6-decimal log).
    Only runs complete in both versions are comparable. Converged runs are excluded: the
    size term changes when convergence is detected, so differences there are expected."""
    out = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        if r.get("G") != "200" or r.get("P") != "100" or r.get("ops", "table2") != "table2":
            continue
        d = "standard_gp" if r["regime"] == "A" else "mutation_only"
        f = os.path.join(ROOT, "results", d, "convergence_data",
                         f"convergence_{r['test_id']}_{r['algo']}_200_100_{int(r['run']):02d}.csv")
        if not os.path.exists(f):
            continue
        o = list(csv.DictReader(open(f)))
        old_best = float(o[-1]["best_fitness"])
        k = (r["test_id"], r["algo"], r["regime"])
        if r["status"] in ("cpu_limit", "crash") or old_best <= 1e-6 or r["status"] == "converged":
            out[k][2] += 1
            continue
        if int(o[-1]["generation"]) < 199 and r["status"] == "budget":
            out[k][2] += 1                              # old run truncated: not comparable
            continue
        same = round(float(r["final_err"]), 6) == old_best
        out[k][0 if same else 1] += 1
    return out


def main(phases):
    for ph in phases:
        path = os.path.join(ROOT, "results_rerun", f"{ph}.csv")
        rows = list(csv.DictReader(open(path)))
        keys = Counter(r["key"] for r in rows)
        dup = [k for k, c in keys.items() if c > 1]
        st = Counter(r["status"] for r in rows)
        print(f"== {ph}: {len(rows)} rows, {len(keys)} unique keys, duplicates {len(dup)}, statuses {dict(st)}")
        # status/err consistency
        bad = [r["key"] for r in rows if r["status"] == "converged" and not (r["final_err"] and float(r["final_err"]) <= 1e-6)]
        bad += [r["key"] for r in rows if r["status"] != "converged" and r["final_err"] and float(r["final_err"]) <= 1e-6]
        print(f"   status vs final_err inconsistencies: {len(bad)} {bad[:5]}")
        # functional-equivalence audit of converged runs
        aud = defaultdict(lambda: [0, 0])
        worst_fail = []
        for r in rows:
            if r["status"] != "converged":
                continue
            log = os.path.join(ROOT, r["log"])
            tree = next((l[11:].strip() for l in open(log) if l.startswith("FINAL_TREE ")), None)
            ok, w = equivalent(tree, r["test_id"]) if tree else (False, float("nan"))
            k = (r["test_id"], r["algo"], r["regime"], r.get("G"), r.get("P"))
            aud[k][0] += ok; aud[k][1] += 1
            if not ok:
                worst_fail.append((r["key"], f"{w:.2e}"))
        tot_ok = sum(v[0] for v in aud.values()); tot = sum(v[1] for v in aud.values())
        print(f"   functional equivalence: {tot_ok}/{tot} converged runs equivalent (1e-9 relative, dense grid)")
        by_algo = defaultdict(lambda: [0, 0])
        for (tid, algo, reg, G, P), (a, b) in aud.items():
            by_algo[(algo, reg)][0] += a; by_algo[(algo, reg)][1] += b
        print("   by algo/regime:", {f"{k[0]}-{k[1]}": f"{v[0]}/{v[1]}" for k, v in sorted(by_algo.items())})
        if worst_fail:
            print("   non-equivalent converged runs (key, worst rel err):", worst_fail[:12])
        bi = bit_identity(rows)
        if bi:
            same = sum(v[0] for v in bi.values()); diff = sum(v[1] for v in bi.values())
            print(f"   bit-identity vs original (non-converged, complete in both): identical {same}, different {diff}")
            for k, v in sorted(bi.items()):
                if v[1]:
                    print(f"     differs: {k} identical {v[0]} different {v[1]}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["P2_bench_ref"])
