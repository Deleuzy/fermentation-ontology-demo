"""Run the SPARQL queries in queries/ over the ontology plus instance data."""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph
from rdflib.term import Literal


def _plain(value):
    if value is None:
        return None
    if isinstance(value, Literal):
        py = value.toPython()
        return float(py) if hasattr(py, "as_tuple") else py
    return str(value)


def run_query(graph: Graph, path: Path) -> list[dict]:
    result = graph.query(path.read_text())
    names = [str(v) for v in result.vars]
    return [{n: _plain(row[n]) for n in names} for row in result]


def run_all(graph: Graph, folder: Path) -> dict[str, list[dict]]:
    return {p.stem: run_query(graph, p) for p in sorted(folder.glob("*.rq"))}
