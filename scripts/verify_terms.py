"""Look up every external IRI used by the ontology in the EBI Ontology Lookup Service.

Network access is needed, so this is run by hand, not in CI. The output file
ontology/external_terms.json records the label OLS returned for each IRI and
whether the term was found. Tests check the ontology only uses verified IRIs.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ontology" / "external_terms.json"
OBO = "http://purl.obolibrary.org/obo/"

# (CURIE, the label we expect, the ontology whose OLS entry we query)
# (CURIE, expected label, OLS ontology, OLS endpoint, where it is used)
# "used" = declared in ontology/ferm.ttl; "cited" = only named in the column
# mapping or gap report as a term that was checked.
TERMS: list[tuple[str, str, str, str, str]] = [
    ("BFO:0000015", "process", "bfo", "terms", "used"),
    ("BFO:0000031", "generically dependent continuant", "bfo", "terms", "used"),
    ("BFO:0000040", "material entity", "bfo", "terms", "used"),
    ("BFO:0000051", "has part", "ro", "properties", "used"),
    ("IAO:0000030", "information content entity", "iao", "terms", "used"),
    ("IAO:0000109", "measurement datum", "iao", "terms", "used"),
    ("IAO:0000032", "scalar measurement datum", "iao", "terms", "used"),
    ("IAO:0000136", "is about", "iao", "properties", "used"),
    ("IAO:0000004", "has measurement value", "iao", "properties", "used"),
    ("IAO:0000039", "has measurement unit label", "iao", "properties", "used"),
    ("IAO:0000115", "definition", "iao", "properties", "used"),
    ("IAO:0000116", "editor note", "iao", "properties", "used"),
    ("IAO:0000412", "imported from", "iao", "properties", "used"),
    ("RO:0000057", "has participant", "ro", "properties", "used"),
    ("OBI:0000299", "has specified output", "obi", "properties", "used"),
    ("COB:0000022", "organism", "cob", "terms", "used"),
    ("COB:0000082", "planned process", "cob", "terms", "used"),
    ("CL:0000000", "cell", "cl", "terms", "used"),
    # PREFER, the precision fermentation ontology (release 2026-08-24)
    ("PREFER:0000004", "fermentation run", "prefer", "terms", "used"),
    ("PREFER:9000003", "precision fermentation process", "prefer", "terms", "used"),
    ("PREFER:0000011", "fermentation medium", "prefer", "terms", "used"),
    ("PREFER:0000012", "cell biocatalyst", "prefer", "terms", "used"),
    ("PREFER:0000014", "bioreactor", "prefer", "terms", "used"),
    ("PREFER:0000098", "precision fermentation process variable", "prefer", "terms", "used"),
    ("PREFER:9000000", "precision fermentation setpoint process variable", "prefer", "terms", "used"),
    ("PREFER:9000001", "precision fermentation measured process variable", "prefer", "terms", "used"),
    ("PREFER:9000002", "precision fermentation calculated process variable", "prefer", "terms", "used"),
    ("PREFER:0000180", "operation mode setpoint process variable", "prefer", "terms", "used"),
    ("PREFER:0000181", "batch operation mode", "prefer", "terms", "used"),
    ("PREFER:0000182", "fed-batch operation mode", "prefer", "terms", "used"),
    ("PREFER:0000041", "temperature measured process variable", "prefer", "terms", "used"),
    ("PREFER:0000040", "pH measured process variable", "prefer", "terms", "used"),
    ("PREFER:0000036", "initial culture volume measured process variable", "prefer", "terms", "used"),
    ("PREFER:0000091", "titer process metric", "prefer", "terms", "used"),
    ("PREFER:8000004", "has medium ingredient", "prefer", "properties", "used"),
    ("PREFER:8000006", "uses bioreactor", "prefer", "properties", "used"),
    ("PREFER:8000015", "cultures cell", "prefer", "properties", "used"),
    ("PREFER:8000060", "has measured process variable", "prefer", "properties", "used"),
    ("PREFER:0000074", "compound concentration variable", "prefer", "terms", "cited"),
    ("PREFER:0000038", "batch medium pH measured process variable", "prefer", "terms", "cited"),
    ("PREFER:0000043", "volume measured process variable", "prefer", "terms", "cited"),
    ("PREFER:0000203", "production culture", "prefer", "terms", "cited"),
    ("PREFER:8000017", "has measured compound", "prefer", "properties", "cited"),
    ("PREFER:8000018", "has operational mode", "prefer", "properties", "cited"),
    ("PREFER:0000108", "fermentation medium role", "prefer", "terms", "cited"),
    ("PREFER:0000016", "fermentation phase", "prefer", "terms", "cited"),
    ("PREFER:8000059", "measured at time datum", "prefer", "properties", "cited"),
    ("PREFER:0000107", "compound formed variable", "prefer", "terms", "cited"),
    ("PREFER:7000006", "unit of optical density", "prefer", "terms", "cited"),
    ("PREFER:7000007", "dimensionless unit", "prefer", "terms", "cited"),
    ("PREFER:7000008", "revolution per minute", "prefer", "terms", "cited"),
    # Organisms, chemicals, units
    ("NCBITaxon:4932", "Saccharomyces cerevisiae", "ncbitaxon", "terms", "used"),
    ("NCBITaxon:562", "Escherichia coli", "ncbitaxon", "terms", "used"),
    ("NCBITaxon:460519", "Komagataella phaffii", "ncbitaxon", "terms", "used"),
    ("NCBITaxon:1423", "Bacillus subtilis", "ncbitaxon", "terms", "used"),
    ("NCBITaxon:51453", "Trichoderma reesei", "ncbitaxon", "terms", "used"),
    ("CHEBI:17234", "glucose", "chebi", "terms", "used"),
    ("CHEBI:17754", "glycerol", "chebi", "terms", "used"),
    ("CHEBI:17790", "methanol", "chebi", "terms", "used"),
    ("CHEBI:17992", "sucrose", "chebi", "terms", "used"),
    ("UO:0000027", "degree Celsius", "uo", "terms", "used"),
    ("UO:0000032", "hour", "uo", "terms", "used"),
    ("UO:0000175", "gram per liter", "uo", "terms", "used"),
    ("UO:0000196", "pH", "uo", "terms", "used"),
    ("UO:0000099", "liter", "uo", "terms", "used"),
    # Checked and not used
    ("OBI:0000079", "culture medium", "obi", "terms", "cited"),
    ("OBI:0001046", "bioreactor", "obi", "terms", "cited"),
    ("OBI:0000293", "has specified input", "obi", "properties", "cited"),
    ("OBI:0100026", "obsolete organism", "obi", "terms", "cited"),
    ("OBI:0000011", "obsolete planned process", "obi", "terms", "cited"),
    ("GO:0006113", "fermentation", "go", "terms", "cited"),
    ("UO:0010080", "titer", "uo", "terms", "cited"),
    ("UO:0000186", "dimensionless unit", "uo", "terms", "cited"),
    ("UO:0000269", "absorbance unit", "uo", "terms", "cited"),
    ("NCIT:C70469", "Revolution per Minute", "ncit", "terms", "cited"),
    ("MSIO:0000181", "batch cell culture", "msio", "terms", "cited"),
    ("MSIO:0000165", "constantly fed-batch culture reactor", "msio", "terms", "cited"),
    ("NCIT:C210081", "Incubation Temperature", "ncit", "terms", "cited"),
]


def iri(curie: str) -> str:
    prefix, local = curie.split(":")
    return f"{OBO}{prefix}_{local}"


def lookup(term_iri: str, ontology: str, endpoint: str) -> str | None:
    enc = urllib.parse.quote(urllib.parse.quote(term_iri, safe=""), safe="")
    url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology}/{endpoint}/{enc}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.load(resp)
    except Exception:  # noqa: BLE001 - any failure means "not verified"
        return None
    return data.get("label")


def main() -> int:
    rows = []
    for curie, expected, onto, endpoint, used in TERMS:
        label = lookup(iri(curie), onto, endpoint)
        ok = label is not None and label.lower() == expected.lower()
        rows.append(
            {
                "curie": curie,
                "iri": iri(curie),
                "expected_label": expected,
                "ols_label": label,
                "ols_ontology": onto,
                "used_in": used,
                "verified": ok,
            }
        )
        print(f"{'OK ' if ok else 'BAD'} {curie:20} expected={expected!r} ols={label!r}")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2) + "\n")
    bad = [r for r in rows if not r["verified"]]
    print(f"{len(rows) - len(bad)}/{len(rows)} verified")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
