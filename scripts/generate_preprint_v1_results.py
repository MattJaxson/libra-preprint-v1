#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate the descriptive results reported in the Libra Version 1 preprint.

This analysis deliberately does not label any threshold as community-defined.
It compares fixed threshold scenarios to show that an audit classification is
sensitive to a normative parameter. Groups with fewer than 30 observations are
retained in the machine-readable appendix but excluded from aggregate flag
counts.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "research" / "preprint_v1_results.json"
THRESHOLDS = (0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
MIN_GROUP_N = 30
BOOTSTRAP_REPLICATES = 10_000
SEED = 20_260_930
SKIP_LABELS = {
    "Race Not Available",
    "Free Form Text Only",
    "Joint",
    "2 or more minority races",
    "Other",
}

DATASETS = {
    "hmda_michigan_single_lender": {
        "label": "HMDA Michigan single-lender filing",
        "path": ROOT / "data" / "demo" / "hmda_michigan_lending.csv",
        "group_column": "derived_race",
        "outcome_column": "action_taken",
        "favorable_value": 1,
        "reference_group": "White",
        "focus_group": "Black or African American",
        "deduplicate": True,
    },
    "compas_broward": {
        "label": "ProPublica COMPAS Broward County data",
        "path": ROOT / "data" / "demo" / "compas_recidivism.csv",
        "group_column": "race",
        "outcome_column": "two_year_recid",
        "favorable_value": 0,
        "reference_group": "Caucasian",
        "focus_group": "African-American",
        "deduplicate": True,
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def bootstrap_di(
    target: np.ndarray,
    reference: np.ndarray,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Percentile interval from stratified Bernoulli bootstrap samples."""
    target_successes = rng.binomial(
        target.size, target.mean(), size=BOOTSTRAP_REPLICATES
    )
    reference_successes = rng.binomial(
        reference.size, reference.mean(), size=BOOTSTRAP_REPLICATES
    )
    target_rates = target_successes / target.size
    reference_rates = reference_successes / reference.size
    valid = reference_rates > 0
    ratios = target_rates[valid] / reference_rates[valid]
    low, high = np.quantile(ratios, [0.025, 0.975])
    return float(low), float(high)


def analyze_dataset(key: str, spec: dict, rng: np.random.Generator) -> dict:
    path = spec["path"]
    frame = pd.read_csv(path)
    raw_n = len(frame)
    frame = frame.loc[~frame[spec["group_column"]].isin(SKIP_LABELS)].copy()
    filtered_n = len(frame)
    duplicates_removed = 0
    if spec["deduplicate"]:
        before = len(frame)
        frame = frame.drop_duplicates().copy()
        duplicates_removed = before - len(frame)

    binary = frame[spec["outcome_column"]].eq(spec["favorable_value"]).astype(int)
    grouped = {
        str(group): binary.loc[index].to_numpy(dtype=int)
        for group, index in frame.groupby(spec["group_column"]).groups.items()
    }
    reference = spec["reference_group"]
    reference_rate = float(grouped[reference].mean())

    groups = {}
    for group, values in sorted(grouped.items()):
        rate = float(values.mean())
        di = 1.0 if group == reference else rate / reference_rate
        if group == reference:
            ci_low, ci_high = 1.0, 1.0
        else:
            ci_low, ci_high = bootstrap_di(values, grouped[reference], rng)
        groups[group] = {
            "n": int(values.size),
            "favorable_rate": round(rate, 6),
            "disparate_impact": round(di, 6),
            "di_bootstrap_95_percentile_interval": [
                round(ci_low, 6),
                round(ci_high, 6),
            ],
            "reportable_n": bool(values.size >= MIN_GROUP_N),
            "flagged_at": [
                threshold
                for threshold in THRESHOLDS
                if group != reference and di < threshold
            ],
        }

    threshold_sweep = {}
    for threshold in THRESHOLDS:
        flagged = [
            group
            for group, result in groups.items()
            if group != reference
            and result["reportable_n"]
            and result["disparate_impact"] < threshold
        ]
        threshold_sweep[f"{threshold:.2f}"] = {
            "flagged_count_minimum_n_30": len(flagged),
            "flagged_groups_minimum_n_30": flagged,
        }

    focus = spec["focus_group"]
    return {
        "label": spec["label"],
        "source_path": str(path.relative_to(ROOT)),
        "source_sha256": sha256(path),
        "raw_records": raw_n,
        "records_after_label_filter": filtered_n,
        "exact_duplicates_removed": duplicates_removed,
        "analyzed_records": len(frame),
        "group_column": spec["group_column"],
        "outcome_column": spec["outcome_column"],
        "favorable_value": spec["favorable_value"],
        "reference_group": reference,
        "focus_group": focus,
        "focus_result": groups[focus],
        "groups": groups,
        "threshold_sweep": threshold_sweep,
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    results = {
        "analysis": {
            "purpose": "descriptive threshold-sensitivity demonstration",
            "community_participant_data_used": False,
            "minimum_group_n_for_aggregate_counts": MIN_GROUP_N,
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "random_seed": SEED,
            "thresholds": list(THRESHOLDS),
            "git_commit_at_generation": git_commit(),
        },
        "datasets": {
            key: analyze_dataset(key, spec, rng) for key, spec in DATASETS.items()
        },
    }
    OUTPUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    for dataset in results["datasets"].values():
        focus = dataset["focus_result"]
        print(
            f"{dataset['label']}: {dataset['focus_group']} "
            f"DI={focus['disparate_impact']:.4f}, "
            f"95% bootstrap interval={focus['di_bootstrap_95_percentile_interval']}"
        )


if __name__ == "__main__":
    main()
