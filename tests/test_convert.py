import re
from decimal import Decimal

from rdflib import Literal
from rdflib.namespace import RDF

from ferm_demo import namespaces as ns


def _provenance_index(prov):
    index = {}
    for stmt in prov.subjects(RDF.type, RDF.Statement):
        triple = (prov.value(stmt, RDF.subject), prov.value(stmt, RDF.predicate), prov.value(stmt, RDF.object))
        index.setdefault(triple, []).append(str(prov.value(stmt, ns.PROV.wasDerivedFrom)))
    return index


def test_one_run_per_row(good, rows):
    runs = set(good.data.subjects(RDF.type, ns.FERMENTATION_RUN))
    assert good.rows == len(rows) == len(runs) == 12


def test_every_triple_has_provenance(good):
    index = _provenance_index(good.provenance)
    missing = [t for t in good.data if t not in index]
    assert missing == []
    assert set(index) == set(good.data)


def test_provenance_points_at_the_right_cell(good, rows):
    """Every measured value must equal the CSV cell its provenance names."""
    index = _provenance_index(good.provenance)
    header = list(rows[0])
    checked = 0
    for (s, p, o), sources in index.items():
        if p != ns.HAS_VALUE:
            continue
        for src in sources:
            row_no, col_no = map(int, re.search(r"#cell=(\d+),(\d+)$", src).groups())
            cell = rows[row_no - 2][header[col_no - 1]]
            assert Decimal(cell) == o.toPython(), (s, src)
            checked += 1
    # 12 rows x 5 measurement columns, minus 2 missing titres
    assert checked == 58


def test_missing_cells_produce_no_triples(good):
    titre_r06 = ns.DATA["datum/R06/titre_g_per_L"]
    assert (titre_r06, None, None) not in good.data


def test_values_are_typed_decimals(good):
    for o in good.data.objects(None, ns.HAS_VALUE):
        assert isinstance(o, Literal) and o.datatype.endswith("#decimal")
