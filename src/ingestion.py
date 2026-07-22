"""Simulates clinical events and runs drug-drug interaction checks."""

import random
import time
import uuid

MEDICATIONS = [
    {
        "generic": "Zolpidem Tartrate", "brand": "Ambien", "class": "Sedative-Hypnotic", 
        "indication": "Insomnia", "off_label": "Restless leg syndrome", 
        "schedule": "Schedule IV", "moa": "GABA-A receptor agonist", 
        "contraindications": "Complex sleep behaviors", 
        "sig": "Take 1 tablet by mouth at bedtime.", "storage": "Store at room temperature.", 
        "side_effects": "Dizziness, daytime drowsiness.", "interaction_tags": ["CNS_DEPRESSANT"],
        "substitution": "Allowed", "source": "Drugs@FDA"
    },
    {
        "generic": "Lisinopril", "brand": "Zestril", "class": "ACE Inhibitor", 
        "indication": "Hypertension", "off_label": "Migraine prevention", 
        "schedule": "Rx Only", "moa": "Inhibits angiotensin-converting enzyme", 
        "contraindications": "History of angioedema", 
        "sig": "Take 1 tablet by mouth daily.", "storage": "Keep dry at room temperature.", 
        "side_effects": "Dry cough, elevated potassium.", "interaction_tags": ["BP_MED"],
        "substitution": "Allowed", "source": "DailyMed (NIH)"
    },
    {
        "generic": "Sertraline HCl", "brand": "Zoloft", "class": "SSRI", 
        "indication": "Depression", "off_label": "Anxiety", 
        "schedule": "Rx Only", "moa": "Inhibits serotonin reuptake", 
        "contraindications": "MAOI use", 
        "sig": "Take 1 tablet daily.", "storage": "Store at room temperature.", 
        "side_effects": "Nausea, insomnia.", "interaction_tags": ["SEROTONERGIC", "CNS_DEPRESSANT"],
        "substitution": "Allowed", "source": "Drugs@FDA"
    }
]

FAMILIES = [
    {"id": "FAM1", "members": [
        {"name": "Robert Smith", "role": "Parent", "diagnoses": ["Hypertension"], "adherence": "92%"},
        {"name": "Mary Smith", "role": "Parent", "diagnoses": ["Insomnia", "Depression"], "adherence": "78%"},
        {"name": "James Smith", "role": "Child", "diagnoses": ["Anxiety"], "adherence": "100%"}
    ]},
    {"id": "FAM2", "members": [
        {"name": "Patricia Johnson", "role": "Parent", "diagnoses": ["Hypertension"], "adherence": "85%"}
    ]}
]

def check_interactions(patient_meds):
    """Interaction Engine: Cross-references active meds for dangers."""
    tags = []
    for med in patient_meds:
        tags.extend(med["interaction_tags"])
    
    if tags.count("CNS_DEPRESSANT") > 1:
        return "CRITICAL: Multiple CNS Depressants prescribed. High risk of respiratory depression."
    return None

def generate_events(count=15):
    """Generates prescription events with interaction mapping."""
    events = []
    current_time = int(time.time())
    
    for family in FAMILIES:
        for patient in family["members"]:
            med_count = random.randint(1, 3)
            patient_meds = random.sample(MEDICATIONS, med_count)
            interaction_alert = check_interactions(patient_meds)
            
            for i, med in enumerate(patient_meds):
                days_until = random.randint(-5, 30)
                event = {
                    "event_id": f"EVT-{current_time}-{str(uuid.uuid4())[:4].upper()}",
                    "family_id": family["id"],
                    "patient_name": patient["name"],
                    "patient_role": patient["role"],
                    "diagnoses": patient["diagnoses"],
                    "medication": med["generic"],
                    "brand_name": med["brand"],
                    "drug_class": med["class"],
                    "indication": med["indication"],
                    "off_label": med["off_label"],
                    "dea_schedule": med["schedule"],
                    "moa": med["moa"],
                    "contraindications": med["contraindications"],
                    "sig": med["sig"],
                    "storage": med["storage"],
                    "side_effects": med["side_effects"],
                    "substitution": med["substitution"],
                    "quantity": random.choice([30, 60, 90]),
                    "source": med["source"],
                    "adherence_score": patient["adherence"],
                    "interaction_alert": interaction_alert,
                    "refill_data": {
                        "total_refills": 12,
                        "refills_remaining": random.randint(0, 5),
                        "days_until_due": days_until,
                        "is_early_refill": days_until > 7
                    }
                }
                events.append(event)
    
    random.shuffle(events)
    return events[:count]
