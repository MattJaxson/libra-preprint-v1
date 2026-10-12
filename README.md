# Libra Technical Preprint v1.1.0

This repository is the public reproducibility package for:

> Matthew Jackson. *Libra: A Prototype for Provenance-Aware Fairness Audit
> Parameters — Implementation Review and Descriptive Sensitivity Analysis.*
> Technical preprint v1.1.0, 2026. Not peer reviewed.
> Zenodo. https://doi.org/10.5281/zenodo.23312450

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23312450.svg)](https://doi.org/10.5281/zenodo.23312450)

## Contents

- `docs/research/libra_preprint_v1.tex`: manuscript source.
- `scripts/generate_preprint_v1_results.py` and
  `scripts/preprint_hmda_outcome_sensitivity.py`: descriptive analyses.
- `docs/research/preprint_v1_results.json` and
  `docs/research/preprint_hmda_outcome_sensitivity.json`: machine-readable results.
- `docs/research/preprint_data_acquisition.md`: exact source URLs, hashes, and
  source-drift cautions.
- `docs/research/requirements-preprint.txt`: tested direct dependency pins.

## Evidence boundary

This revision reviews a partial software prototype and researcher-defined
threshold and outcome scenarios. It is **not** a participant-backed study, an
AI-model fairness evaluation, a complete end-to-end authenticated governance
trace, a completed District 3 session, or evidence of government endorsement
or adoption. The COMPAS example uses observed recidivism, not model scores.
The earlier v1.0.1 release reports a different analysis and should not be used
to reproduce the v1.1.0 paper.
This narrow package reproduces the descriptive analyses, not the paper's
local API/core implementation checks; the inspected application source and
test fixtures are not bundled here.

## Reproduction

The analyses were checked using Python 3.12.0 and the direct pins in
`docs/research/requirements-preprint.txt`. Place source data at:

- `data/demo/hmda_michigan_lending.csv`
- `data/demo/compas_recidivism.csv`

Then run:

```bash
python -m pip install -r docs/research/requirements-preprint.txt
python scripts/generate_preprint_v1_results.py
python scripts/preprint_hmda_outcome_sensitivity.py
```

The release does not redistribute raw third-party datasets. Follow the
[acquisition note](docs/research/preprint_data_acquisition.md) for the exact
CFPB query and ProPublica file, then verify the recorded hashes and row counts.
The primary HMDA calculation retains four identical public-use rows because
their identity does not prove duplicate real-world applications; the separate
deduplication analysis is a sensitivity check. Reacquired source files can
drift, so reproduce against the documented snapshots before comparing outputs.

## Licensing

- Manuscript source and rendered manuscript: **CC BY 4.0**. See
  `LICENSE-PAPER.md`.
- Original analysis code: **Apache License 2.0**. See `LICENSE`.
- Derived JSON results: **CC BY 4.0** with attribution.
- Third-party datasets and publications are not relicensed.

## Citation

Use the metadata in `CITATION.cff`. The preprint PDF is archived on Zenodo:
<https://doi.org/10.5281/zenodo.23312450>

The versioned companion release is:

<https://github.com/MattJaxson/libra-preprint-v1/releases/tag/v1.1.0>
