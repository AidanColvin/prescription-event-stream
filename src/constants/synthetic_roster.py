"""Constants for the synthetic benchmark roster.

The generator draws mostly from the family's curated medications and a
weighted tail of other common generic names the live lookup path already
handles. A planned fraction of events is built to trip each rule, so the
benchmark exercises the full engine, not just the clear path.
"""

# Share of generated events built to trip each rule.
R1_VIOLATION_FRACTION: float = 0.05
R2_VIOLATION_FRACTION: float = 0.05
R3_VIOLATION_FRACTION: float = 0.05

# Share of events whose drug comes from the tail rather than the curated
# set. The remainder keep their curated drug, so curated names dominate.
TAIL_DRUG_FRACTION: float = 0.30

# Target prescriptions per synthetic patient. A real regimen is a handful
# of drugs, so the interaction screen stays bounded per patient and the
# whole engine scales linearly with the event count.
MED_EVENTS_PER_PATIENT: int = 4

# Common generic names outside the curated family, handled live by RxNorm
# and openFDA in the deployed app.
TAIL_DRUG_NAMES: "tuple[str, ...]" = (
    "Gabapentin", "Hydrochlorothiazide", "Losartan", "Simvastatin",
    "Escitalopram", "Montelukast", "Pantoprazole", "Furosemide",
    "Metoprolol Succinate", "Prednisone", "Citalopram", "Duloxetine",
    "Bupropion", "Clopidogrel", "Rosuvastatin", "Fluoxetine",
)

# Drugs used to build each rule violation deterministically.
R1_DRUG: str = "Zolpidem Tartrate"
R2_DRUG: str = "Temazepam"
R3_DRUG: str = "Tramadol HCl"

# A registration that fails the DEA check digit, used for R3 violations.
INVALID_DEA_NUMBER: str = "MH5502841"
