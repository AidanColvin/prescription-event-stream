import random

def get_refill_events():
    """Generates simulated prescription refill events meeting U.S. compliance standards."""
    medications = [
        {
            "generic": "Zolpidem Tartrate", "brand": "Ambien", "class": "Sedative-Hypnotic",
            "indication": "Insomnia", "off_label": "Restless leg syndrome", "schedule": "Schedule IV",
            "sig": "Take 1 tablet by mouth at bedtime.", "strength": "10 mg", "form": "Tablet",
            "interactions": "CNS depressants, alcohol", "contraindications": "Complex sleep behaviors",
            "source": "Drugs@FDA / DailyMed"
        },
        {
            "generic": "Lisinopril", "brand": "Zestril", "class": "ACE Inhibitor",
            "indication": "Hypertension", "off_label": "Migraine prevention", "schedule": "Non-controlled",
            "sig": "Take 1 tablet by mouth daily.", "strength": "20 mg", "form": "Tablet",
            "interactions": "NSAIDs, potassium supplements", "contraindications": "History of angioedema, pregnancy",
            "source": "DailyMed (NIH)"
        },
        {
            "generic": "Metformin HCl", "brand": "Glucophage", "class": "Biguanide",
            "indication": "Type 2 Diabetes", "off_label": "PCOS Management", "schedule": "Non-controlled",
            "sig": "Take 1 tablet by mouth twice daily with meals.", "strength": "500 mg", "form": "Tablet",
            "interactions": "Iodinated contrast media", "contraindications": "Severe renal impairment",
            "source": "Drugs@FDA"
        },
        {
            "generic": "Amphetamine / Dextroamphetamine", "brand": "Adderall", "class": "Central Nervous System Stimulant",
            "indication": "ADHD", "off_label": "Treatment-resistant depression", "schedule": "Schedule II",
            "sig": "Take 1 capsule orally once daily in the morning.", "strength": "20 mg", "form": "Capsule",
            "interactions": "MAOIs, serotonergic drugs", "contraindications": "History of marked anxiety, glaucoma",
            "source": "AHFS / PDR"
        }
    ]
    
    patients = [
        {"name": "Patricia Johnson", "dob": "1988-04-12", "address": "142 Maple St, Raleigh, NC", "phone": "919-555-0192", "insurance": "BlueCross NC (ID: BC99281, Grp: 400)"},
        {"name": "Mary Smith", "dob": "1975-09-23", "address": "810 Oak Ave, Durham, NC", "phone": "919-555-4811", "insurance": "Aetna Healthcare (ID: AET4419, Grp: 102)"},
        {"name": "James Smith", "dob": "2015-02-14", "address": "810 Oak Ave, Durham, NC", "phone": "919-555-4811", "insurance": "Medicaid NC (ID: MED7721, Grp: 88)"}
    ]

    prescribers = [
        {"name": "Dr. Sarah Jenkins, MD", "designation": "MD", "address": "Triangle Medical Center, Chapel Hill, NC", "phone": "919-966-4000", "license": "NC-209381", "dea": "BJ8839201"},
        {"name": "Dr. Robert Chen, DO", "designation": "DO", "address": "Carolina Family Practice, Raleigh, NC", "phone": "919-832-0011", "license": "NC-184920", "dea": "None (Non-controlled)"}
    ]
    
    events = []
    for i in range(1, 13):
        med = random.choice(medications)
        pat = random.choice(patients)
        pres = random.choice(prescribers)
        qty = random.choice([30, 60, 90])
        
        events.append({
            "event_id": f"EVT-{random.randint(100000, 999999)}",
            "patient": pat["name"],
            "dob": pat["dob"],
            "address": pat["address"],
            "phone": pat["phone"],
            "insurance": pat["insurance"],
            "prescriber": pres["name"],
            "designation": pres["designation"],
            "prescriber_address": pres["address"],
            "license": pres["license"],
            "dea": pres["dea"],
            "medication": med["generic"],
            "brand": med["brand"],
            "drug_class": med["class"],
            "indication": med["indication"],
            "off_label": med["off_label"],
            "strength": med["strength"],
            "form": med["form"],
            "quantity": qty,
            "sig": med["sig"],
            "refills_remaining": random.randint(0, 5),
            "next_refill_due": "2026-08-15",
            "dea_schedule": med["schedule"],
            "interactions": med["interactions"],
            "contraindications": med["contraindications"],
            "adherence_score": f"{random.randint(78, 100)}%",
            "source": med["source"]
        })
    return events
