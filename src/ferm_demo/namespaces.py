"""Namespaces and the fixed lookups from CSV values to ontology terms."""

from rdflib import Namespace

OBO = Namespace("http://purl.obolibrary.org/obo/")
FERM = Namespace("https://github.com/Deleuzy/fermentation-ontology-demo/FERM_")
DATA = Namespace("https://github.com/Deleuzy/fermentation-ontology-demo/data/")
PROV = Namespace("http://www.w3.org/ns/prov#")

# Classes and properties, named so the code reads like the ontology.
FERMENTATION_RUN = FERM["0000001"]
BATCH_RUN = FERM["0000002"]
FED_BATCH_RUN = FERM["0000003"]
PRODUCTION_STRAIN = FERM["0000004"]
TARGET_PRODUCT = FERM["0000005"]
TITRE_DATUM = FERM["0000010"]
TEMPERATURE_DATUM = FERM["0000011"]
PH_DATUM = FERM["0000012"]
DURATION_DATUM = FERM["0000013"]
VOLUME_DATUM = FERM["0000014"]
HAS_CARBON_SOURCE = FERM["0000101"]

CULTURE_MEDIUM = OBO.OBI_0000079
BIOREACTOR = OBO.OBI_0001046
HAS_PARTICIPANT = OBO.RO_0000057
HAS_SPECIFIED_INPUT = OBO.OBI_0000293
HAS_SPECIFIED_OUTPUT = OBO.OBI_0000299
IS_ABOUT = OBO.IAO_0000136
HAS_VALUE = OBO.IAO_0000004
HAS_UNIT = OBO.IAO_0000039

MODE_CLASS = {"batch": BATCH_RUN, "fed-batch": FED_BATCH_RUN}

CARBON_SOURCE_CLASS = {
    "glucose": OBO.CHEBI_17234,
    "glycerol": OBO.CHEBI_17754,
    "methanol": OBO.CHEBI_17790,
    "sucrose": OBO.CHEBI_17992,
}

# CSV column -> (datum class, unit individual)
MEASUREMENT_COLUMNS = {
    "working_volume_L": (VOLUME_DATUM, OBO.UO_0000099),
    "temperature_C": (TEMPERATURE_DATUM, OBO.UO_0000027),
    "pH": (PH_DATUM, OBO.UO_0000196),
    "duration_h": (DURATION_DATUM, OBO.UO_0000032),
    "titre_g_per_L": (TITRE_DATUM, OBO.UO_0000175),
}
