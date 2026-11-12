"""Ontology quality checks that need no Java.

* term_stats: counts of declared classes and properties, FERM vs external.
* external_iri_problems: every obo IRI in the ontology must be listed as
  verified in ontology/external_terms.json (written by scripts/verify_terms.py).
* missing_metadata: every FERM term needs a label and a definition.
* owl_rl_errors: run the OWL 2 RL rules (owlrl) and return the inconsistencies
  they find. OWL RL is weaker than a full DL reasoner such as HermiT, which
  runs in CI through ROBOT (see .github/workflows/ci.yml).
"""

from __future__ import annotations

import json
from pathlib import Path

import owlrl
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS

from . import namespaces as ns

OBO_PREFIX = str(ns.OBO)
FERM_PREFIX = str(ns.FERM)
DEFINITION = ns.OBO.IAO_0000115
OWLRL_ERROR = URIRef("http://www.daml.org/2002/03/agents/agent-ont#error")


def _declared(g: Graph, kind: URIRef) -> set[URIRef]:
    return {s for s in g.subjects(RDF.type, kind) if isinstance(s, URIRef)}


def term_stats(onto: Graph) -> dict[str, int]:
    classes = _declared(onto, OWL.Class)
    props = _declared(onto, OWL.ObjectProperty) | _declared(onto, OWL.DatatypeProperty) | _declared(onto, OWL.AnnotationProperty)
    ferm = lambda xs: {x for x in xs if str(x).startswith(FERM_PREFIX)}  # noqa: E731
    obo = lambda xs: {x for x in xs if str(x).startswith(OBO_PREFIX)}  # noqa: E731
    return {
        "ontology_triples": len(onto),
        "classes": len(classes),
        "ferm_classes": len(ferm(classes)),
        "external_classes": len(obo(classes)),
        "properties": len(props),
        "ferm_properties": len(ferm(props)),
        "external_properties": len(obo(props)),
        "unit_individuals": len(_declared(onto, OWL.NamedIndividual)),
        "subclass_axioms": len(list(onto.triples((None, RDFS.subClassOf, None)))),
        "existential_restrictions": len(list(onto.triples((None, OWL.someValuesFrom, None)))),
        "disjointness_axioms": len(list(onto.triples((None, OWL.disjointWith, None)))),
    }


def ontology_obo_iris(onto: Graph) -> set[str]:
    iris = set()
    for triple in onto:
        for term in triple:
            if isinstance(term, URIRef) and str(term).startswith(OBO_PREFIX) and "_" in str(term):
                local = str(term)[len(OBO_PREFIX) :]
                if not local.endswith(".owl"):
                    iris.add(str(term))
    return iris


def external_iri_problems(onto: Graph, terms_file: Path) -> list[str]:
    rows = json.loads(terms_file.read_text())
    verified = {r["iri"] for r in rows if r["verified"]}
    return sorted(ontology_obo_iris(onto) - verified)


def missing_metadata(onto: Graph) -> list[str]:
    problems = []
    terms = _declared(onto, OWL.Class) | _declared(onto, OWL.ObjectProperty) | _declared(onto, OWL.DatatypeProperty)
    for t in sorted(terms):
        if onto.value(t, RDFS.label) is None:
            problems.append(f"{t} has no label")
        if str(t).startswith(FERM_PREFIX) and onto.value(t, DEFINITION) is None:
            problems.append(f"{t} has no definition")
    return problems


def owl_rl_errors(graph: Graph) -> list[str]:
    g = Graph()
    for t in graph:
        g.add(t)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics, rdfs_closure=False, axiomatic_triples=False, datatype_axioms=False).expand(g)
    return sorted(str(o) for o in g.objects(None, OWLRL_ERROR))


def unsatisfiable_ferm_classes(onto: Graph) -> list[str]:
    """Probe each FERM class with a fresh individual; report classes that cause an OWL RL error."""
    bad = []
    for cls in sorted(c for c in _declared(onto, OWL.Class) if str(c).startswith(FERM_PREFIX)):
        g = Graph()
        for t in onto:
            g.add(t)
        g.add((BNode(), RDF.type, cls))
        if owl_rl_errors(g):
            bad.append(str(cls))
    return bad
