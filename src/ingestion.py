import random
import time
import uuid

MEDICATIONS = [
    {
        "generic": "Zolpidem Tartrate", "brand": "Ambien", "class": "Sedative-Hypnotic", 
        "indication": "Insomnia", "off_label": "Restless leg syndrome", 
        "schedule": "IV", "moa": "GABA-A receptor agonist", 
        "contraindications": "Complex sleep behaviors", 
        "sig": "Take 1 tablet by mouth at bedtime.", "storage": "Store at room temperature.", 
        "side_effects": "Dizziness, daytime drowsiness.", "interactions": "CNS depressants.",
        "substitution": "Generic substitution permitted.", "source": "Drugs@FDA"
    },
    {
        "generic": "Lisinopril", "brand": "Zestril", "class": "ACE Inhibitor", 
        "indication": "Hypertension", "off_label": "Migraine prevention", 
        "schedule": "Rx", "moa": "Inhibits angiotensin-converting enzyme", 
        "contraindications": "History of angioedema", 
        "sig": "Take 1 tablet by mouth daily.", "storage": "Keep dry at room temperature.", 
        "side_effects": "Dry cough, dizziness.", "interactions": "NSAIDs, potassium supplements.",
        "substitution": "Generic substitution permitted.", "source": "DailyMed (NIH)"
    },
    {
        "generic": "Metformin HCl", "brand": "Glucophage", "class": "Biguanide", 
        "indication": "Type 2 Diabetes", "off_label": "PCOS", 
        "schedule": "Rx", "moa": "Decreases hepatic glucose production", 
        "contraindications": "Severe renal impairment", 
        "sig": "Take 1 tablet by mouth twice daily with meals.", "storage": "Store at room temperature.", 
        "side_effects": "Nausea, stomach upset.", "interactions": "Iodinated contrast.",
        "substitution": "Generic substitution permitted.", "source": "Drugs@FDA"
    }
]

def generate_patient():
    firsts = ["James", "Mary", "Robert", "Patricia", "John"]
    lasts = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    return {
        "patient_id": str(uuid.uuid4())[:8].upper(),
        "name": f"{random.choice(firsts)} {random.choice(lasts)}",
        "adherence_score": f"{random.randint(65, 100)}%"
    }

def generate_events(count=20):
    events = []
    current_time = int(time.time())
    for i in range(count):
        med = random.choice(MEDICATIONS)
        qty = random.choice([30, 60, 90])
        event = {
            "event_id": f"EVT-{current_time}-{i:03d}",
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
            "interactions": med["interactions"],
            "substitution": med["substitution"],
            "quantity": qty,
            "source": med["source"],
            "patient_data": generate_patient()
        }
        events.append(event)
    return events
