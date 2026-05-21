# EML Operator: Theory, Implementation, and K-Complexity Notes

Source: arXiv:2603.21852, "All elementary functions from a single operator" (Odrzywolek).
Implementation: Local directory `eml-skill/` (originally yaniv-golan/eml-skill).

---

## Core Definition

The EML operator is defined as:

> eml(x, y) = exp(x) − ln(y)

Together with the constant 1 as the sole leaf terminal, this single binary operator generates all elementary functions. The grammar is:

> S → 1 | eml(S, S)

Every elementary function is expressed as a binary tree in which every internal node is `eml` and every leaf is 1 (or an input variable x, y). The structural complexity of a function is measured by K, the total number of nodes (operators plus leaves) in the minimal such tree.

---

## Foundational Axioms

**Axiom [1]:** eml(1, 1) = exp(1) − ln(1) = e. K = 3.

**Axiom [2]:** eml(x, 1) = exp(x) − ln(1) = exp(x). K = 3. Proven minimal.

**Axiom [3]:** ln(x) = eml(1, eml(eml(1, x), 1)). K = 7. Proven minimal by exhaustive enumeration up to K = 5 (no match found at K ≤ 5).

Derivation of Axiom [3]:

    Let A = eml(1, x) = exp(1) − ln(x) = e − ln(x)
    Let B = eml(A, 1) = exp(A) = exp(e − ln(x)) = exp(e) / x
    Let C = eml(1, B) = exp(1) − ln(B) = e − ln(exp(e) / x) = e − (e − ln(x)) = ln(x)

---

## K-Complexity Table

K is the node count of the minimal (or best-known) EML tree for each primitive. Values marked as proven minimal were confirmed by exhaustive enumeration. All others are upper bounds.

| Primitive | K | Source | Minimal |
|---|---|---|---|
| 1 (constant) | 1 | trivial leaf | proven |
| e | 3 | Axiom [1] | proven |
| exp(x) | 3 | Axiom [2] | proven |
| ln(x) | 7 | Axiom [3] | proven |
| x − y | 11 | direct search | proven |
| x × y | 17 | direct search | proven |
| x / y | 17 | direct search | — |
| x + y | 19 | direct search | proven |
| sqrt(x) | 59 | via exp(½·ln(x)) | upper bound |
| sinh(x) | 81 | via exp composition | upper bound |
| cosh(x) | 89 | via exp composition | upper bound |
| tanh(x) | 201 | via sinh/cosh | upper bound |
| cos(x) | 269 | i-cascade | upper bound |
| sin(x) | 351 | i-cascade | upper bound |
| arctan(x) | 355 | via log | upper bound |
| tan(x) | 651 | via sin/cos | upper bound |

**Note on negation and reciprocal:** The paper (Table 4, direct-search) reports K = 15 for both −x and 1/x. These values require extended-real arithmetic (ln(0) = −∞ treated symbolically). Under IEEE-754 floating-point (Python cmath), exhaustive search up to K = 17 finds no match at K = 15; the shortest IEEE-754 witnesses have K = 17. This is a semantic divergence, not a mathematical error. All computations in this experiment use IEEE-754 arithmetic, so K = 17 is the operative value for any function that requires negation or reciprocal as a sub-expression.

**Note on trigonometric K-values:** sin, cos, and tan do not appear in Table 4 of the paper. The values above are upper bounds derived from the proof-engine closure page using an i-cascade construction: sin(x) = (exp(ix) − exp(−ix)) / 2i, cos(x) = (exp(ix) + exp(−ix)) / 2. These are not direct-search minimums.

**Note on sqrt:** The paper reports a direct-search value of K ≥ 43 (lower bound 35, minimality unconfirmed). The best known witness is K = 59, constructed via exp(½·ln(x)). The value K = 59 is used in this experiment.

---

## Complex Arithmetic

The paper requires that all internal computations be performed in the complex domain. This is necessary because constants such as i and π must be derived through complex logarithms:

    ln(−1) = iπ  (principal branch)
    i = exp(ln(−1) / 2)
    π = Im(ln(−1))

The implementation uses Python's `cmath` module throughout (principal branch). Euler's formula exp(iφ) = cos(φ) + i·sin(φ) is satisfied to within floating-point precision across all tested values. Branch cuts on the negative real axis for ln, asin, acos, and atan are handled correctly by the principal branch convention.

---

## Semantic Note: IEEE-754 vs Extended Reals

The paper's Mathematica proofs use extended-real arithmetic in which ln(0) = −∞ and exp(−∞) = 0 are treated as exact symbolic values. Python cmath approximates these as `complex(-inf, 0)` and `0.0` respectively, which agrees in practice but differs in two edge cases (negation and reciprocal at K = 15) where intermediate symbolic cancellations do not survive floating-point evaluation.

All K-values used in this experiment reflect IEEE-754 behaviour. Where the paper's value and the IEEE-754 value differ, the IEEE-754 value is used and noted above.

---

## Coverage

The witness library covers all 36 primitives listed in Table 1 of the paper: 8 constants (1, e, i, −1, 2, −2, π, √2), 20 functions (exp, ln, sqrt, sin, cos, tan, arcsin, arccos, arctan, sinh, cosh, tanh, and their inverses), and 8 operations (+, −, ×, /, power, logarithm base a, average, hypotenuse). All have verified witnesses with numerical error below 1×10⁻¹⁰ on test inputs. Nine primitives have been proven minimal by exhaustive enumeration; the remainder are certified upper bounds.
