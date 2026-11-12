import json

import jsonschema

from ferm_demo.linkml_check import csv_to_instance, validate_csv
from ferm_demo.paths import BROKEN_CSV, JSON_SCHEMA, LINKML_SCHEMA, RUNS_CSV, SHAPES
from ferm_demo.shacl import validate_data


def test_shacl_accepts_good_runs(good):
    conforms, violations = validate_data(good.data, SHAPES)
    assert conforms and violations == []


def test_shacl_catches_each_fault_in_broken_record(broken):
    conforms, violations = validate_data(broken.data, SHAPES)
    assert not conforms
    assert [(v.focus.rsplit("/data/", 1)[1], v.message) for v in violations] == [
        ("datum/B01/pH", "pH must be one decimal value between 0 and 14."),
        ("run/B01", "A run needs a culture medium as specified input."),
        ("strain/S99", "A production strain must be typed with an NCBITaxon class."),
    ]


def test_linkml_accepts_good_runs():
    assert validate_csv(RUNS_CSV, LINKML_SCHEMA) == []


def test_linkml_catches_each_fault_in_broken_record():
    errors = validate_csv(BROKEN_CSV, LINKML_SCHEMA)
    assert len(errors) == 3
    assert any("medium_id" in e for e in errors)
    assert any("ncbi_taxon" in e for e in errors)
    assert any("maximum of 14" in e for e in errors)


def test_generated_json_schema_agrees():
    schema = json.loads(JSON_SCHEMA.read_text())
    jsonschema.validate(csv_to_instance(RUNS_CSV), schema)
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(csv_to_instance(BROKEN_CSV)))
    assert len(errors) == 3
