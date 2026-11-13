"""The SSSOM file must parse, use known predicates, and cite only checked terms."""

import csv
import json

from ferm_demo.gap import cited_curies, load_mapping
from ferm_demo.paths import COLUMN_MAPPING, EXTERNAL_TERMS, ONTOLOGY, ROOT

SSSOM = ROOT / "mappings" / "ferm.sssom.tsv"
# uom IRIs as listed in PREFER src/templates/units.tsv (checked 2026-11-13)
PREFER_UOM = {"uom:Cel", "uom:h", "uom:L", "uom:g.L-1", "uom:%5BpH%5D"}


def _rows():
    lines = [line for line in SSSOM.read_text().splitlines() if not line.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def _verified():
    return {r["curie"] for r in json.loads(EXTERNAL_TERMS.read_text()) if r["verified"]}


def test_sssom_rows_are_well_formed():
    rows = _rows()
    assert rows
    for r in rows:
        assert r["predicate_id"] in {"skos:exactMatch", "skos:broadMatch", "skos:narrowMatch", "skos:relatedMatch"}
        assert r["mapping_justification"] == "semapv:ManualMappingCuration"


def test_sssom_terms_exist():
    ferm = ONTOLOGY.read_text()
    verified = _verified()
    for r in _rows():
        for curie in (r["subject_id"], r["object_id"]):
            if curie.startswith("FERM:"):
                assert f"FERM:{curie.split(':')[1]} a owl:" in ferm, curie
            elif curie.startswith("uom:"):
                assert curie in PREFER_UOM, curie
            else:
                assert curie in verified, curie


def test_gap_report_cites_only_verified_terms():
    assert cited_curies(load_mapping(COLUMN_MAPPING)) - _verified() == set()
