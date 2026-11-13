# FAIR checklist

An honest self check of this demo against the FAIR principles. "Yes" means
the repo does it today; "No" means it does not, with what a real release would
need.

| Principle | Check | Status |
|---|---|---|
| Findable | Every term has a globally unique IRI | Yes for reused terms (OBO PURLs). FERM IRIs are unique but sit under the GitHub URL. |
| Findable | IRIs resolve to a description of the term | No for FERM IRIs. Reused PREFER, IAO, UO, ChEBI and NCBITaxon IRIs resolve through OBO PURLs. A real release would need a PURL (for example via w3id.org). |
| Findable | Rich metadata: labels and definitions | Yes. Every FERM term has a label and an IAO definition; a test enforces it. |
| Findable | Registered in a searchable resource | No. Not in OLS or BioPortal, which is right for a demo. |
| Accessible | Retrievable with an open protocol | Yes. Public GitHub repository over HTTPS. |
| Accessible | Metadata stays available if data goes away | Partly. Git history keeps every version, but there is no archive (for example Zenodo DOI). |
| Interoperable | Formal, shared language | Yes. OWL 2 in Turtle, RDF instances, SPARQL, SHACL, LinkML, SSSOM. |
| Interoperable | Uses FAIR vocabularies | Yes. PREFER, BFO, IAO, RO, OBI, COB, CL, NCBITaxon, ChEBI and UO terms, each looked up in OLS (`ontology/external_terms.json`). |
| Interoperable | Qualified references to other vocabularies | Yes. SKOS mappings in `mappings/ferm.sssom.tsv`, including UO to the uom units PREFER uses. |
| Reusable | Clear license | Yes. Ontology and data CC BY 4.0 (declared in the ontology header and the SSSOM header), code MIT. |
| Reusable | Provenance | Yes for data: every triple points at its CSV cell. Partly for the ontology: external terms carry `imported from`, FERM terms carry no editor or date. |
| Reusable | Versioning | Partly. The ontology has a dated `owl:versionIRI`, but there are no tagged releases and the version IRI does not resolve. |
| Reusable | Community standards | Partly. Follows OBO patterns (IAO definitions, BFO alignment, ROBOT checks in CI) but has no ODK setup and no community review. |
