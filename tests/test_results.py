"""The committed results, gap report and README block must match a fresh run."""

import json
import subprocess
import sys
from pathlib import Path

from ferm_demo.paths import JSON_SCHEMA, LINKML_SCHEMA, RESULTS, ROOT
from ferm_demo.pipeline import START, readme_block, run


def test_results_and_readme_are_current():
    committed = json.loads((RESULTS / "results.json").read_text())
    gap_committed = (RESULTS / "gap_report.md").read_text()
    fresh = run()
    assert fresh == committed
    assert (RESULTS / "gap_report.md").read_text() == gap_committed
    readme = (ROOT / "README.md").read_text()
    assert START in readme
    assert readme_block(fresh) in readme


def test_json_schema_is_regenerated_from_linkml():
    out = subprocess.run(
        [str(Path(sys.executable).parent / "gen-json-schema"), str(LINKML_SCHEMA)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert out.stdout == JSON_SCHEMA.read_text()


def test_readme_has_no_long_dashes():
    text = (ROOT / "README.md").read_text()
    assert "–" not in text and "—" not in text
