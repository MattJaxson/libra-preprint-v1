# Libra Preprint Version 1

This repository is the public reproducibility package for:

> Matthew Jackson. *Libra: From Community Input to Audit Parameters — A
> Provenance-Bearing Prototype for Participatory Fairness Auditing.* Version
> 1.0 preprint, 2026.

## Contents

- `docs/research/libra_preprint_v1.tex`: manuscript source.
- `scripts/generate_preprint_v1_results.py`: analysis used for the reported
  HMDA and COMPAS threshold-sensitivity results.
- `docs/research/preprint_v1_results.json`: machine-readable Version 1 output.

## Evidence boundary

Version 1 evaluates a methods-and-system prototype and researcher-defined
threshold scenarios. It uses no community participant data and does not claim
a community-selected threshold, a completed District 3 session, endorsement,
adoption, or a published community standard.

## Reproduction

The analysis requires Python 3.11 or later with the packages listed in
`requirements.txt`. Place source data at:

- `data/demo/hmda_michigan_lending.csv`
- `data/demo/compas_recidivism.csv`

Then run:

```bash
python -m pip install -r requirements.txt
python scripts/generate_preprint_v1_results.py
```

The release does not redistribute the raw datasets. Obtain and use HMDA data
from the [CFPB data publication platform](https://ffiec.cfpb.gov/data-publication/)
and COMPAS data from the
[ProPublica COMPAS repository](https://github.com/propublica/compas-analysis),
subject to their respective terms. The JSON output records the SHA-256 digest
of each exact input file used for Version 1.

## Licensing

- Manuscript source and rendered manuscript: **CC BY 4.0**. See
  `LICENSE-PAPER.md`.
- Original analysis code: **Apache License 2.0**. See `LICENSE`.
- Derived JSON results: **CC BY 4.0** with attribution.
- Third-party datasets and publications are not relicensed.

## Citation

Use the metadata in `CITATION.cff`. The stable Version 1 release is:

<https://github.com/MattJaxson/libra-preprint-v1/releases/tag/v1.0.0>
