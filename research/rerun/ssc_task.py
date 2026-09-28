"""One SSC run (Regime A, reference cell) -> GEN lines + one RESULT JSON line."""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import run_ssc_baseline as S  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--test_id", required=True)
ap.add_argument("--algo", choices=["std", "eml"], required=True)
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--mode", choices=["uy", "min"], default="uy")
ap.add_argument("--generations", type=int, default=S.GENERATIONS)
ap.add_argument("--no_size_penalty", action="store_true")
a = ap.parse_args()

rec = S.run_ssc(a.test_id, a.algo == "eml", a.seed, generations=a.generations,
                size_penalty=not a.no_size_penalty, ssc_mode=a.mode, trace=True)
last_gen, best = rec[-1]
conv = best <= 1e-6
stop = "converged" if conv else ("budget" if last_gen == a.generations - 1 else "plateau")
print("RESULT " + json.dumps({"final_err": repr(best), "last_gen": last_gen,
                               "converged": conv, "stop_reason": stop}), flush=True)
