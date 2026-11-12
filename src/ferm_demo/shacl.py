"""SHACL validation of converted run data with pyshacl."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

SH = Namespace("http://www.w3.org/ns/shacl#")


@dataclass
class Violation:
    focus: str
    message: str


def validate_data(data: Graph, shapes_path: Path) -> tuple[bool, list[Violation]]:
    shapes = Graph().parse(shapes_path, format="turtle")
    conforms, report, text = validate(data, shacl_graph=shapes, inference="none")
    if not isinstance(report, Graph):
        raise RuntimeError(f"SHACL validation did not run: {text}")
    violations = [
        Violation(str(report.value(r, SH.focusNode)), str(report.value(r, SH.resultMessage)))
        for r in report.subjects(RDF.type, SH.ValidationResult)
    ]
    violations.sort(key=lambda v: (v.focus, v.message))
    return bool(conforms), violations
