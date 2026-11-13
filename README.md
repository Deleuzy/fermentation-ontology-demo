# fermentation-ontology-demo

A small learning demo of semantic web work on precision fermentation data. It
has a small OWL ontology for fermentation runs built on
[PREFER](https://github.com/Multiomics-Analytics-Group/prefer_ontology), the
precision fermentation ontology, and aligned to BFO, a LinkML metadata
template, a script that turns a CSV of runs into RDF with provenance for every
triple, SPARQL queries, SHACL shapes, a gap report, tests and CI.

I built it to practise the tools a standards office uses (OWL, RDF, SPARQL,
OBO terms, LinkML, SHACL, ROBOT) on a domain close to precision fermentation.
All data is synthetic and the scope is a toy. See "What this is not" below.

## What is in the repo

| Path | What it is |
|---|---|
| `ontology/ferm.ttl` | The OWL ontology (Turtle), with ontology IRI and version IRI |
| `ontology/external_terms.json` | Every external IRI, the label the EBI Ontology Lookup Service (OLS) returned, and whether it matched |
| `ontology/column_mapping.yaml` | How each CSV column maps to terms, which existing terms were checked and why they were not used |
| `scripts/verify_terms.py` | Looks up each external IRI in OLS and writes `external_terms.json` |
| `data/runs.csv` | 12 synthetic runs that meet the required metadata |
| `data/broken_runs.csv` | 1 synthetic run with three planted faults |
| `schema/run_metadata.yaml` | LinkML schema for the run metadata template |
| `schema/run_metadata.schema.json` | JSON Schema generated from the LinkML schema |
| `shapes/run_shapes.ttl` | SHACL shapes for required metadata and value ranges |
| `queries/*.rq` | Five SPARQL queries |
| `src/ferm_demo/` | Converter, checks, gap report and the pipeline that writes `results/` |
| `results/results.json` | Every number in this README comes from here |
| `results/gap_report.md` | Columns that needed new terms, with the proposed terms |
| `mappings/ferm.sssom.tsv` | SSSOM mappings: FERM gap terms to PREFER and IAO, and UO units to the uom units PREFER uses |
| `docs/fair_checklist.md` | Self check against the FAIR principles, including what is missing |

## How to run

Needs Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

```bash
uv run python -m ferm_demo.pipeline
```

```bash
uv run pytest
```

```bash
uv run ruff check .
```

The pipeline writes `build/instances.ttl` and `build/provenance.ttl`, then
`results/results.json` and `results/gap_report.md`, and refreshes the results
block in this README. A test fails if any of these are stale.

`scripts/verify_terms.py` needs network access, so it is run by hand, not in CI.
Tests check that every external IRI in the ontology is listed as verified in
its saved output.

## Ontology design

* **PREFER first.** Every CSV column was first looked up in PREFER (release
  2026-08-24). A run is a PREFER `fermentation run` (PREFER:0000004), the
  strain a `cell biocatalyst` (PREFER:0000012), and the medium and bioreactor
  are PREFER `fermentation medium` and `bioreactor`. Operation mode,
  temperature, pH, initial culture volume and titer are PREFER process
  variables. Runs link to them with PREFER relations (`uses bioreactor`,
  `cultures cell`, `has measured process variable`).
* **Upper level.** PREFER places a run under `precision fermentation process`,
  then `planned process` (COB:0000082) and BFO `process` (BFO:0000015).
  Bioreactors, media and cells are material entities (BFO:0000040), and
  process variables are information content entities (IAO:0000030).
* **Other reused terms.** NCBITaxon for organisms (each strain is also typed
  with its species class), ChEBI for carbon sources, UO for units, IAO for
  values, definitions and `is about`, OBI `has specified output` for the
  product.
* **New terms only for gaps.** Three columns had no fitting term, so the
  ontology adds `target product`, `run duration datum` and `has carbon source`
  (a subproperty of PREFER `has medium ingredient`). The gap report lists what
  was checked for each.
* **Checked IRIs.** Every external IRI was looked up in OLS (Nov 2026) and its
  label compared with the expected one. This also showed that OBI has made
  `organism` (OBI:0100026) and `planned process` (OBI:0000011) obsolete in
  favour of COB terms.
* **No full imports.** External terms are declared as small stubs with a label,
  their superclass and `imported from`, in the spirit of MIREOT. Intermediate
  PREFER classes are collapsed. A real build would extract modules with ROBOT
  or use the Ontology Development Kit (ODK), which PREFER itself uses.
* **Just enough disjointness.** Three BFO disjointness axioms (process,
  material entity, generically dependent continuant). That is enough for a
  reasoner to reject a run that is also typed as a bioreactor, which the tests
  plant on purpose.
* **Provenance.** Each data triple is also written as an `rdf:Statement` with
  `prov:wasDerivedFrom` pointing at the CSV cell it came from, using RFC 7111
  fragments (`runs.csv#cell=row,col`, header is row 1). A test reads every
  measured value back from the cell its provenance names.

## Where the demo departs from PREFER

* **Operation mode.** PREFER links the mode to the bioreactor
  (`has operational mode`). In the data one bioreactor runs batch on one run and
  fed-batch on another, so here the mode is a PREFER mode individual that `is
  about` the run.
* **Units and values.** PREFER uses w3id.org/uom units and value
  specifications. The demo uses UO units with IAO `has measurement value`, the
  older OBI pattern.
* **Taxon.** PREFER models taxon as a quality with a few species. The demo
  types each strain with its NCBITaxon class instead.

## Known gaps in the model

* A strain is modelled as one cell. Strictly it is a population or lineage.
* `has carbon source` says which ingredient is the carbon source, but a carbon
  source role on the ingredient, next to PREFER `fermentation medium role`
  (PREFER:0000108), would be cleaner.
* Target products are FERM `target product` individuals with a text label. They
  should point to Protein Ontology terms, which I did not verify. PREFER issue
  70 on product classification is open.
* Temperature and pH are single mean values per run, not time series.
* FERM IRIs live under the GitHub URL and do not resolve.
* The OWL RL check run locally is weaker than a full DL reasoner. HermiT runs
  in CI (through owlready2 and ROBOT), where Java is available.

## Quality checks

* **OWL RL reasoning** (`owlrl`, pure Python) over ontology plus data, a
  satisfiability probe for each FERM class, and a planted inconsistency that
  must be caught.
* **HermiT** in CI through owlready2 (the test is skipped without Java), and
  ROBOT `reason` with HermiT. ROBOT `report` runs in CI and fails the build on
  any ERROR level problem; its TSV is uploaded as a build artifact and is not
  used for any number here.
* **Mappings**: a test checks that the SSSOM file uses SKOS predicates and only
  cites FERM terms in the ontology or external terms verified in OLS.
* **SHACL** (`pyshacl`): required links (strain, bioreactor, medium, product,
  temperature, pH, run mode), NCBITaxon typing of strains, carbon source on
  media, value ranges and units.
* **LinkML**: the CSV is validated against the schema, and against the JSON
  Schema generated from it. A test checks the JSON Schema is current.
* **Gap report**: `results/gap_report.md` lists each CSV column that no existing
  term covered, what was checked in OLS, and the proposed FERM term.

## Results

<!-- results:start -->
<!-- generated by `uv run python -m ferm_demo.pipeline` from results/results.json -->

| What | Number |
|---|---|
| Classes in `ferm.ttl` (FERM / reused) | 36 (2 / 34) |
| Properties (FERM / reused) | 14 (1 / 13) |
| Triples in `ferm.ttl` | 231 |
| External IRIs looked up in OLS / verified | 78 / 78 |
| External IRIs used in the ontology but not verified | 0 |
| CSV rows converted | 12 |
| Instance triples | 387 |
| Provenance records (one per derived triple and source cell) | 460 |
| OWL RL errors on ontology plus data | 0 |
| OWL RL errors after planting a run typed as a bioreactor | 1 |
| SHACL violations, `runs.csv` | 0 |
| SHACL violations, `broken_runs.csv` | 3 |
| LinkML errors, `runs.csv` / `broken_runs.csv` | 0 / 3 |
| CSV columns needing a new term (gap report) | 3 of 14 |

SHACL messages for the broken record:

* `datum/B01/pH`: pH must be one decimal value between 0 and 14.
* `run/B01`: A run needs a fermentation medium as participant.
* `strain/S99`: A cell biocatalyst (strain) must be typed with an NCBITaxon class.

Query `01_runs_per_organism.rq`:

| taxon | organism | runs |
|---|---|---|
| NCBITaxon_460519 | Komagataella phaffii | 3 |
| NCBITaxon_4932 | Saccharomyces cerevisiae | 3 |
| NCBITaxon_1423 | Bacillus subtilis | 2 |
| NCBITaxon_562 | Escherichia coli | 2 |
| NCBITaxon_51453 | Trichoderma reesei | 2 |

Query `02_mean_titre_per_carbon_source.rq`:

| carbon_source | unit | n_with_titre | mean_titre |
|---|---|---|---|
| methanol | gram per liter | 2 | 4.9 |
| glucose | gram per liter | 5 | 3.52 |
| sucrose | gram per liter | 3 | 0.97 |

Query `03_runs_missing_titre.rq`:

| run_label |
|---|
| fermentation run R06 |
| fermentation run R10 |

Query `04_runs_using_methanol.rq`:

| run_label | organism |
|---|---|
| fermentation run R04 | Komagataella phaffii |
| fermentation run R05 | Komagataella phaffii |

Query `05_titre_by_mode.rq`:

| mode | n_with_titre | mean_titre | max_titre |
|---|---|---|---|
| batch operation mode | 3 | 0.9 | 1.2 |
| fed-batch operation mode | 7 | 3.94 | 7.9 |

<!-- results:end -->

## What this is not

* **Not part of PREFER.** It reuses PREFER terms by IRI but is not a PREFER
  module and was not reviewed by its curators.
* **Not real data.** Every run, strain, medium and titre in `data/` is made up.
  The query results describe the synthetic data and say nothing about real
  organisms or processes.
* **Not an OBO Foundry ontology.** No PURL, no ODK repo, no release pipeline,
  no community review.
* **Toy scope.** A few FERM terms, a few queries and a dozen runs, as the
  results table shows. Enough to show the workflow, not to model a field.

## License

Code: MIT. Ontology and data: CC BY 4.0.
