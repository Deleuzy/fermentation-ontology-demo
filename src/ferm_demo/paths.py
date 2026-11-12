"""Repository paths used by the pipeline and the tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY = ROOT / "ontology" / "ferm.ttl"
EXTERNAL_TERMS = ROOT / "ontology" / "external_terms.json"
COLUMN_MAPPING = ROOT / "ontology" / "column_mapping.yaml"
RUNS_CSV = ROOT / "data" / "runs.csv"
BROKEN_CSV = ROOT / "data" / "broken_runs.csv"
SHAPES = ROOT / "shapes" / "run_shapes.ttl"
LINKML_SCHEMA = ROOT / "schema" / "run_metadata.yaml"
JSON_SCHEMA = ROOT / "schema" / "run_metadata.schema.json"
QUERIES = ROOT / "queries"
RESULTS = ROOT / "results"
BUILD = ROOT / "build"
