# Data acquisition and snapshot checks for the revised Libra preprint

Verified on **2026-09-30**. These are third-party public-use datasets, not community-session data. The commands below write to a new temporary directory; they do not replace the repository's local data files.

## Reproduce the analysis

From the repository root, use Python 3.12 with the pinned direct dependencies in [`requirements-preprint.txt`](requirements-preprint.txt):

```sh
preprint_env_dir=$(mktemp -d)
python3.12 -m venv "$preprint_env_dir/venv"
"$preprint_env_dir/venv/bin/python" -m pip install -r docs/research/requirements-preprint.txt
"$preprint_env_dir/venv/bin/python" scripts/generate_preprint_v1_results.py
"$preprint_env_dir/venv/bin/python" scripts/preprint_hmda_outcome_sensitivity.py
```

A fresh Python 3.12.0 environment with NumPy 2.3.5 and pandas 2.2.3 regenerated both v1.1.0 result files on 2026-10-02. The scripts record interpreter and package versions and their own SHA-256 digests in the JSON output. These direct pins are not a full transitive lock. The parametric-bootstrap percentile endpoints depend on the declared preprocessing, seed, and library versions, so use the regenerated JSON as the source for the revised manuscript's intervals. The scripts write their result JSON files in `docs/research/`; copy them first if you need to preserve an earlier output byte-for-byte.

The primary HMDA analysis retains all 3,831 race-eligible public-use records, including four pairs of identical released rows. Identity of released fields is insufficient evidence that they represent duplicate real-world applications. `preprint_hmda_outcome_sensitivity.json` reports exact-row deduplication separately for all three outcome definitions. Do not silently substitute those sensitivity results for the primary estimates.

## HMDA: one lender, Michigan, 2024

The official [CFPB/FFIEC Data Browser API](https://ffiec.cfpb.gov/documentation/api/data-browser/) supports a CSV subset request with year, state, LEI, and action filters. The matching request is:

```text
https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?states=MI&years=2024&leis=B4TYDEB6GKMZO031MB27&actions_taken=1,2,3,4,5,6,7,8
```

The official [action-code guide](https://files.ffiec.cfpb.gov/documentation/2024-hmda-fig.pdf) defines codes 1–8. The current API response has 4,463 rows and 99 columns. Its parsed CSV row multiset is identical to `data/demo/hmda_michigan_lending.csv`; the byte SHA-256 differs because the API returned rows in a different order. The order-insensitive parsed-row multiset digest from `scripts/preprint_hmda_outcome_sensitivity.py` is `b1c6b9619e2676fe8ce2901707cf17e99987bde668a678605d7f9702d1d9f4da` for both copies. The repository snapshot byte SHA-256 is `17dad996ce10286d269e278cd6538067eab40cbf5616d26b6f2c6bcb169d3029`.

To reacquire without overwriting the local source:

```sh
reacquired_dir=$(mktemp -d)
curl -fLsS 'https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?states=MI&years=2024&leis=B4TYDEB6GKMZO031MB27&actions_taken=1,2,3,4,5,6,7,8' -o "$reacquired_dir/hmda.csv"
```

This API's one-year dataset can be updated. A future response may differ; use the archived local file hash and the acquisition date to distinguish source drift from analysis drift. Do not assume identical public-use rows represent duplicate real-world applications.

## ProPublica COMPAS

The source file is [`compas-scores-two-years.csv`](https://github.com/propublica/compas-analysis/blob/master/compas-scores-two-years.csv) from ProPublica's repository. On 2026-09-30, a fresh download was byte-for-byte identical to `data/demo/compas_recidivism.csv`: 7,214 rows and SHA-256 `c451db85908b2f7fef1d83203bedf6b71ecda0d5af468d82ae62178f91d0cc7d`.

```sh
reacquired_dir=$(mktemp -d)
curl -fLsS 'https://raw.githubusercontent.com/propublica/compas-analysis/master/compas-scores-two-years.csv' -o "$reacquired_dir/compas.csv"
shasum -a 256 "$reacquired_dir/compas.csv"
```

The current manuscript uses only recorded two-year recidivism, not COMPAS model-score fields. This acquisition check establishes source identity, not the benchmark's construct validity or a model-fairness result.
