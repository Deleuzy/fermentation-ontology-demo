import csv

import pytest

from ferm_demo.convert import convert, load_ontology
from ferm_demo.paths import BROKEN_CSV, ONTOLOGY, RUNS_CSV


@pytest.fixture(scope="session")
def onto():
    return load_ontology(ONTOLOGY)


@pytest.fixture(scope="session")
def good():
    return convert(RUNS_CSV)


@pytest.fixture(scope="session")
def broken():
    return convert(BROKEN_CSV)


@pytest.fixture(scope="session")
def rows():
    with RUNS_CSV.open(newline="") as fh:
        return list(csv.DictReader(fh))
