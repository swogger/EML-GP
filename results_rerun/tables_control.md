## Table 15: convergence by operator set, both regimes (reference cell, rerun)

| ID | Test | Set change (8-primitive vs Table 2) | 8-prim A | 8-prim B | 6-prim A | 6-prim B | Table 2 set A | Table 2 set B | EML-GP A | EML-GP B |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | + sin, cos | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 1.2 | Ln(x) | + sin, cos | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.93 |
| 1.3 | Addition | + exp, log, sin, cos | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| 1.4 | Exp Comp. | + sin, cos | 0.17 | 0.23 | 0.47 | 0.70 | 0.47 | 0.70 | 0.00 | 0.00 |
| 2.1 | Sin+Cos | − tan; + exp, log | 0.33 | 0.17 | 0.00 | 0.00 | 0.27 | 0.47 | 0.00 | 0.00 |
| 3.1 | Sinh(x) | − sinh, cosh, tanh; + sin, cos | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| 3.2 | Arctan(x) | − tan, arctan | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| 3.3 | x^x | − sqrt; + sin, cos | 0.13 | 0.30 | 0.43 | 0.53 | 0.33 | 0.47 | 0.00 | 0.00 |
| 3.4 | Sigmoid | + sin, cos | 0.03 | 0.00 | 0.23 | 0.10 | 0.23 | 0.10 | 0.00 | 0.00 |
| 3.5 | Polynomial | + exp, log, sin, cos | 0.10 | 0.10 | 0.17 | 0.20 | 0.97 | 0.93 | 0.00 | 0.00 |
| 4.1 | Nested I | − tan | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 |
| 4.2 | Nested II | − tan | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| | Mean | | 0.314 | 0.317 | 0.358 | 0.378 | 0.606 | 0.642 | 0.167 | 0.161 |

- Regime A: tailored − EML gap 0.439; share removed by the uniform FIX8 set 0.66 (remaining Std-GP advantage 0.147)
- Regime A: tailored − EML gap 0.439; share removed by the uniform ABL6 set 0.56 (remaining Std-GP advantage 0.192)
- Regime B: tailored − EML gap 0.481; share removed by the uniform FIX8 set 0.68 (remaining Std-GP advantage 0.156)
- Regime B: tailored − EML gap 0.481; share removed by the uniform ABL6 set 0.55 (remaining Std-GP advantage 0.217)

## Table 16: decomposition, seed-matched tests (McNemar on convergence; Wilcoxon on final error; Holm within column)

### Replacing the Table 2 set by the 6-primitive set, Regime A (tailored → ABL6)

| ID | Test | conv tailored → ABL6 | only tailored / only ABL6 | McNemar Holm p | error: tailored lower / ABL6 lower | Wilcoxon Holm p | CPU-limited tailored/ABL6 |
|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.2 | Ln(x) | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.3 | Addition | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.4 | Exp Comp. | 0.47 → 0.47 | 0 / 0 | – | 7 / 1 | 0.08 | 11/12 |
| 2.1 | Sin+Cos | 0.27 → 0.00 | 8 / 0 | **0.016** | 30 / 0 | **0.000** | 13/15 |
| 3.1 | Sinh(x) | 1.00 → 0.00 | 30 / 0 | **0.000** | 30 / 0 | **0.000** | 0/7 |
| 3.2 | Arctan(x) | 1.00 → 0.00 | 30 / 0 | **0.000** | 30 / 0 | **0.000** | 0/15 |
| 3.3 | x^x | 0.33 → 0.43 | 5 / 8 | 0.58 | 9 / 16 | 0.60 | 11/7 |
| 3.4 | Sigmoid | 0.23 → 0.23 | 0 / 0 | – | 0 / 3 | 0.60 | 12/12 |
| 3.5 | Polynomial | 0.97 → 0.17 | 24 / 0 | **0.000** | 25 / 0 | **0.000** | 0/11 |
| 4.1 | Nested I | 0.00 → 0.00 | 0 / 0 | – | 19 / 11 | 0.60 | 21/17 |
| 4.2 | Nested II | 0.00 → 0.00 | 0 / 0 | – | 20 / 10 | 0.22 | 14/7 |

### Replacing the Table 2 set by the 6-primitive set, Regime B (tailored → ABL6)

| ID | Test | conv tailored → ABL6 | only tailored / only ABL6 | McNemar Holm p | error: tailored lower / ABL6 lower | Wilcoxon Holm p | CPU-limited tailored/ABL6 |
|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.2 | Ln(x) | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.3 | Addition | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.4 | Exp Comp. | 0.70 → 0.70 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 2.1 | Sin+Cos | 0.47 → 0.00 | 14 / 0 | **0.000** | 30 / 0 | **0.000** | 0/0 |
| 3.1 | Sinh(x) | 1.00 → 0.00 | 30 / 0 | **0.000** | 30 / 0 | **0.000** | 0/0 |
| 3.2 | Arctan(x) | 1.00 → 0.00 | 30 / 0 | **0.000** | 30 / 0 | **0.000** | 0/0 |
| 3.3 | x^x | 0.47 → 0.53 | 6 / 8 | 1.00 | 8 / 14 | 0.67 | 0/0 |
| 3.4 | Sigmoid | 0.10 → 0.10 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 3.5 | Polynomial | 0.93 → 0.20 | 23 / 1 | **0.000** | 24 / 1 | **0.000** | 0/1 |
| 4.1 | Nested I | 0.03 → 0.00 | 1 / 0 | 1.00 | 19 / 11 | 0.67 | 0/0 |
| 4.2 | Nested II | 0.00 → 0.00 | 0 / 0 | – | 10 / 20 | 0.67 | 0/0 |

### Adding sin and cos to the 6-primitive set, Regime A (ABL6 → FIX8)

| ID | Test | conv ABL6 → FIX8 | only ABL6 / only FIX8 | McNemar Holm p | error: ABL6 lower / FIX8 lower | Wilcoxon Holm p | CPU-limited ABL6/FIX8 |
|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.2 | Ln(x) | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.3 | Addition | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.4 | Exp Comp. | 0.47 → 0.17 | 11 / 2 | 0.09 | 20 / 7 | 1.00 | 12/20 |
| 2.1 | Sin+Cos | 0.00 → 0.33 | 0 / 10 | **0.010** | 3 / 27 | **0.000** | 15/11 |
| 3.1 | Sinh(x) | 0.00 → 0.00 | 0 / 0 | – | 6 / 24 | **0.002** | 7/20 |
| 3.2 | Arctan(x) | 0.00 → 0.00 | 0 / 0 | – | 14 / 16 | 1.00 | 15/16 |
| 3.3 | x^x | 0.43 → 0.13 | 13 / 4 | 0.15 | 20 / 10 | 1.00 | 7/14 |
| 3.4 | Sigmoid | 0.23 → 0.03 | 7 / 1 | 0.15 | 24 / 6 | **0.012** | 12/21 |
| 3.5 | Polynomial | 0.17 → 0.10 | 5 / 3 | 0.73 | 16 / 14 | 1.00 | 11/11 |
| 4.1 | Nested I | 0.00 → 0.00 | 0 / 0 | – | 10 / 20 | 1.00 | 17/23 |
| 4.2 | Nested II | 0.00 → 0.00 | 0 / 0 | – | 10 / 20 | 0.21 | 7/13 |

### Adding sin and cos to the 6-primitive set, Regime B (ABL6 → FIX8)

| ID | Test | conv ABL6 → FIX8 | only ABL6 / only FIX8 | McNemar Holm p | error: ABL6 lower / FIX8 lower | Wilcoxon Holm p | CPU-limited ABL6/FIX8 |
|---|---|---|---|---|---|---|---|
| 1.1 | Exp(x) | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.2 | Ln(x) | 1.00 → 1.00 | 0 / 0 | – | 0 / 0 | – | 0/0 |
| 1.3 | Addition | 1.00 → 0.97 | 1 / 0 | 1.00 | 2 / 0 | 1.00 | 0/0 |
| 1.4 | Exp Comp. | 0.70 → 0.23 | 16 / 2 | **0.009** | 21 / 4 | **0.043** | 0/0 |
| 2.1 | Sin+Cos | 0.00 → 0.17 | 0 / 5 | 0.38 | 1 / 29 | **0.000** | 0/0 |
| 3.1 | Sinh(x) | 0.00 → 0.00 | 0 / 0 | – | 5 / 25 | **0.001** | 0/0 |
| 3.2 | Arctan(x) | 0.00 → 0.00 | 0 / 0 | – | 14 / 16 | 1.00 | 0/0 |
| 3.3 | x^x | 0.53 → 0.30 | 10 / 3 | 0.46 | 18 / 6 | 0.39 | 0/0 |
| 3.4 | Sigmoid | 0.10 → 0.00 | 3 / 0 | 1.00 | 24 / 6 | **0.018** | 0/0 |
| 3.5 | Polynomial | 0.20 → 0.10 | 5 / 2 | 1.00 | 18 / 11 | 0.52 | 1/0 |
| 4.1 | Nested I | 0.00 → 0.03 | 0 / 1 | 1.00 | 8 / 22 | 0.38 | 0/0 |
| 4.2 | Nested II | 0.00 → 0.00 | 0 / 0 | – | 9 / 21 | 0.52 | 0/0 |

## Table S9: 8-primitive control, per target

| Test | Regime | Conv. | Median error (completed runs) | Median nodes (completed) | CPU-limited | Table 2 set conv. |
|---|---|---|---|---|---|---|
| Exp(x) | A | 1.00 | 0 | 2 | 0 | 1.00 |
| Exp(x) | B | 1.00 | 0 | 3 | 0 | 1.00 |
| Ln(x) | A | 1.00 | 0 | 2 | 0 | 1.00 |
| Ln(x) | B | 1.00 | 0 | 4 | 0 | 1.00 |
| Addition | A | 1.00 | 0 | 4 | 0 | 1.00 |
| Addition | B | 0.97 | 6.2×10⁻³⁵ | 7 | 0 | 1.00 |
| Exp Comp. | A | 0.17 | 9.2×10⁻⁴ | 17.5 | 20 | 0.47 |
| Exp Comp. | B | 0.23 | 0.0103 | 36 | 0 | 0.70 |
| Sin+Cos | A | 0.33 | 1.2×10⁻³² | 9 | 11 | 0.27 |
| Sin+Cos | B | 0.17 | 0.044 | 28.5 | 0 | 0.47 |
| Sinh(x) | A | 0.00 | 0.162 | 454 | 20 | 1.00 |
| Sinh(x) | B | 0.00 | 0.0642 | 48.5 | 0 | 1.00 |
| Arctan(x) | A | 0.00 | 0.112 | 306 | 16 | 1.00 |
| Arctan(x) | B | 0.00 | 0.0959 | 55 | 0 | 1.00 |
| x^x | A | 0.13 | 0.0108 | 288 | 14 | 0.33 |
| x^x | B | 0.30 | 0.0482 | 51.5 | 0 | 0.47 |
| Sigmoid | A | 0.03 | 0.0039 | 421 | 21 | 0.23 |
| Sigmoid | B | 0.00 | 0.0078 | 47 | 0 | 0.10 |
| Polynomial | A | 0.10 | 358 | 216 | 11 | 0.97 |
| Polynomial | B | 0.10 | 306 | 65 | 0 | 0.93 |
| Nested I | A | 0.00 | 0.0392 | 482 | 23 | 0.00 |
| Nested I | B | 0.03 | 0.0234 | 49 | 0 | 0.03 |
| Nested II | A | 0.00 | 0.352 | 180 | 13 | 0.00 |
| Nested II | B | 0.00 | 0.289 | 33.5 | 0 | 0.00 |

## Table S11: 6-primitive control, per target

| Test | Regime | Conv. | Median error (completed runs) | Median nodes (completed) | CPU-limited | Table 2 set conv. |
|---|---|---|---|---|---|---|
| Exp(x) | A | 1.00 | 0 | 2 | 0 | 1.00 |
| Exp(x) | B | 1.00 | 0 | 3 | 0 | 1.00 |
| Ln(x) | A | 1.00 | 0 | 2 | 0 | 1.00 |
| Ln(x) | B | 1.00 | 0 | 4 | 0 | 1.00 |
| Addition | A | 1.00 | 0 | 5 | 0 | 1.00 |
| Addition | B | 1.00 | 2.2×10⁻³⁴ | 10.5 | 0 | 1.00 |
| Exp Comp. | A | 0.47 | 6.1×10⁻³³ | 13.5 | 12 | 0.47 |
| Exp Comp. | B | 0.70 | 6.4×10⁻³³ | 24.5 | 0 | 0.70 |
| Sin+Cos | A | 0.00 | 0.117 | 483 | 15 | 0.27 |
| Sin+Cos | B | 0.00 | 0.126 | 78.5 | 0 | 0.47 |
| Sinh(x) | A | 0.00 | 0.671 | 30 | 7 | 1.00 |
| Sinh(x) | B | 0.00 | 0.227 | 57.5 | 0 | 1.00 |
| Arctan(x) | A | 0.00 | 0.176 | 223 | 15 | 1.00 |
| Arctan(x) | B | 0.00 | 0.0881 | 77 | 0 | 1.00 |
| x^x | A | 0.43 | 3.9×10⁻³⁰ | 13 | 7 | 0.33 |
| x^x | B | 0.53 | 1.1×10⁻¹³ | 29 | 0 | 0.47 |
| Sigmoid | A | 0.23 | 3.3×10⁻⁴ | 116.5 | 12 | 0.23 |
| Sigmoid | B | 0.10 | 0.00213 | 61.5 | 0 | 0.10 |
| Polynomial | A | 0.17 | 282 | 265 | 11 | 0.97 |
| Polynomial | B | 0.20 | 217 | 99 | 1 | 0.93 |
| Nested I | A | 0.00 | 0.327 | 76 | 17 | 0.00 |
| Nested I | B | 0.00 | 0.115 | 74 | 0 | 0.03 |
| Nested II | A | 0.00 | 0.378 | 121 | 7 | 0.00 |
| Nested II | B | 0.00 | 0.312 | 91 | 0 | 0.00 |

