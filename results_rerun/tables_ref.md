## Table 6 (Regime A): convergence, Std-GP vs EML-GP, reference cell, rerun

| ID | Test Case | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | Ln(x) | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.3 | Addition | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | Yes |
| 1.4 | Exp Comp. | 0.47 | 0.00 | +0.47 | <0.001 | <0.001 | Yes |
| 2.1 | Sin+Cos | 0.27 | 0.00 | +0.27 | 0.005 | 0.027 | Yes |
| 3.1 | Sinh(x) | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | Yes |
| 3.2 | Arctan(x) | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | Yes |
| 3.3 | x^x | 0.33 | 0.00 | +0.33 | <0.001 | 0.006 | Yes |
| 3.4 | Sigmoid | 0.23 | 0.00 | +0.23 | 0.011 | 0.053 | No |
| 3.5 | Polynomial | 0.97 | 0.00 | +0.97 | <0.001 | <0.001 | Yes |
| 4.1 | Nested I | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | Nested II | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

Significant: 7 of 12

## Table 6 (Regime B): convergence, Std-GP vs EML-GP, reference cell, rerun

| ID | Test Case | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | Ln(x) | 1.00 | 0.93 | +0.07 | 0.492 | 1.000 | No |
| 1.3 | Addition | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | Yes |
| 1.4 | Exp Comp. | 0.70 | 0.00 | +0.70 | <0.001 | <0.001 | Yes |
| 2.1 | Sin+Cos | 0.47 | 0.00 | +0.47 | <0.001 | <0.001 | Yes |
| 3.1 | Sinh(x) | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | Yes |
| 3.2 | Arctan(x) | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | Yes |
| 3.3 | x^x | 0.47 | 0.00 | +0.47 | <0.001 | <0.001 | Yes |
| 3.4 | Sigmoid | 0.10 | 0.00 | +0.10 | 0.237 | 1.000 | No |
| 3.5 | Polynomial | 0.93 | 0.00 | +0.93 | <0.001 | <0.001 | Yes |
| 4.1 | Nested I | 0.03 | 0.00 | +0.03 | 1.000 | 1.000 | No |
| 4.2 | Nested II | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

Significant: 7 of 12

## Table 7 (Regime A): final tree size over completed runs, reference cell, rerun

| ID | Test | n (Std/EML) | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|---|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 30/30 | 2.0 | 3.0 | 0.637 | 1.000 | +0.067 (negligible) | No |
| 1.2 | Ln(x) | 30/30 | 2.0 | 7.0 | <0.001 | <0.001 | +0.809 (large) | Yes |
| 1.3 | Addition | 30/30 | 6.0 | 1.0 | <0.001 | <0.001 | -0.933 (large) | Yes |
| 1.4 | Exp Comp. | 19/14 | 14.0 | 221.0 | 0.009 | 0.055 | +0.541 (large) | No |
| 2.1 | Sin+Cos | 16/4 | 9.5 | 257.0 | 0.026 | 0.128 | +0.750 (large) | No |
| 3.1 | Sinh(x) | 30/26 | 2.0 | 1.0 | <0.001 | <0.001 | -0.923 (large) | Yes |
| 3.2 | Arctan(x) | 30/9 | 2.0 | 473.0 | <0.001 | <0.001 | +1.000 (large) | Yes |
| 3.3 | x^x | 19/12 | 13.0 | 477.0 | <0.001 | <0.001 | +0.912 (large) | Yes |
| 3.4 | Sigmoid | 18/4 | 116.5 | 404.0 | 0.217 | 0.650 | +0.417 (medium) | No |
| 3.5 | Polynomial | 30/9 | 44.0 | 477.0 | <0.001 | <0.001 | +0.948 (large) | Yes |
| 4.1 | Nested I | 9/7 | 321.0 | 331.0 | 0.672 | 1.000 | +0.143 (small) | No |
| 4.2 | Nested II | 16/5 | 107.5 | 299.0 | 0.109 | 0.437 | +0.500 (large) | No |

Completed share on the eight bloat-prone targets: EML-GP 27%, Std-GP 65%; testable 12, significant 6

## Table 10: EML-GP Regime A vs Regime B, reference cell, rerun (d = B − A; r > 0 means A lower)

| ID | Test | K | Regime A | Regime B | Pairs A lower / B lower | r | p (raw) | p (Holm) | Direction | CPU-limited A/B |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 3 | 0 | 0 | 0 / 0 | – | – | – | identical | 0/0 |
| 1.2 | Ln(x) | 7 | 1.8×10⁻³⁰ | 6.0×10⁻³⁰ | 9 / 0 | +1.00 | 0.004 | 0.035 | A better | 0/0 |
| 1.3 | Addition | 19 | 8.3 | 7.05 | 5 / 23 | −0.87 | <0.001 | <0.001 | B better | 0/0 |
| 1.4 | Exp Comp. | ≤53 | 0.0915 | 0.0522 | 10 / 20 | −0.38 | 0.073 | 0.586 | no significant difference | 16/0 |
| 2.1 | Sin+Cos | ≤637 | 0.222 | 0.288 | 16 / 14 | +0.07 | 0.746 | 1.000 | no significant difference | 26/0 |
| 3.1 | Sinh(x) | ≤81 | 5.7 | 2.92 | 4 / 26 | −0.82 | <0.001 | <0.001 | B better | 4/0 |
| 3.2 | Arctan(x) | ≤355 | 0.406 | 0.688 | 17 / 13 | +0.23 | 0.280 | 1.000 | no significant difference | 21/0 |
| 3.3 | x^x | ≤25 | 1.74 | 2 | 19 / 11 | +0.32 | 0.129 | 0.905 | no significant difference | 18/0 |
| 3.4 | Sigmoid | ≤53 | 0.0192 | 0.0267 | 17 / 13 | +0.01 | 0.984 | 1.000 | no significant difference | 26/0 |
| 3.5 | Polynomial | ≤135 | 333 | 327 | 15 / 15 | +0.06 | 0.792 | 1.000 | no significant difference | 21/2 |
| 4.1 | Nested I | ≤411 | 0.436 | 0.482 | 18 / 12 | +0.09 | 0.685 | 1.000 | no significant difference | 23/0 |
| 4.2 | Nested II | ≤1085 | 0.361 | 0.366 | 14 / 16 | +0.14 | 0.503 | 1.000 | no significant difference | 25/0 |

## Table 10 stability across the grid (paired Wilcoxon, uncorrected)

- Ln(x): expected direction in 9/9 cells; significant (p < 0.05) in that direction in 7/9 cells; G100P100: r=+1.00 p=0.000122, G100P200: r=+0.86 p=0.0469, G100P500: r=+1.00 p=0.0312, G200P100: r=+1.00 p=0.00391, G200P200: r=+0.73 p=0.188, G200P500: r=+1.00 p=0.0312, G500P100: r=+1.00 p=0.0156, G500P200: r=+0.73 p=0.188, G500P500: r=+1.00 p=0.0312
- Addition: expected direction in 9/9 cells; significant (p < 0.05) in that direction in 9/9 cells; G100P100: r=-0.70 p=0.00178, G100P200: r=-0.73 p=0.000342, G100P500: r=-0.66 p=0.00218, G200P100: r=-0.87 p=7.96e-06, G200P200: r=-0.82 p=3.18e-05, G200P500: r=-0.72 p=0.000536, G500P100: r=-0.95 p=4.1e-07, G500P200: r=-0.85 p=3.19e-05, G500P500: r=-0.73 p=0.000479 (incomplete pairs: ['G500P200 n=29', 'G500P500 n=29'])
- Sinh(x): expected direction in 9/9 cells; significant (p < 0.05) in that direction in 6/9 cells; G100P100: r=-0.68 p=0.000809, G100P200: r=-0.57 p=0.00578, G100P500: r=-0.30 p=0.152, G200P100: r=-0.82 p=1.82e-05, G200P200: r=-0.66 p=0.00113, G200P500: r=-0.37 p=0.0767, G500P100: r=-0.87 p=4.42e-06, G500P200: r=-0.70 p=0.00046, G500P500: r=-0.37 p=0.0767

## Table 8: SSC (Uy bounds) vs standard crossover, reference cell, corrected fitness

| ID | Test | Std-GP crossover | Std-GP SSC | EML-GP crossover | EML-GP SSC | EML-GP mutation only | SSC effect on EML-GP | SSC effect on Std-GP |
|---|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 0 | 0 | 0 | 0 | 0 | no change | no change |
| 1.2 | Ln(x) | 0 | 0 | 1.8×10⁻³⁰ | 3.8×10⁻³⁰ | 6.0×10⁻³⁰ | no significant difference (Holm p = 1.00; SSC lower in 0 of 30) | no change |
| 1.3 | Addition | 0 | 0 | 8.3 | 8.3 | 7.05 | no significant difference (Holm p = 1.00; SSC lower in 2 of 30) | no change |
| 2.1 | Sin+Cos | 0.00438 | 3.5×10⁻⁴ | 0.222 | 0.153 | 0.288 | better (Holm p = 0.05; SSC lower in 21 of 30) | no significant difference (Holm p = 0.92; SSC lower in 11 of 30) |
| 3.2 | Arctan(x) | 0 | 0 | 0.406 | 0.197 | 0.688 | no significant difference (Holm p = 0.85; SSC lower in 18 of 30) | no change |
| 3.3 | x^x | 0.0671 | 0.0416 | 1.74 | 1.53 | 2 | no significant difference (Holm p = 1.00; SSC lower in 17 of 30) | no significant difference (Holm p = 0.48; SSC lower in 13 of 30) |

CPU-limited runs (crossover/SSC): eml 1.2: 0/1; eml 1.3: 0/1; eml 2.1: 26/29; eml 3.2: 21/24; eml 3.3: 18/25; std 2.1: 13/7; std 3.3: 11/22

## New supplementary table: original configuration vs rerun at the reference cell (convergence, of 30; censored)

| ID | Test | Algo | Regime | Converged original | Converged rerun | Censored original (wall clock) | Censored rerun (CPU) |
|---|---|---|---|---|---|---|---|
| 1.2 | Ln(x) | EML-GP | A | 23 | 30 | 1 | 0 |
| 1.2 | Ln(x) | EML-GP | B | 6 | 28 | 0 | 0 |
| 1.4 | Exp Comp. | Std-GP | A | 14 | 14 | 12 | 11 |
| 1.4 | Exp Comp. | Std-GP | B | 20 | 21 | 0 | 0 |
| 1.4 | Exp Comp. | EML-GP | A | 0 | 0 | 18 | 16 |
| 2.1 | Sin+Cos | Std-GP | A | 6 | 8 | 13 | 13 |
| 2.1 | Sin+Cos | Std-GP | B | 10 | 14 | 0 | 0 |
| 2.1 | Sin+Cos | EML-GP | A | 0 | 0 | 25 | 26 |
| 3.1 | Sinh(x) | Std-GP | B | 29 | 30 | 0 | 0 |
| 3.2 | Arctan(x) | Std-GP | B | 27 | 30 | 0 | 0 |
| 3.2 | Arctan(x) | EML-GP | A | 0 | 0 | 22 | 21 |
| 3.3 | x^x | Std-GP | B | 13 | 14 | 0 | 0 |
| 3.3 | x^x | EML-GP | A | 0 | 0 | 19 | 18 |
| 3.4 | Sigmoid | Std-GP | A | 5 | 7 | 12 | 12 |
| 3.5 | Polynomial | Std-GP | A | 28 | 29 | 0 | 0 |
| 3.5 | Polynomial | EML-GP | A | 0 | 0 | 20 | 21 |
| 4.1 | Nested I | EML-GP | A | 0 | 0 | 21 | 23 |
| 4.2 | Nested II | Std-GP | A | 0 | 0 | 8 | 14 |
| 4.2 | Nested II | EML-GP | A | 0 | 0 | 21 | 25 |

(rows omitted where both columns agree)

## Reference-cell censoring in the rerun (bloat-prone targets, CPU limit)

- Regime A, eml: 176 of 240
- Regime A, std: 82 of 240
- Regime B, eml: 2 of 240
- Regime B, std: 0 of 240
- crashes: ['2.1|std|A|200|100|28']

