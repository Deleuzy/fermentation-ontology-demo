"""Convert the run metadata CSV to RDF instances, with provenance for every triple.

Each data triple is also written to a provenance graph as an rdf:Statement with
prov:wasDerivedFrom pointing at the CSV cell it came from, using RFC 7111
fragment identifiers (file.csv#cell=row,col, header line is row 1). Triples
that come from a whole row rather than one cell (for example "R01 is a
fermentation run") point at the row (file.csv#row=n).
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from . import namespaces as ns


@dataclass
class Conversion:
    data: Graph = field(default_factory=Graph)
    provenance: Graph = field(default_factory=Graph)
    rows: int = 0


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _curie_to_iri(curie: str) -> URIRef:
    prefix, local = curie.split(":", 1)
    return ns.OBO[f"{prefix}_{local}"]


def convert(csv_path: Path, source_iri: str | None = None) -> Conversion:
    """Read a run CSV and return data and provenance graphs."""
    source = source_iri or f"https://github.com/Deleuzy/fermentation-ontology-demo/data/{csv_path.name}"
    out = Conversion()
    for g in (out.data, out.provenance):
        g.bind("obo", ns.OBO)
        g.bind("ferm", ns.FERM)
        g.bind("data", ns.DATA)
        g.bind("prov", ns.PROV)

    with csv_path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        columns = reader.fieldnames or []
        col_index = {name: i + 1 for i, name in enumerate(columns)}
        for i, row in enumerate(reader):
            out.rows += 1
            row_no = i + 2  # header is row 1 in RFC 7111 numbering

            def add(s, p, o, column: str | None, row_no: int = row_no) -> None:
                out.data.add((s, p, o))
                frag = f"cell={row_no},{col_index[column]}" if column else f"row={row_no}"
                stmt = BNode()
                prov = out.provenance
                prov.add((stmt, RDF.type, RDF.Statement))
                prov.add((stmt, RDF.subject, s))
                prov.add((stmt, RDF.predicate, p))
                prov.add((stmt, RDF.object, o))
                prov.add((stmt, ns.PROV.wasDerivedFrom, URIRef(f"{source}#{frag}")))

            _convert_row(row, add)
    return out


def _convert_row(row: dict[str, str], add) -> None:
    v = {k: (val or "").strip() for k, val in row.items()}
    run = ns.DATA[f"run/{v['run_id']}"]
    add(run, RDF.type, ns.FERMENTATION_RUN, None)
    add(run, RDFS.label, Literal(f"fermentation run {v['run_id']}"), "run_id")
    if v["mode"]:
        add(run, RDF.type, ns.MODE_CLASS[v["mode"]], "mode")

    if v["strain_id"]:
        strain = ns.DATA[f"strain/{v['strain_id']}"]
        add(strain, RDF.type, ns.PRODUCTION_STRAIN, "strain_id")
        add(strain, RDFS.label, Literal(f"strain {v['strain_id']}"), "strain_id")
        add(run, ns.HAS_PARTICIPANT, strain, "strain_id")
        if v["ncbi_taxon"]:
            add(strain, RDF.type, _curie_to_iri(v["ncbi_taxon"]), "ncbi_taxon")

    if v["bioreactor_id"]:
        reactor = ns.DATA[f"bioreactor/{v['bioreactor_id']}"]
        add(reactor, RDF.type, ns.BIOREACTOR, "bioreactor_id")
        add(reactor, RDFS.label, Literal(f"bioreactor {v['bioreactor_id']}"), "bioreactor_id")
        add(run, ns.HAS_PARTICIPANT, reactor, "bioreactor_id")

    if v["medium_id"]:
        medium = ns.DATA[f"medium/{v['medium_id']}"]
        add(medium, RDF.type, ns.CULTURE_MEDIUM, "medium_id")
        add(medium, RDFS.label, Literal(f"culture medium {v['medium_id']}"), "medium_id")
        add(run, ns.HAS_SPECIFIED_INPUT, medium, "medium_id")
        if v["carbon_source"]:
            portion = ns.DATA[f"medium/{v['medium_id']}/carbon-source"]
            add(portion, RDF.type, ns.CARBON_SOURCE_CLASS[v["carbon_source"]], "carbon_source")
            add(medium, ns.HAS_CARBON_SOURCE, portion, "carbon_source")

    if v["target_product"]:
        product = ns.DATA[f"product/{_slug(v['target_product'])}"]
        add(product, RDF.type, ns.TARGET_PRODUCT, "target_product")
        add(product, RDFS.label, Literal(v["target_product"]), "target_product")
        add(run, ns.HAS_SPECIFIED_OUTPUT, product, "target_product")

    for column, (datum_class, unit) in ns.MEASUREMENT_COLUMNS.items():
        if not v[column]:
            continue
        datum = ns.DATA[f"datum/{v['run_id']}/{column}"]
        add(datum, RDF.type, datum_class, column)
        add(datum, ns.IS_ABOUT, run, column)
        add(datum, ns.HAS_VALUE, Literal(Decimal(v[column]), datatype=XSD.decimal), column)
        add(datum, ns.HAS_UNIT, unit, column)


def load_ontology(path: Path) -> Graph:
    g = Graph()
    g.parse(path, format="turtle")
    return g
