# fermentation-ontology-demo

A small learning demo of semantic web work on precision fermentation data. It
has a BFO aligned OWL ontology for fermentation runs, a LinkML metadata
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

* **Upper level.** A fermentation run is a `planned process` (COB:0000082),
  which is a BFO `process` (BFO:0000015). Strains are organisms (COB:0000022),
  and bioreactors (OBI:0001046) and culture media (OBI:0000079) are material
  entities (BFO:0000040). Measurements are IAO `scalar measurement datum`
  (IAO:0000032) individuals that are `about` the run and carry a value and a UO
  unit, following the pattern OBI uses.
* **Reused terms.** NCBITaxon for organisms, ChEBI for carbon sources, UO for
  units, OBI and RO relations (`has specified input`, `has specified output`,
  `has participant`), IAO for definitions and data. Strain individuals are typed
  directly with their NCBITaxon class, so "runs per organism" needs no extra
  relation.
* **Checked IRIs.** Every external IRI was looked up in OLS (Nov 2026) and its
  label compared with the expected one. This caught two terms that OBI has made
  obsolete, `organism` (OBI:0100026) and `planned process` (OBI:0000011); the
  ontology uses their COB replacements instead.
* **No full imports.** External terms are declared as small stubs with a label,
  their superclass and `imported from`, in the spirit of MIREOT. A real build
  would extract modules with ROBOT or use the Ontology Development Kit (ODK).
* **Just enough disjointness.** Three BFO disjointness axioms (process,
  material entity, generically dependent continuant) and batch against
  fed-batch. That is enough for a reasoner to reject a run that is also typed
  as a bioreactor, which the tests plant on purpose.
* **Provenance.** Each data triple is also written as an `rdf:Statement` with
  `prov:wasDerivedFrom` pointing at the CSV cell it came from, using RFC 7111
  fragments (`runs.csv#cell=row,col`, header is row 1). A test reads every
  measured value back from the cell its provenance names.

## Known gaps in the model

* A strain is modelled as one organism. Strictly it is a population or lineage.
* `has carbon source` is a subproperty of `has part`. A role based model (the
  chemical bears a carbon source role) would be cleaner.
* Target products are FERM `target product` individuals with a text label. They
  should point to Protein Ontology terms, which I did not verify.
* Temperature and pH are single mean values per run, not time series, and
  there is no link to the device or assay that measured them.
* FERM IRIs live under the GitHub URL and do not resolve. A real ontology
  would get a PURL.
* The OWL RL check run locally is weaker than a full DL reasoner. HermiT runs
  in CI (through owlready2 and ROBOT), where Java is available.

## Quality checks

* **OWL RL reasoning** (`owlrl`, pure Python) over ontology plus data, a
  satisfiability probe for each FERM class, and a planted inconsistency that
  must be caught.
* **HermiT** in CI through owlready2 (the test is skipped without Java), and
  ROBOT `reason` with HermiT. ROBOT `report` runs in CI and its TSV is uploaded
  as a build artifact; it is not used for any number here.
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
| Classes in `ferm.ttl` (FERM / reused) | 29 (10 / 19) |
| Properties (FERM / reused) | 11 (1 / 10) |
| Triples in `ferm.ttl` | 194 |
| External IRIs looked up in OLS / verified | 41 / 41 |
| External IRIs used in the ontology but not verified | 0 |
| CSV rows converted | 12 |
| Instance triples | 375 |
| Provenance records (one per derived triple and source cell) | 448 |
| OWL RL errors on ontology plus data | 0 |
| OWL RL errors after planting a run typed as a bioreactor | 1 |
| SHACL violations, `runs.csv` | 0 |
| SHACL violations, `broken_runs.csv` | 3 |
| LinkML errors, `runs.csv` / `broken_runs.csv` | 0 / 3 |
| CSV columns needing a new term (gap report) | 10 of 14 |

SHACL messages for the broken record:

* `datum/B01/pH`: pH must be one decimal value between 0 and 14.
* `run/B01`: A run needs a culture medium as specified input.
* `strain/S99`: A production strain must be typed with an NCBITaxon class.

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
| batch fermentation run | 3 | 0.9 | 1.2 |
| fed-batch fermentation run | 7 | 3.94 | 7.9 |

<!-- results:end -->

## What this is not

* **Not PREFER.** It does not use, copy or extend the PREFER ontology. It is
  my own small model of the same kind of data.
* **Not real data.** Every run, strain, medium and titre in `data/` is made up.
  The query results describe the synthetic data and say nothing about real
  organisms or processes.
* **Not an OBO Foundry ontology.** No PURL, no ODK repo, no release pipeline,
  no community review.
* **Toy scope.** A few FERM terms, a few queries and a dozen runs, as the
  results table shows. Enough to show the workflow, not to model a field.

## License

Code: MIT. Ontology and data: CC BY 4.0.
