# Findings suite

Every review finding is an executable check, so no finding rests on reasoning alone.

- `instruments.py` holds the shared loaders and statistics. `self_tests()` runs positive and negative controls for every instrument, and the suite reports nothing if any control fails.
- `findings.py` is the registry: one function per finding (A–F), plus the manuscript phrases that indicate the error.
- `run_findings.py` is the runner; it writes `revision/FINDINGS_REPORT.md` and a `.json` copy.
- `cache/` holds the extracted text of Odrzywołek [9] (v2, main and SI) and a DOI-metadata cache (`--online` refreshes it).

## Workflow

1. **Baseline, once.** Run against the *unedited* submitted manuscript. Every error phrase must be found; any that isn't shows `PATTERN_FAIL`, and that pattern gets fixed before being trusted.

       python3 research/findings/run_findings.py --baseline \
           --manuscript revision/manuscript/submitted_main.pdf \
           --manuscript revision/manuscript/submitted_supplement.pdf

2. **After editing.** Run against the revised manuscript (PDF, DOCX or TXT). Every `error` finding should show `FIXED`.

       python3 research/findings/run_findings.py --manuscript revised_main.docx --manuscript revised_supplement.docx

3. **Evidence only, no manuscript:** `python3 research/findings/run_findings.py [--skip-slow]`. `--skip-slow` skips the SSC re-run in A7 (about 1 minute).

## Statuses

- **Evidence:**
  - `CONFIRMED`: the error exists.
  - `FACT`: an undocumented implementation fact, verified in code.
  - `UNREPRODUCIBLE`: the published value can't be reproduced by any available method.
  - `REFUTED`: the evidence contradicts the finding. Investigate before dropping it: in the first run, all three REFUTED results were bugs in the checks themselves.
  - `SUGGESTION`: wording only.
- **Text:**
  - `OPEN`: the erroneous wording is still present, or required wording is missing.
  - `FIXED`: neither.
  - `EXTRACTION_FAIL`: the manuscript text couldn't be read.
  - `PATTERN_FAIL`: baseline mode only; the phrase isn't in the submission.

## Rules

- A new finding enters `findings.py` only with an evidence function.
- Compare like with like: same source, same precision (trajectory logs are 6-decimal), same definition.
- Reproduce a published value with its original method before calling it wrong.
- Author-only facts are questions, not findings.
- Rerun-driven number changes are tracked in `revision/CLAIMS_LEDGER.md`. A separate numbers-reconciliation script checks those against the revised text at the end.
