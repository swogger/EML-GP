# Supplementary Material S1: Per-Cell Statistical Analyses

Statistical comparisons of EML-GP vs Std-GP at every grid cell. Convergence rates compared with Fisher's exact test; tree sizes with Mann-Whitney U test. All p-values Holm-Bonferroni corrected across the 12 target functions per cell (α = 0.05).

## Summary across all cells

| Grid cell (Gens × Pop) | n per algorithm per test | Convergence: significant tests | Tree size: significant tests |
|---------------|--------------------------|-------------------------|----------------------|
| 100×100 | 30 | 6/12 | 6/12 |
| 100×200 | 30 | 7/12 | 7/12 |
| 100×500 | 30 | 8/12 | 4/12 |
| 200×100 | 30 | 6/12 | 8/12 |
| 200×200 | 30 | 7/12 | 4/12 |
| 200×500 | 30 | 8/12 | 4/12 |
| 500×100 | 30 | 6/12 | 4/12 |
| 500×200 | 30 | 7/12 | 4/12 |
| 500×500 | 30 | 8/12 | 4/12 |

## Grid cell 100×100

**Table X. Convergence-rate comparison (100×100 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.77 | +0.23 | 0.011 | 0.063 | No |
| 1.3 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.47 | 0.00 | +0.47 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.20 | 0.00 | +0.20 | 0.024 | 0.119 | No |
| 3.1 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.33 | 0.00 | +0.33 | <0.001 | 0.006 | **Yes** |
| 3.4 | 0.17 | 0.00 | +0.17 | 0.052 | 0.209 | No |
| 3.5 | 0.93 | 0.00 | +0.93 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (100×100 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | 0.004 | 0.025 | +0.400 (medium) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +0.844 (large) | **Yes** |
| 1.3 | 5.0 | 1.0 | <0.001 | <0.001 | -0.933 (large) | **Yes** |
| 1.4 | 35.0 | 207.0 | 0.323 | 1.000 | +0.152 (small) | No |
| 2.1 | 174.5 | 386.0 | 0.133 | 0.666 | +0.231 (small) | No |
| 3.1 | 2.0 | 1.0 | <0.001 | <0.001 | -0.667 (large) | **Yes** |
| 3.2 | 2.0 | 415.0 | <0.001 | <0.001 | +1.000 (large) | **Yes** |
| 3.3 | 58.5 | 192.0 | 0.072 | 0.434 | +0.271 (small) | No |
| 3.4 | 285.5 | 369.0 | 0.517 | 1.000 | +0.101 (small) | No |
| 3.5 | 43.0 | 305.0 | <0.001 | <0.001 | +0.938 (large) | **Yes** |
| 4.1 | 471.5 | 379.0 | 0.271 | 1.000 | -0.167 (small) | No |
| 4.2 | 328.0 | 260.0 | 0.912 | 1.000 | -0.018 (negligible) | No |

## Grid cell 100×200

**Table X. Convergence-rate comparison (100×200 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.80 | +0.20 | 0.024 | 0.119 | No |
| 1.3 | 1.00 | 0.03 | +0.97 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.60 | 0.00 | +0.60 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.43 | 0.00 | +0.43 | <0.001 | <0.001 | **Yes** |
| 3.1 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.37 | 0.00 | +0.37 | <0.001 | 0.002 | **Yes** |
| 3.4 | 0.13 | 0.00 | +0.13 | 0.112 | 0.450 | No |
| 3.5 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (100×200 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | <0.001 | <0.001 | +0.800 (large) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +0.944 (large) | **Yes** |
| 1.3 | 3.0 | 1.0 | <0.001 | <0.001 | -0.933 (large) | **Yes** |
| 1.4 | 19.0 | 299.0 | 0.199 | 0.856 | +0.218 (small) | No |
| 2.1 | 26.0 | 459.0 | <0.001 | 0.004 | +0.615 (large) | **Yes** |
| 3.1 | 2.0 | 1.0 | <0.001 | 0.002 | -0.517 (large) | **Yes** |
| 3.2 | 2.0 | 476.0 | <0.001 | <0.001 | +1.000 (large) | **Yes** |
| 3.3 | 135.0 | 271.0 | 0.171 | 0.856 | +0.225 (small) | No |
| 3.4 | 391.0 | 425.0 | 0.266 | 0.856 | +0.200 (small) | No |
| 3.5 | 33.0 | 303.0 | <0.001 | <0.001 | +0.997 (large) | **Yes** |
| 4.1 | 531.0 | 382.0 | 0.449 | 0.898 | -0.127 (small) | No |
| 4.2 | 261.5 | 322.0 | 0.638 | 0.898 | +0.082 (negligible) | No |

## Grid cell 100×500

**Table X. Convergence-rate comparison (100×500 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.90 | +0.10 | 0.237 | 0.949 | No |
| 1.3 | 1.00 | 0.03 | +0.97 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.77 | 0.00 | +0.77 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.60 | 0.00 | +0.60 | <0.001 | <0.001 | **Yes** |
| 3.1 | 0.97 | 0.00 | +0.97 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.50 | 0.00 | +0.50 | <0.001 | <0.001 | **Yes** |
| 3.4 | 0.27 | 0.00 | +0.27 | 0.005 | 0.023 | **Yes** |
| 3.5 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (100×500 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | <0.001 | <0.001 | +0.933 (large) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +1.000 (large) | **Yes** |
| 1.3 | 3.0 | 1.0 | <0.001 | <0.001 | -0.589 (large) | **Yes** |
| 1.4 | 13.5 | 419.0 | insufficient data | — | — | — |
| 2.1 | 7.0 | nan | insufficient data | — | — | — |
| 3.1 | 2.0 | 1.0 | <0.001 | <0.001 | -1.000 (large) | **Yes** |
| 3.2 | 2.0 | 305.0 | insufficient data | — | — | — |
| 3.3 | 9.0 | 199.0 | insufficient data | — | — | — |
| 3.4 | 20.0 | nan | insufficient data | — | — | — |
| 3.5 | 24.0 | nan | insufficient data | — | — | — |
| 4.1 | 77.5 | 299.0 | insufficient data | — | — | — |
| 4.2 | 5.0 | nan | insufficient data | — | — | — |

## Grid cell 200×100

**Table X. Convergence-rate comparison (200×100 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.77 | +0.23 | 0.011 | 0.063 | No |
| 1.3 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.47 | 0.00 | +0.47 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.20 | 0.00 | +0.20 | 0.024 | 0.119 | No |
| 3.1 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.33 | 0.00 | +0.33 | <0.001 | 0.006 | **Yes** |
| 3.4 | 0.17 | 0.00 | +0.17 | 0.052 | 0.209 | No |
| 3.5 | 0.93 | 0.00 | +0.93 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (200×100 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | 0.004 | 0.022 | +0.400 (medium) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +0.844 (large) | **Yes** |
| 1.3 | 5.0 | 1.0 | <0.001 | <0.001 | -0.933 (large) | **Yes** |
| 1.4 | 13.5 | 273.0 | 0.008 | 0.040 | +0.583 (large) | **Yes** |
| 2.1 | 15.0 | 295.0 | 0.041 | 0.165 | +0.624 (large) | No |
| 3.1 | 2.0 | 1.0 | <0.001 | <0.001 | -0.923 (large) | **Yes** |
| 3.2 | 2.0 | 461.0 | <0.001 | <0.001 | +1.000 (large) | **Yes** |
| 3.3 | 13.0 | 399.0 | <0.001 | <0.001 | +0.904 (large) | **Yes** |
| 3.4 | 136.0 | 648.0 | 0.115 | 0.345 | +0.528 (large) | No |
| 3.5 | 43.0 | 485.0 | <0.001 | <0.001 | +0.953 (large) | **Yes** |
| 4.1 | 321.0 | 443.0 | 0.377 | 0.377 | +0.259 (small) | No |
| 4.2 | 228.5 | 419.0 | 0.184 | 0.369 | +0.313 (medium) | No |

## Grid cell 200×200

**Table X. Convergence-rate comparison (200×200 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.80 | +0.20 | 0.024 | 0.119 | No |
| 1.3 | 1.00 | 0.03 | +0.97 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.60 | 0.00 | +0.60 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.43 | 0.00 | +0.43 | <0.001 | <0.001 | **Yes** |
| 3.1 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.37 | 0.00 | +0.37 | <0.001 | 0.002 | **Yes** |
| 3.4 | 0.13 | 0.00 | +0.13 | 0.112 | 0.450 | No |
| 3.5 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (200×200 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | <0.001 | <0.001 | +0.800 (large) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +0.936 (large) | **Yes** |
| 1.3 | 3.0 | 1.0 | <0.001 | <0.001 | -0.933 (large) | **Yes** |
| 1.4 | 14.0 | 47.0 | 0.117 | 0.117 | +0.474 (medium) | No |
| 2.1 | 10.0 | nan | insufficient data | — | — | — |
| 3.1 | 2.0 | 1.0 | <0.001 | <0.001 | -1.000 (large) | **Yes** |
| 3.2 | 2.0 | nan | insufficient data | — | — | — |
| 3.3 | 12.0 | nan | insufficient data | — | — | — |
| 3.4 | 33.0 | nan | insufficient data | — | — | — |
| 3.5 | 33.0 | nan | insufficient data | — | — | — |
| 4.1 | 400.0 | 133.0 | insufficient data | — | — | — |
| 4.2 | 22.5 | nan | insufficient data | — | — | — |

## Grid cell 200×500

**Table X. Convergence-rate comparison (200×500 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.90 | +0.10 | 0.237 | 0.949 | No |
| 1.3 | 1.00 | 0.03 | +0.97 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.77 | 0.00 | +0.77 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.60 | 0.00 | +0.60 | <0.001 | <0.001 | **Yes** |
| 3.1 | 0.97 | 0.00 | +0.97 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.50 | 0.00 | +0.50 | <0.001 | <0.001 | **Yes** |
| 3.4 | 0.27 | 0.00 | +0.27 | 0.005 | 0.023 | **Yes** |
| 3.5 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (200×500 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | <0.001 | <0.001 | +0.933 (large) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +1.000 (large) | **Yes** |
| 1.3 | 3.0 | 1.0 | <0.001 | <0.001 | -0.771 (large) | **Yes** |
| 1.4 | 13.5 | nan | insufficient data | — | — | — |
| 2.1 | 7.0 | nan | insufficient data | — | — | — |
| 3.1 | 2.0 | 1.0 | <0.001 | <0.001 | -1.000 (large) | **Yes** |
| 3.2 | 2.0 | nan | insufficient data | — | — | — |
| 3.3 | 9.0 | nan | insufficient data | — | — | — |
| 3.4 | 20.0 | nan | insufficient data | — | — | — |
| 3.5 | 24.0 | nan | insufficient data | — | — | — |
| 4.1 | 91.0 | nan | insufficient data | — | — | — |
| 4.2 | 5.0 | nan | insufficient data | — | — | — |

## Grid cell 500×100

**Table X. Convergence-rate comparison (500×100 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.77 | +0.23 | 0.011 | 0.063 | No |
| 1.3 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.47 | 0.00 | +0.47 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.20 | 0.00 | +0.20 | 0.024 | 0.119 | No |
| 3.1 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.33 | 0.00 | +0.33 | <0.001 | 0.006 | **Yes** |
| 3.4 | 0.17 | 0.00 | +0.17 | 0.052 | 0.209 | No |
| 3.5 | 0.93 | 0.00 | +0.93 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (500×100 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | 0.004 | 0.004 | +0.400 (medium) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +0.811 (large) | **Yes** |
| 1.3 | 5.0 | 1.0 | <0.001 | <0.001 | -1.000 (large) | **Yes** |
| 1.4 | 13.5 | nan | insufficient data | — | — | — |
| 2.1 | 12.0 | nan | insufficient data | — | — | — |
| 3.1 | 2.0 | 1.0 | <0.001 | <0.001 | -1.000 (large) | **Yes** |
| 3.2 | 2.0 | nan | insufficient data | — | — | — |
| 3.3 | 13.0 | nan | insufficient data | — | — | — |
| 3.4 | 108.0 | nan | insufficient data | — | — | — |
| 3.5 | 43.0 | nan | insufficient data | — | — | — |
| 4.1 | 83.5 | nan | insufficient data | — | — | — |
| 4.2 | 111.0 | nan | insufficient data | — | — | — |

## Grid cell 500×200

**Table X. Convergence-rate comparison (500×200 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.80 | +0.20 | 0.024 | 0.119 | No |
| 1.3 | 1.00 | 0.03 | +0.97 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.60 | 0.00 | +0.60 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.43 | 0.00 | +0.43 | <0.001 | <0.001 | **Yes** |
| 3.1 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.37 | 0.00 | +0.37 | <0.001 | 0.002 | **Yes** |
| 3.4 | 0.13 | 0.00 | +0.13 | 0.112 | 0.450 | No |
| 3.5 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (500×200 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | <0.001 | <0.001 | +0.800 (large) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +0.933 (large) | **Yes** |
| 1.3 | 3.0 | 1.0 | <0.001 | <0.001 | -0.933 (large) | **Yes** |
| 1.4 | 14.0 | nan | insufficient data | — | — | — |
| 2.1 | 10.0 | nan | insufficient data | — | — | — |
| 3.1 | 2.0 | 1.0 | <0.001 | <0.001 | -1.000 (large) | **Yes** |
| 3.2 | 2.0 | nan | insufficient data | — | — | — |
| 3.3 | 12.0 | nan | insufficient data | — | — | — |
| 3.4 | 38.0 | nan | insufficient data | — | — | — |
| 3.5 | 33.0 | nan | insufficient data | — | — | — |
| 4.1 | 400.0 | nan | insufficient data | — | — | — |
| 4.2 | 22.5 | nan | insufficient data | — | — | — |

## Grid cell 500×500

**Table X. Convergence-rate comparison (500×500 grid cell, 30 runs each, Fisher's exact test, Holm-Bonferroni correction across 12 tests).**

| Test | Std-GP rate | EML-GP rate | Δ | p (raw) | p (Holm) | Significant |
|------|-------------|-------------|------|---------|----------|-------------|
| 1.1 | 1.00 | 1.00 | +0.00 | 1.000 | 1.000 | No |
| 1.2 | 1.00 | 0.90 | +0.10 | 0.237 | 0.949 | No |
| 1.3 | 1.00 | 0.03 | +0.97 | <0.001 | <0.001 | **Yes** |
| 1.4 | 0.77 | 0.00 | +0.77 | <0.001 | <0.001 | **Yes** |
| 2.1 | 0.60 | 0.00 | +0.60 | <0.001 | <0.001 | **Yes** |
| 3.1 | 0.97 | 0.00 | +0.97 | <0.001 | <0.001 | **Yes** |
| 3.2 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 3.3 | 0.50 | 0.00 | +0.50 | <0.001 | <0.001 | **Yes** |
| 3.4 | 0.27 | 0.00 | +0.27 | 0.005 | 0.023 | **Yes** |
| 3.5 | 1.00 | 0.00 | +1.00 | <0.001 | <0.001 | **Yes** |
| 4.1 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |
| 4.2 | 0.00 | 0.00 | +0.00 | 1.000 | 1.000 | No |

**Table Y. Tree-size comparison (500×500 grid cell, Mann-Whitney U test, Holm-Bonferroni correction).**

| Test | Std-GP median | EML-GP median | p (raw) | p (Holm) | Effect size | Significant |
|------|---------------|---------------|---------|----------|-------------|-------------|
| 1.1 | 2.0 | 3.0 | <0.001 | <0.001 | +0.933 (large) | **Yes** |
| 1.2 | 2.0 | 7.0 | <0.001 | <0.001 | +1.000 (large) | **Yes** |
| 1.3 | 3.0 | 1.0 | <0.001 | <0.001 | -0.771 (large) | **Yes** |
| 1.4 | 13.5 | nan | insufficient data | — | — | — |
| 2.1 | 7.0 | nan | insufficient data | — | — | — |
| 3.1 | 2.0 | 1.0 | <0.001 | <0.001 | -1.000 (large) | **Yes** |
| 3.2 | 2.0 | nan | insufficient data | — | — | — |
| 3.3 | 9.0 | nan | insufficient data | — | — | — |
| 3.4 | 20.0 | nan | insufficient data | — | — | — |
| 3.5 | 24.0 | nan | insufficient data | — | — | — |
| 4.1 | 91.0 | nan | insufficient data | — | — | — |
| 4.2 | 5.0 | nan | insufficient data | — | — | — |