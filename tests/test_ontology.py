import os
import subprocess
import tempfile

import pytest
from rdflib import URIRef
from rdflib.namespace import OWL, RDF, RDFS

from ferm_demo import checks
from ferm_demo import namespaces as ns
from ferm_demo.paths import EXTERNAL_TERMS
from ferm_demo.pipeline import planted_inconsistency

ONTOLOGY_IRI = URIRef("https://github.com/Deleuzy/fermentation-ontology-demo/ferm.ttl")


def test_has_ontology_header_with_version_iri(onto):
    assert (ONTOLOGY_IRI, RDF.type, OWL.Ontology) in onto
    assert onto.value(ONTOLOGY_IRI, OWL.versionIRI) is not None


def test_every_external_iri_was_verified_in_ols(onto):
    assert checks.external_iri_problems(onto, EXTERNAL_TERMS) == []


def test_every_term_has_label_and_ferm_terms_have_definitions(onto):
    assert checks.missing_metadata(onto) == []


def test_fermentation_run_is_a_bfo_process(onto):
    # FERM run -> COB planned process -> BFO process
    assert (ns.FERMENTATION_RUN, RDFS.subClassOf, ns.OBO.COB_0000082) in onto
    assert (ns.OBO.COB_0000082, RDFS.subClassOf, ns.OBO.BFO_0000015) in onto


def test_owl_rl_finds_no_inconsistency(onto, good):
    assert checks.owl_rl_errors(onto + good.data) == []
    assert checks.unsatisfiable_ferm_classes(onto) == []


def test_owl_rl_catches_planted_inconsistency(onto, good):
    errors = planted_inconsistency(onto, good.data)
    assert len(errors) == 1
    assert "BFO_0000015" in errors[0] and "BFO_0000040" in errors[0]


def _java_works() -> bool:
    try:
        return subprocess.run(["java", "-version"], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False


@pytest.mark.skipif(not _java_works(), reason="HermiT needs Java; CI runs it")
def test_hermit_consistency(onto, good):
    import owlready2

    def reason(graph):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ferm.nt")
            graph.serialize(path, format="nt")
            world = owlready2.World()
            world.get_ontology(f"file://{path}").load()
            with world.get_ontology("http://example.org/inferred#"):
                owlready2.sync_reasoner_hermit(world, infer_property_values=False, debug=0)

    reason(onto + good.data)  # raises if inconsistent
    bad = onto + good.data
    bad.add((ns.DATA["run/R01"], RDF.type, ns.BIOREACTOR))
    with pytest.raises(owlready2.OwlReadyInconsistentOntologyError):
        reason(bad)
