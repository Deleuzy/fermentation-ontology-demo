"""Namespaces and the fixed lookups from CSV values to ontology terms."""

from rdflib import Namespace

OBO = Namespace("http://purl.obolibrary.org/obo/")
FERM = Namespace("https://github.com/Deleuzy/fermentation-ontology-demo/FERM_")
DATA = Namespace("https://github.com/Deleuzy/fermentation-ontology-demo/data/")
PROV = Namespace("http://www.w3.org/ns/prov#")

# PREFER terms (precision fermentation ontology), reused wherever they fit.
FERMENTATION_RUN = OBO.PREFER_0000004
FERMENTATION_MEDIUM = OBO.PREFER_0000011
CELL_BIOCATALYST = OBO.PREFER_0000012
BIOREACTOR = OBO.PREFER_0000014
BATCH_MODE = OBO.PREFER_0000181
FED_BATCH_MODE = OBO.PREFER_0000182
TEMPERATURE_VAR = OBO.PREFER_0000041
PH_VAR = OBO.PREFER_0000040
INITIAL_VOLUME_VAR = OBO.PREFER_0000036
TITER_METRIC = OBO.PREFER_0000091
USES_BIOREACTOR = OBO.PREFER_8000006
CULTURES_CELL = OBO.PREFER_8000015
HAS_MEASURED_VARIABLE = OBO.PREFER_8000060

# FERM terms, only for the gaps in results/gap_report.md.
TARGET_PRODUCT = FERM["0000005"]
DURATION_DATUM = FERM["0000013"]
HAS_CARBON_SOURCE = FERM["0000101"]

HAS_PARTICIPANT = OBO.RO_0000057
HAS_SPECIFIED_OUTPUT = OBO.OBI_0000299
IS_ABOUT = OBO.IAO_0000136
HAS_VALUE = OBO.IAO_0000004
HAS_UNIT = OBO.IAO_0000039

MODE_CLASS = {"batch": BATCH_MODE, "fed-batch": FED_BATCH_MODE}

CARBON_SOURCE_CLASS = {
    "glucose": OBO.CHEBI_17234,
    "glycerol": OBO.CHEBI_17754,
    "methanol": OBO.CHEBI_17790,
    "sucrose": OBO.CHEBI_17992,
}

# CSV column -> (datum class, unit individual, link from the run)
# Measured variables hang off the run with PREFER "has measured process
# variable"; the others point at the run with IAO "is about".
MEASURED = "has measured process variable"
ABOUT = "is about"
MEASUREMENT_COLUMNS = {
    "working_volume_L": (INITIAL_VOLUME_VAR, OBO.UO_0000099, MEASURED),
    "temperature_C": (TEMPERATURE_VAR, OBO.UO_0000027, MEASURED),
    "pH": (PH_VAR, OBO.UO_0000196, MEASURED),
    "duration_h": (DURATION_DATUM, OBO.UO_0000032, ABOUT),
    "titre_g_per_L": (TITER_METRIC, OBO.UO_0000175, ABOUT),
}
