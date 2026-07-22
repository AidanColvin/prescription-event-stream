"""Prescription refill event ingestion.

Simulates a live clinical refill stream. Every event is generated
deterministically (seeded per index) so the UI sees a stable dataset
across polls — search results don't shuffle underneath the user.

Medication reference fields (indication, sig, schedule, interactions)
are modeled on public FDA / DailyMed structured product labeling.
"""

import random

DRUG_CATALOG = [
    {
        "medication": "Amoxicillin", "brand": "Amoxil", "strength": "500 mg", "form": "Capsule",
        "indication": "Bacterial infections (ear, sinus, throat)",
        "off_label": "H. pylori eradication (combination therapy)",
        "sig": "Take 1 capsule by mouth every 8 hours for 10 days",
        "dea_schedule": "Non-Controlled",
        "interactions": "Warfarin, Methotrexate",
        "contraindications": "Penicillin allergy",
    },
    {
        "medication": "Atorvastatin", "brand": "Lipitor", "strength": "20 mg", "form": "Tablet",
        "indication": "High cholesterol, cardiovascular risk reduction",
        "off_label": "None commonly recognized",
        "sig": "Take 1 tablet by mouth once daily at bedtime",
        "dea_schedule": "Non-Controlled",
        "interactions": "Grapefruit juice, Clarithromycin, Cyclosporine",
        "contraindications": "Active liver disease, Pregnancy",
    },
    {
        "medication": "Lisinopril", "brand": "Zestril", "strength": "10 mg", "form": "Tablet",
        "indication": "High blood pressure, heart failure",
        "off_label": "Post-MI cardioprotection",
        "sig": "Take 1 tablet by mouth once daily",
        "dea_schedule": "Non-Controlled",
        "interactions": "Potassium supplements, NSAIDs, Lithium",
        "contraindications": "History of angioedema, Pregnancy",
    },
    {
        "medication": "Metformin", "brand": "Glucophage", "strength": "500 mg", "form": "Tablet",
        "indication": "Type 2 diabetes",
        "off_label": "Polycystic ovary syndrome (PCOS)",
        "sig": "Take 1 tablet by mouth twice daily with meals",
        "dea_schedule": "Non-Controlled",
        "interactions": "Iodinated contrast, Alcohol",
        "contraindications": "Severe renal impairment (eGFR < 30)",
    },
    {
        "medication": "Levothyroxine", "brand": "Synthroid", "strength": "75 mcg", "form": "Tablet",
        "indication": "Hypothyroidism",
        "off_label": "None commonly recognized",
        "sig": "Take 1 tablet by mouth every morning on an empty stomach",
        "dea_schedule": "Non-Controlled",
        "interactions": "Calcium, Iron supplements, Antacids",
        "contraindications": "Untreated adrenal insufficiency",
    },
    {
        "medication": "Albuterol", "brand": "ProAir HFA", "strength": "90 mcg/actuation", "form": "Inhaler",
        "indication": "Asthma, bronchospasm relief",
        "off_label": "Exercise-induced bronchospasm prevention",
        "sig": "Inhale 2 puffs by mouth every 4-6 hours as needed",
        "dea_schedule": "Non-Controlled",
        "interactions": "Beta-blockers, MAO inhibitors",
        "contraindications": "Hypersensitivity to albuterol",
    },
    {
        "medication": "Omeprazole", "brand": "Prilosec", "strength": "20 mg", "form": "Capsule DR",
        "indication": "GERD, acid reflux, stomach ulcers",
        "off_label": "Laryngopharyngeal reflux",
        "sig": "Take 1 capsule by mouth once daily before breakfast",
        "dea_schedule": "Non-Controlled",
        "interactions": "Clopidogrel, Methotrexate, Diazepam",
        "contraindications": "Concomitant rilpivirine",
    },
    {
        "medication": "Sertraline", "brand": "Zoloft", "strength": "50 mg", "form": "Tablet",
        "indication": "Depression, anxiety disorders",
        "off_label": "Premenstrual dysphoric disorder",
        "sig": "Take 1 tablet by mouth once daily in the morning",
        "dea_schedule": "Non-Controlled",
        "interactions": "MAO inhibitors, NSAIDs, Warfarin",
        "contraindications": "MAOI use within 14 days, Pimozide",
    },
    {
        "medication": "Methylphenidate ER", "brand": "Concerta", "strength": "36 mg", "form": "Tablet ER",
        "indication": "Attention-deficit/hyperactivity disorder (ADHD)",
        "off_label": "Narcolepsy adjunct",
        "sig": "Take 1 tablet by mouth every morning",
        "dea_schedule": "Schedule II (C-II)",
        "interactions": "MAO inhibitors, Clonidine",
        "contraindications": "Glaucoma, Motor tics, Severe anxiety",
    },
    {
        "medication": "Zolpidem", "brand": "Ambien", "strength": "10 mg", "form": "Tablet",
        "indication": "Short-term treatment of insomnia",
        "off_label": "None commonly recognized",
        "sig": "Take 1 tablet by mouth at bedtime as needed",
        "dea_schedule": "Schedule IV (C-IV)",
        "interactions": "CNS depressants, Ketoconazole, Rifampin",
        "contraindications": "Complex sleep behaviors history",
    },
    {
        "medication": "Montelukast", "brand": "Singulair", "strength": "10 mg", "form": "Tablet",
        "indication": "Asthma maintenance, seasonal allergies",
        "off_label": "Chronic urticaria adjunct",
        "sig": "Take 1 tablet by mouth once daily in the evening",
        "dea_schedule": "Non-Controlled",
        "interactions": "Phenobarbital, Rifampin",
        "contraindications": "Hypersensitivity to montelukast",
    },
    {
        "medication": "Amlodipine", "brand": "Norvasc", "strength": "5 mg", "form": "Tablet",
        "indication": "High blood pressure, angina",
        "off_label": "Raynaud phenomenon",
        "sig": "Take 1 tablet by mouth once daily",
        "dea_schedule": "Non-Controlled",
        "interactions": "Simvastatin (dose limit), CYP3A4 inhibitors",
        "contraindications": "Hypersensitivity to amlodipine",
    },
]

PATIENTS = [
    {"name": "Patricia Johnson", "dob": "1958-03-14", "phone": "(919) 555-0142"},
    {"name": "Mary Smith", "dob": "1985-07-22", "phone": "(919) 555-0187"},
    {"name": "James Smith", "dob": "2012-11-05", "phone": "(919) 555-0163"},
]

PRESCRIBERS = [
    {"name": "Dr. Susan Lee, MD", "dea": "BL6428731"},
    {"name": "Dr. Marcus Webb, MD", "dea": "BW3157246"},
    {"name": "Dr. Anita Rao, DO", "dea": "FR8203914"},
]

QUANTITIES = [30, 60, 90, 120]
SOURCES = ["DailyMed SPL", "Drugs@FDA", "AHFS Compendium"]

DEFAULT_BATCH_SIZE = 15


def generate_mock_event(index=0):
    """Build one deterministic refill event for a given stream index."""
    rng = random.Random(1000 + index)
    drug = DRUG_CATALOG[index % len(DRUG_CATALOG)]
    patient = PATIENTS[index % len(PATIENTS)]
    prescriber = PRESCRIBERS[index % len(PRESCRIBERS)]

    quantity = QUANTITIES[rng.randrange(len(QUANTITIES))]
    refills_remaining = rng.randrange(0, 6)
    days_until_due = rng.randrange(1, 29)
    adherence = rng.randrange(68, 100)
    controlled = "Schedule" in drug["dea_schedule"]

    event = {
        "event_id": "RX-2026-%04d" % (1000 + index),
        "patient": patient["name"],
        "dob": patient["dob"],
        "phone": patient["phone"],
        "quantity": quantity,
        "refills_remaining": refills_remaining,
        "next_refill_due": "%d Day%s" % (days_until_due, "" if days_until_due == 1 else "s"),
        "adherence_score": "%d%%" % adherence,
        "prescriber": prescriber["name"],
        "dea": prescriber["dea"],
        "substitution": "Dispense as Written" if controlled else "Permitted (AB-rated)",
        "source": SOURCES[index % len(SOURCES)],
        "patient_data": {
            "name": patient["name"],
            "adherence_score": "%d%%" % adherence,
        },
    }
    event.update(drug)
    return event


def fetch_live_batch(count):
    """Return a batch of `count` refill events."""
    return [generate_mock_event(i) for i in range(count)]


def get_refill_events():
    """Entry point used by the /api/events serverless function."""
    return fetch_live_batch(DEFAULT_BATCH_SIZE)
