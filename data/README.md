# Data

All data in this folder is synthetic. It was written by hand for this demo and
does not come from any real fermentation, lab or company. The organisms and
products are plausible pairings, but the numbers are made up.

* `runs.csv`: 12 runs that meet the required metadata. Two runs (R06, R10) have
  no titre, which is allowed because titre is recommended, not required.
* `broken_runs.csv`: one run (B01) with three deliberate faults: no NCBI taxon
  for the strain, no medium, and a pH of 15. The SHACL shapes and the LinkML
  schema must both reject it.
