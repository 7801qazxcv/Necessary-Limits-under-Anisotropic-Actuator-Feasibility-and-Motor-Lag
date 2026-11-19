# Necessary Limits under Anisotropic Actuator Feasibility and Motor Lag — replication bundle

**Status: PUBLIC REPLICATION BUNDLE.** This repository holds the scripts, result
artifacts, frozen preregistration criteria and manuscript source for the paper.
It is a **pre-submission** manuscript; see "Author-side decisions still open".

The repository was populated on 2026-11-19 and verified through the GitHub API:
one commit, a non-truncated recursive tree, and every blob SHA matching the local
commit. The manuscript's Data-availability statement still reads "available from
the corresponding author upon reasonable request" — citing this repository in the
paper is an author-side decision that has not been taken automatically.

## What is here
- Frozen preregistration criteria (`preregistration_*.md`) and all amendments, so the
  timeline of every criterion change is auditable.
- Simulation / audit scripts and their on-disk result artifacts (JSON).
- The manuscript LaTeX source, the compiled PDF (`paper/main.pdf`), bibliography,
  figures, provenance table and baseline set.
- `MANIFEST.md` with SHA-256 of every file.

## What is deliberately excluded
Third-party raw scrapes whose redistribution licence is not yet closed
(`crazyflie_params_raw.json`, `arxiv2404_text.txt`), live-API response dumps and
request-header utilities (`ref_meta_raw.json`, `verify_cites.py`), superseded result
versions, internal editorial assessment reports, author metadata records, and
pre-revision manuscript snapshots. Only `real_platform_config.json` — our own derived
parameter mapping — is included.

## Reproduce
Python 3.13 with numpy; a TeX distribution with `elsarticle.cls` for the PDF.
From the repository root:

    python experiments/run_all_experiments.py            # frozen-artifact assertions
    python experiments/run_all_experiments.py --full    # re-run the full chain
    python build_manuscript_numbers.py && python build_manuscript.py
    pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex

All displayed numeric values are generated from the JSON artifacts by
`build_manuscript_numbers.py`; none is transcribed by hand. See `paper/provenance.md`.

## Note on the term "reviewer" in tool code
`build_submission.py` contains the literal blocklist terms (`reviewer`, `rebuttal`,
`editorial-only`, ...) as **regex patterns** used to keep the submission package free
of internal wording. Those strings are tool code, not manuscript content, and are
intentionally retained so the check remains functional.

## Author-side decisions still open
- **Preprint policy**: whether a pre-submission manuscript may be made public at all.
  The included `paper/main.tex`, `paper/main.pdf` and `build_manuscript.py` contain
  author names, affiliations, ORCID and e-mail addresses exactly as they appear in
  the manuscript.
- Repository licence, CRediT, funding, AI-disclosure approval and submission approval.
- Whether to replace the Data-availability statement with this repository's URL.
