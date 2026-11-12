"""Validate a run CSV against the LinkML schema."""

from __future__ import annotations

import csv
from pathlib import Path

from linkml.validator import validate

NUMERIC = {"working_volume_L", "temperature_C", "pH", "duration_h", "titre_g_per_L"}


def csv_to_instance(csv_path: Path) -> dict:
    """Read the CSV into a RunCollection dict, dropping empty cells."""
    runs = []
    with csv_path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            run = {}
            for key, value in row.items():
                value = (value or "").strip()
                if not value:
                    continue
                run[key] = float(value) if key in NUMERIC else value
            runs.append(run)
    return {"runs": runs}


def validate_csv(csv_path: Path, schema_path: Path) -> list[str]:
    """Return LinkML validation messages (empty list means valid)."""
    report = validate(csv_to_instance(csv_path), str(schema_path), target_class="RunCollection")
    return sorted(r.message for r in report.results)
