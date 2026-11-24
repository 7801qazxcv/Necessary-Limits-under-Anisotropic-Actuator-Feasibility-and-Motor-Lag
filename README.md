# Necessary Limits under Anisotropic Actuator Feasibility and Motor Lag — replication bundle

**Status: PUBLIC REPLICATION BUNDLE.** This repository holds the scripts, result
artifacts, frozen preregistration criteria and manuscript source for the paper.
It is a **pre-submission** manuscript; see "Author-side decisions still open".

Populated 2026-11-19 and kept in step with the manuscript since; after every push
the GitHub API is used to confirm the commit, a non-truncated recursive tree, and
that every remote blob SHA matches the local commit. The manuscript's
Data-availability statement cites this repository directly. The bundle's
`build_manuscript.py` regenerates the manuscript source, the separate title page
and the highlights from the artifact macros, so the archived generator and the
archived `paper/main.tex` agree.

## What is here
- Frozen preregistration criteria (`preregistration_*.md`) and all amendments, so the
  timeline of every criterion change is auditable.
- Simulation / audit scripts and their on-disk result artifacts (JSON).
- The **anonymized** manuscript LaTeX source and compiled PDF
  (`paper/main.tex`, `paper/main.pdf`), bibliography, figures, provenance table
  and baseline set.
- The separate `paper/title_page.tex` / `title_page.pdf` (author identities,
  affiliations, ORCID, contact, declarations) and `paper/highlights.txt`,
  required by the journal's double-anonymized submission.
- `MANIFEST.md` with SHA-256 of every file, and `LICENSE` (MIT).

## What is deliberately excluded
Third-party raw scrapes whose redistribution licence is not yet closed
(`crazyflie_params_raw.json` and fetched paper text, fetched paper text), live-API response dumps
and request-header utilities, superseded result versions, internal editorial
assessment and reviewer-response reports, the internal author-metadata record
file, and pre-revision manuscript snapshots. Only `real_platform_config.json` —
our own derived parameter mapping — is included.

## Reproduce
Python 3.13 with numpy; a TeX distribution with `elsarticle.cls` for the PDF.
From the repository root:

    python experiments/run_all_experiments.py            # frozen-artifact assertions
    python experiments/run_all_experiments.py --full    # re-run the full chain
    python build_manuscript_numbers.py && python build_manuscript.py
    pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
    pdflatex title_page.tex && pdflatex title_page.tex

All displayed numeric values are generated from the JSON artifacts by
`build_manuscript_numbers.py`; none is transcribed by hand. See `paper/provenance.md`.

## Note on the term "reviewer" in tool code
`build_submission.py` contains the literal blocklist terms (`reviewer`, `rebuttal`,
`editorial-only`, ...) as **regex patterns** used to keep the submission package free
of internal wording. Those strings are tool code, not manuscript content, and are
intentionally retained so the check remains functional.

## Author-side decisions still open
- **Preprint policy**: whether a pre-submission manuscript may be made public at all.
- **Double-anonymized review tension**: the manuscript PDF is anonymized, but this
  public repository ships a title page with author identities and the manuscript
  cites the repository in Data availability. A referee searching the title can
  therefore recover identities. The author has chosen to keep the repository
  public; making it private until acceptance remains an open author decision.
- Clarivate Master Journal List per-ISSN re-check under an institutional login
  (the SCIE indexing line has been retrieved and verified; the site notes some
  details require a free login).
- The venue-specific Editorial Manager URL is entered via "Submit your article"
  on the journal homepage at submission time; it is intentionally not guessed here.
