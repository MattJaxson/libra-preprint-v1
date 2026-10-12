#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproduce HMDA outcome-definition sensitivity for the Libra preprint.

These are descriptive administrative-record comparisons, not model audits.
The input is the local, single-lender 2024 Michigan HMDA extract used in v1.
"""

from __future__ import annotations

import hashlib
import json
import csv
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/demo/hmda_michigan_lending.csv"
OUTPUT = ROOT / "docs/research/preprint_hmda_outcome_sensitivity.json"
SKIP = {
    "Race Not Available", "Free Form Text Only", "Joint",
    "2 or more minority races", "Other",
}
SCENARIOS = {
    "all_actions_origination": {
        "included_actions": [1, 2, 3, 4, 5, 6],
        "favorable_actions": [1],
        "interpretation": "originated versus every other recorded action",
    },
    "originated_versus_denied": {
        "included_actions": [1, 3],
        "favorable_actions": [1],
        "interpretation": "originated versus denied only",
    },
    "approved_or_originated_versus_denied": {
        "included_actions": [1, 2, 3],
        "favorable_actions": [1, 2],
        "interpretation": "originated or approved-not-accepted versus denied",
    },
}


def row_multiset_sha256(path: Path) -> str:
    """Order-insensitive digest of parsed CSV rows, including the header."""
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = sorted(tuple(row) for row in reader)
    canonical = json.dumps([header, rows], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> None:
    raw = pd.read_csv(INPUT)
    filtered = raw.loc[~raw.derived_race.isin(SKIP)].copy()
    # A public-use file can contain identical rows for distinct applications.
    # Retain them in the primary analysis; report exact-row deduplication below
    # only as an analytic sensitivity scenario.
    frame = filtered
    deduplicated = filtered.drop_duplicates().copy()
    results = {
        "python_version": sys.version.split()[0],
        "pandas_version": pd.__version__,
        "analysis_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_path": str(INPUT.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "source_row_multiset_sha256": row_multiset_sha256(INPUT),
        "official_acquisition_url": (
            "https://ffiec.cfpb.gov/v2/data-browser-api/view/csv"
            "?states=MI&years=2024&leis=B4TYDEB6GKMZO031MB27"
            "&actions_taken=1,2,3,4,5,6,7,8"
        ),
        "official_reacquisition_verified_date": "2026-09-30",
        "lender_lei": sorted(str(x) for x in raw.lei.dropna().unique()),
        "activity_year": sorted(int(x) for x in raw.activity_year.dropna().unique()),
        "raw_n": len(raw),
        "after_race_filter_n": len(filtered),
        "exact_duplicate_rows_present": len(filtered) - len(deduplicated),
        "exact_duplicates_removed": 0,
        "action_codes": {
            "1": "originated", "2": "approved, not accepted", "3": "denied",
            "4": "withdrawn", "5": "closed for incompleteness",
            "6": "purchased loan",
        },
        "scenarios": {},
    }
    results["exact_row_deduplication_sensitivity"] = {}
    for name, spec in SCENARIOS.items():
        for source, destination in (
            (frame, results["scenarios"]),
            (deduplicated, results["exact_row_deduplication_sensitivity"]),
        ):
            subset = source.loc[source.action_taken.isin(spec["included_actions"])].copy()
            subset["favorable"] = subset.action_taken.isin(spec["favorable_actions"])
            grouped = subset.groupby("derived_race").favorable.agg(["sum", "count", "mean"])
            reference_rate = float(grouped.loc["White", "mean"])
            groups = {
                str(group): {
                    "favorable_n": int(row["sum"]),
                    "n": int(row["count"]),
                    "rate": float(row["mean"]),
                    "ratio_to_white": float(row["mean"] / reference_rate),
                }
                for group, row in grouped.iterrows()
            }
            destination[name] = {
                **spec,
                "n": len(subset),
                "groups": groups,
                "black_to_white_ratio": groups["Black or African American"]["ratio_to_white"],
            }
    OUTPUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for name, scenario in results["scenarios"].items():
        print(f"{name}: n={scenario['n']}, Black/White={scenario['black_to_white_ratio']:.4f}")
    print(
        "all_actions_exact_row_deduplication_sensitivity: "
        f"n={results['exact_row_deduplication_sensitivity']['all_actions_origination']['n']}, "
        f"Black/White={results['exact_row_deduplication_sensitivity']['all_actions_origination']['black_to_white_ratio']:.4f}"
    )
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
