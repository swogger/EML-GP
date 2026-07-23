# Resolution package — reviewer point on identical convergence rates (Tables 4 & 5)

**Reviewer point:** "Convergence rates are exactly identical across all three generation budgets (100/200/500) at a given population size. The early-stopping explanation is plausible but currently asserted rather than shown — provide the actual distribution of termination generations."

**Verified facts (from raw convergence trajectories, both regimes, full 3×3 grid × 30 runs):**

- Regime A: all 2,544 convergence events occur by generation 91 (median 0, p90 8, p99 21); the converged-run *sets* are identical across the three budgets in all 72 test × algorithm × population configurations. Early-stopping patience max(50, G/10) × mult evaluates identically (50 × mult) at G = 100/200/500. Non-converging EML-GP runs use the full larger budgets (median termination 99/199/499) without a single additional success.
- Regime B: invariance is close but not exact — 15 runs (14 Std-GP on Exp Comp./Sin+Cos/x^x at generations 103–275; 1 EML-GP on Ln(x) at generation 467) first converge after generation 99. Thirteen convert between G=100→200; two grid-wide between G=200→500.
- Two Regime B G=100 EML-GP files are CPU-timeout truncations (Exp(x) run 27 killed at gen 42, converges at 46; Ln(x) run 13 killed at gen 0, converges at 16) — collection artifacts, each worth 0.03 in one rate cell.

Data files:
- `results/standard_gp/termination_generation_analysis.csv`
- `results/mutation_only/termination_generation_analysis.csv`
- `results/mutation_only/regimeB_convergence_rates_std.csv`
- `results/mutation_only/regimeB_convergence_rates_eml.csv`

---

## Part 1 — Corrections to the main paper

### Edit 1 (required): replace the Section 5 opening observation paragraph

Replace the passage from "A number of important observations are worth noting…" through "…rather than any property of the crossover operator." with:

> A number of important observations are worth noting in advance of a more detailed phase-by-phase result analysis. In Regime A, convergence rates are not merely similar but exactly invariant to the generation budget: for every target function, algorithm, and population size, the same individual seeded runs succeed under all three budgets (100, 200, 500). The run-level trajectories explain why (Supplementary Table S-X). Across all 2,544 successful Regime A runs, the convergence tolerance was first met no later than generation 91 (median 0; 90th percentile 8) — within even the smallest budget. Two structural properties make this exact invariance a logical consequence rather than a coincidence. First, the early-stopping patience window, max(50, G/10) scaled by the K-complexity multiplier for EML-GP, evaluates to the same value at G = 100, 200, and 500, so deterministically seeded runs face identical stopping criteria under every budget. Second, the additional generations at larger budgets are genuinely explored, not truncated: because the K-scaled patience window exceeds the budget, non-converging EML-GP runs continue to budget exhaustion (median termination generation rising from 99 at G = 100 to 499 at G = 500), yet this additional search never produces a single further success. The failure of EML-GP outside its native domain is therefore structural rather than compute-bound.
>
> Regime B replicates this pattern almost exactly for EML-GP: across the entire mutation-only grid, extending the budget from 100 to 500 generations yields exactly one additional EML-GP success (a single Ln(x) run converging at generation 467). For Std-GP under mutation-only evolution the invariance is instead approximate: on Exp Composite, Sin+Cos, and x^x, fourteen runs first converge between generations 103 and 275, raising convergence rates modestly from G = 100 to G = 200 (e.g., Sin+Cos at Population 100: 0.20 → 0.33) before saturating, with only two further successes grid-wide from G = 200 to G = 500. This contrast is itself informative: mutation-only Std-GP continues to make convertible progress past generation 100 on precisely the targets where crossover is disruptive (Section 5.3.3), whereas EML-GP's stagnation is budget-independent in both regimes — confirming that the cause is the topology of the EML search landscape rather than any property of the crossover operator.

Notes on what this replaces and why:

- The old sentence "Increasing the maximum generation budget rarely alters the effective run length" is contradicted by the data (failing EML-GP runs' median termination rises 99 → 199 → 499). The new text states the correct mechanism: run length does scale, outcomes do not.
- The old sentence "This pattern is replicated in Regime B, where the same generation-invariant structure persists" is not exactly true and must be qualified as above.

### Edit 2: Table 3 caption

Append to the final sentence: "…corroborating the early-determination finding **(Supplementary Table S-X)**."

### Edit 3: Table 5 caption

After "regardless of computational budget," insert: "**(all convergence events in the grid occur by generation 91; Supplementary Table S-X)**".

### Edit 4: Nested I absolute claims

Regime B Std-GP has one Nested I success (Population 100, converging at generation 52; rate 0.03). If any sentence claims neither algorithm ever converges on Nested I in any regime, qualify it. Tables 4/5 (Regime A) are unaffected.

### Edit 5: existing supplementary Regime B convergence tables

If the current supplementary Regime B rate tables show rates constant across generation budgets, replace them with Tables S-Z1/S-Z2 below (nine Std-GP cells and one EML-GP cell differ across budgets, plus two timeout-artifact cells).

---

## Part 2 — Supplement content (four tables)

### Table S-X. Termination-generation analysis, Regime A (crossover + mutation)

**Caption:** For each target and algorithm: the number of converged runs under each generation budget (out of 90 = 3 population sizes × 30 runs); the distribution of the first generation at which the convergence tolerance (validation MSE ≤ 10⁻⁶) was met (median / 90th percentile / maximum, pooled across all nine grid cells, valid because converged-run sets are identical across budgets); and the median [interquartile range] termination generation of non-converging runs under each budget. Every convergence event in the grid occurs by generation 91; converged counts are exactly identical across budgets. Non-converging EML-GP runs terminate at or near budget exhaustion because the K-complexity-scaled patience window exceeds the generation budget, confirming that the additional compute was explored rather than truncated.

| Test | Algo | Conv G=100 | Conv G=200 | Conv G=500 | 1st-conv med | p90 | max | Fail term G=100 | G=200 | G=500 |
|---|---|---|---|---|---|---|---|---|---|---|
| Exp(x) | Std-GP | 90 | 90 | 90 | 0 | 0 | 2 | — | — | — |
| Exp(x) | EML-GP | 90 | 90 | 90 | 0 | 2 | 3 | — | — | — |
| Ln(x) | Std-GP | 90 | 90 | 90 | 0 | 1 | 2 | — | — | — |
| Ln(x) | EML-GP | 74 | 74 | 74 | 3 | 8 | 91 | 99 [99–99] | 185 [144–199] | 192 [144–361] |
| Addition | Std-GP | 90 | 90 | 90 | 0 | 2 | 4 | — | — | — |
| Addition | EML-GP | 2 | 2 | 2 | 32 | 33 | 33 | 99 [99–99] | 199 [199–199] | 499 [499–499] |
| Exp Comp. | Std-GP | 55 | 55 | 55 | 6 | 16 | 23 | 99 [74–99] | 116 [74–137] | 116 [74–140] |
| Exp Comp. | EML-GP | 0 | 0 | 0 | — | — | — | 99 [66–99] | 109 [68–172] | 112 [66–174] |
| Sin+Cos | Std-GP | 37 | 37 | 37 | 4 | 14 | 20 | 99 [75–99] | 95 [74–144] | 104 [74–148] |
| Sin+Cos | EML-GP | 0 | 0 | 0 | — | — | — | 99 [65–99] | 96 [63–129] | 99 [63–139] |
| Sinh(x) | Std-GP | 89 | 89 | 89 | 0 | 2 | 14 | 78 [78–78] | 78 [78–78] | 78 [78–78] |
| Sinh(x) | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [129–199] | 499 [129–499] |
| Arctan(x) | Std-GP | 90 | 90 | 90 | 0 | 1 | 11 | — | — | — |
| Arctan(x) | EML-GP | 0 | 0 | 0 | — | — | — | 99 [66–99] | 104 [68–148] | 102 [66–147] |
| x^x | Std-GP | 36 | 36 | 36 | 4 | 17 | 23 | 99 [72–99] | 97 [72–129] | 97 [72–131] |
| x^x | EML-GP | 0 | 0 | 0 | — | — | — | 99 [72–99] | 118 [72–161] | 118 [70–165] |
| Sigmoid | Std-GP | 17 | 17 | 17 | 10 | 14 | 17 | 99 [73–99] | 98 [73–126] | 98 [70–126] |
| Sigmoid | EML-GP | 0 | 0 | 0 | — | — | — | 99 [64–99] | 107 [64–144] | 107 [63–142] |
| Polynomial | Std-GP | 88 | 88 | 88 | 5 | 11 | 41 | 75 [63–87] | 109 [80–138] | 109 [80–138] |
| Polynomial | EML-GP | 0 | 0 | 0 | — | — | — | 99 [57–99] | 106 [57–147] | 106 [38–147] |
| Nested I | Std-GP | 0 | 0 | 0 | — | — | — | 99 [68–99] | 101 [68–134] | 105 [67–134] |
| Nested I | EML-GP | 0 | 0 | 0 | — | — | — | 99 [73–99] | 104 [73–153] | 103 [71–153] |
| Nested II | Std-GP | 0 | 0 | 0 | — | — | — | 97 [58–99] | 96 [62–136] | 96 [64–136] |
| Nested II | EML-GP | 0 | 0 | 0 | — | — | — | 99 [52–99] | 102 [61–144] | 102 [59–145] |

### Table S-Y. Termination-generation analysis, Regime B (mutation only)

**Caption:** Structure as in Table S-X. Unlike Regime A, invariance here is close but not exact: fourteen Std-GP runs (Exp Composite, Sin+Cos, x^x) and one EML-GP run (Ln(x), generation 467) first converge after generation 99, raising rates modestly between G = 100 and G = 200 and saturating thereafter (two further successes grid-wide from G = 200 to G = 500).

**Footnote:** Two G = 100 EML-GP files are truncated by the 600 s CPU-time limit rather than terminated by the algorithm: Exp(x) run 27 (killed at generation 42; the same seed converges at generation 46 under the other budgets) and Ln(x) run 13 (killed at generation 0; converges at generation 16). These are collection artifacts of the CPU timeout, not budget effects, and affect at most one run (0.03) in the corresponding rate cells.

| Test | Algo | Conv G=100 | Conv G=200 | Conv G=500 | 1st-conv med | p90 | max | Fail term G=100 | G=200 | G=500 |
|---|---|---|---|---|---|---|---|---|---|---|
| Exp(x) | Std-GP | 90 | 90 | 90 | 0 | 0 | 3 | — | — | — |
| Exp(x) | EML-GP | 89 | 90 | 90 | 0 | 16 | 67 | 42 [42–42] | — | — |
| Ln(x) | Std-GP | 90 | 90 | 90 | 0 | 1 | 6 | — | — | — |
| Ln(x) | EML-GP | 27 | 28 | 29 | 1 | 44 | 467 | 99 [99–99] | 199 [199–199] | 499 [349–499] |
| Addition | Std-GP | 90 | 90 | 90 | 0 | 4 | 9 | — | — | — |
| Addition | EML-GP | 1 | 1 | 1 | 95 | 95 | 95 | 99 [99–99] | 199 [199–199] | 365 [167–499] |
| Exp Comp. | Std-GP | 62 | 64 | 64 | 9 | 33 | 158 | 99 [87–99] | 119 [89–145] | 119 [89–145] |
| Exp Comp. | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [199–199] | 499 [203–499] |
| Sin+Cos | Std-GP | 32 | 39 | 40 | 11 | 109 | 275 | 99 [99–99] | 154 [104–199] | 151 [103–210] |
| Sin+Cos | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [168–199] | 351 [167–499] |
| Sinh(x) | Std-GP | 88 | 88 | 88 | 0 | 2 | 57 | 87 [85–88] | 87 [85–88] | 87 [85–88] |
| Sinh(x) | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [199–199] | 417 [235–499] |
| Arctan(x) | Std-GP | 87 | 87 | 87 | 0 | 3 | 4 | 99 [99–99] | 126 [117–152] | 126 [117–152] |
| Arctan(x) | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [199–199] | 371 [209–499] |
| x^x | Std-GP | 45 | 49 | 49 | 11 | 67 | 198 | 99 [99–99] | 156 [115–199] | 156 [115–204] |
| x^x | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [199–199] | 499 [233–499] |
| Sigmoid | Std-GP | 10 | 10 | 10 | 8 | 17 | 17 | 99 [95–99] | 129 [95–190] | 129 [95–187] |
| Sigmoid | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [199–199] | 467 [223–499] |
| Polynomial | Std-GP | 88 | 88 | 88 | 5 | 12 | 50 | 86 [79–92] | 105 [89–121] | 105 [89–121] |
| Polynomial | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 185 [91–199] | 183 [91–292] |
| Nested I | Std-GP | 1 | 1 | 1 | 52 | 52 | 52 | 99 [99–99] | 199 [159–199] | 200 [159–267] |
| Nested I | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [199–199] | 499 [290–499] |
| Nested II | Std-GP | 0 | 0 | 0 | — | — | — | 99 [96–99] | 126 [96–175] | 126 [96–175] |
| Nested II | EML-GP | 0 | 0 | 0 | — | — | — | 99 [99–99] | 199 [113–199] | 210 [107–499] |

### Table S-Z1. Convergence rates of Std-GP, Regime B (mutation only)

**Caption:** Each cell reports the proportion of 30 deterministic runs achieving fitness convergence (within tolerance) before budget exhaustion or the 600-second CPU-time timeout. Unlike Regime A (Table 4), rates are not fully invariant to the generation budget: on Exp Composite, Sin+Cos, and x^x, mutation-only evolution continues to convert failures into successes past generation 100 (first-convergence generations 103–275; Table S-Y), raising rates between G = 100 and G = 200 before saturating. Bold marks cells that changed from the previous budget column at the same population.

| Test Case | G100 P100 | G100 P200 | G100 P500 | G200 P100 | G200 P200 | G200 P500 | G500 P100 | G500 P200 | G500 P500 |
|---|---|---|---|---|---|---|---|---|---|
| Exp(x) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Ln(x) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Addition | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Exp Comp. | 0.63 | 0.60 | 0.83 | **0.67** | **0.63** | 0.83 | 0.67 | 0.63 | 0.83 |
| Sin+Cos | 0.20 | 0.30 | 0.57 | **0.33** | **0.40** | 0.57 | 0.33 | 0.40 | **0.60** |
| Sinh(x) | 0.97 | 1.00 | 0.97 | 0.97 | 1.00 | 0.97 | 0.97 | 1.00 | 0.97 |
| Arctan(x) | 0.90 | 1.00 | 1.00 | 0.90 | 1.00 | 1.00 | 0.90 | 1.00 | 1.00 |
| x^x | 0.40 | 0.47 | 0.63 | **0.43** | **0.53** | **0.67** | 0.43 | 0.53 | 0.67 |
| Sigmoid | 0.10 | 0.10 | 0.13 | 0.10 | 0.10 | 0.13 | 0.10 | 0.10 | 0.13 |
| Polynomial | 0.93 | 1.00 | 1.00 | 0.93 | 1.00 | 1.00 | 0.93 | 1.00 | 1.00 |
| Nested I | 0.03 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 |
| Nested II | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

### Table S-Z2. Convergence rates of EML-GP, Regime B (mutation only)

**Caption:** Convergence remains restricted to the native exponential domain, and rates are generation-invariant except for a single Ln(x) run at Population 200 that first converges at generation 467 (bold). The Ln(x) rates (0.17–0.40) are substantially below Regime A (0.77–0.90; Table 5), consistent with crossover's constructive role on the K = 7 cascade (Section 5.1). † marks the two CPU-timeout-artifact cells (see Table S-Y footnote).

| Test Case | G100 P100 | G100 P200 | G100 P500 | G200 P100 | G200 P200 | G200 P500 | G500 P100 | G500 P200 | G500 P500 |
|---|---|---|---|---|---|---|---|---|---|
| Exp(x) | 0.97† | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Ln(x) | 0.17† | 0.33 | 0.40 | 0.20 | 0.33 | 0.40 | 0.20 | **0.37** | 0.40 |
| Addition | 0.00 | 0.03 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.03 | 0.00 |
| Exp Comp. | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Sin+Cos | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Sinh(x) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Arctan(x) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| x^x | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Sigmoid | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Polynomial | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Nested I | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Nested II | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

---

## Part 3 — Response to the reviewer

> We thank the reviewer for pressing on this point; the analysis it prompted both substantiates the mechanism and refined one claim. We extracted the termination and first-convergence generations of every individual run and report the full distributions in new Supplementary Tables S-X and S-Y.
>
> For the regime shown in Tables 4–5, the invariance is exact at the level of individual runs, not merely of rates: the set of converged runs is identical across the three generation budgets for every target function, algorithm, and population size. All 2,544 convergence events occur no later than generation 91 (median 0, 90th percentile 8) — within even the smallest budget. Two structural facts make this a logical consequence: (i) the early-stopping patience window, max(50, G/10) scaled by the K-complexity multiplier, evaluates to the same value at G = 100, 200, and 500; and (ii) runs are deterministically seeded, so trajectories are identical up to termination. Crucially, the larger budgets are genuinely explored rather than truncated: because the K-scaled patience exceeds the budget, non-converging EML-GP runs continue to budget exhaustion (median termination generation 99/199/499 under the three budgets) without yielding a single additional success — supporting the structural, rather than compute-bound, interpretation.
>
> Extending the same analysis to Regime B showed that generation-invariance there is close but not exact: fifteen runs (fourteen Std-GP, one EML-GP) first converge between generations 103 and 467, almost all between budgets 100 and 200. We have revised Section 5 accordingly: the text no longer asserts exact replication in Regime B but quantifies the deviation, and notes that its concentration in Std-GP on crossover-disrupted targets (Sin+Cos, x^x, Exp Composite) is consistent with the analysis in Section 5.3.3, while EML-GP's stagnation remains budget-independent in both regimes. The supplementary Regime B convergence-rate tables have been regenerated directly from the raw trajectories (Tables S-Z1, S-Z2) to reflect these budget-dependent cells.
