# prescription-event-stream

A demo that streams simulated prescription refill events, gives every
prescription a second look against federal dispensing rules, and renders
the result on three surfaces — patient, pharmacist, and prescriber — in
the language each reader needs.

**Live app:** https://prescription-event-stream.vercel.app

| Page | Who it serves | What it answers |
| --- | --- | --- |
| `/` | Patients and parents | Is my family okay, and what do I do today? |
| `/pharmacist` | Pharmacists | Can I legally fill this, and why not? |
| `/md` | Prescribers | Is anything from my panel being stopped? |
| `/how-it-works` | Everyone | Architecture, rules, and diagrams |

Every page has live search across patient, medication, brand, schedule,
indication, and prescriber. Press `/` to focus the search box; click any
row or card for full detail.

## Rule engine

Every event is evaluated on the server before it reaches the browser.
Three rules ship today. Each is one function in `src/rules/` that takes
an event and returns a `Finding` or `None`.

| Rule | Checks | Severity | Citation |
| --- | --- | --- | --- |
| R1 | Patient age against the label minimum | blocked | DailyMed SPL 8.4 |
| R2 | Refill count and total days supply against the schedule cap | blocked | 21 CFR 1306.12, 1306.22 |
| R3 | DEA registration presence and check digit | blocked | 21 CFR 1301.13, 1306.03 |

A `Finding` carries one message per audience, so the same object renders
on the pharmacist, patient, and prescriber surfaces without any rule
knowing which surface is asking.

On the current synthetic queue the engine reads 16 prescriptions, clears
13, and stops 3:

- **R1 and R2.** James Smith, age 11, holds a 10 mg zolpidem prescription
  written for 90 tablets with 4 refills. No pediatric indication exists,
  and 450 authorized days exceeds the 180 day Schedule IV window.
- **R3.** A Schedule IV tramadol prescription has no DEA registration
  recorded for its prescriber.
- **R3.** A Schedule IV temazepam prescription carries a registration
  that fails the DEA check digit.

The pharmacist surface shows only what was stopped, above a computed
count of what cleared. Nothing on any screen is hardcoded.

![Rule engine](docs/rule-engine.svg)

![Pharmacist surface before and after](docs/pharmacist-before-after.svg)

## Drug interaction screen

Alongside the per-prescription rules, the server screens each patient's
full regimen for known drug-drug interactions. The screen runs per
person — an interaction is a property of two prescriptions in one body,
never of the queue — and each finding carries a severity, the clinical
mechanism, a plain-language version for patients, and a suggested
action, sourced from AHFS Drug Information and FDA prescribing
information.

On the current queue it finds three:

| Severity | Pair | Patient | Risk |
| --- | --- | --- | --- |
| Major | Sertraline + Tramadol | Mary Smith | Serotonin syndrome |
| Moderate | Sertraline + Ibuprofen | Mary Smith | GI bleeding |
| Moderate | Omeprazole + Warfarin | Patricia Johnson | Elevated INR |

Warfarin + ibuprofen is a known major interaction but never fires here:
those prescriptions belong to different patients, and a test asserts
the screen never pairs drugs across people.

![Drug interaction screen](docs/interaction-screen.svg)

## Medication knowledge

Every medication answers two questions a patient actually asks: what is
this approved to treat, and what else is it commonly prescribed for?
Each roster entry carries `approved_uses` (FDA-approved indications)
and `off_label` (commonly recognized off-label uses, stated honestly —
including "none commonly recognized" where that is the truth). Both
render in the expandable detail on the patient and MD views and are
reachable from every search box.

## Data honesty

The interface previously carried a green badge reading SECURE U.S.
CLINICAL STREAM. The application uses synthetic records and makes no
security claim, so the badge is gone. A gray line on every page states
what the data actually is: synthetic demonstration data, no real
patients.

## How it works

- `src/ingestion.py` — the deterministic synthetic roster. Same queue on
  every request, so every count on every screen is reproducible.
- `src/rules/` — the engine. One file per rule; adding a rule means
  writing one function and registering it in `REGISTERED_RULES`.
  `interactions.py` holds the per-patient drug-drug interaction screen.
- `src/transform.py` — evaluates each event and attaches findings,
  verdicts, DEA status, and a computed queue summary.
- `api/events.py` — a Python serverless function on Vercel serving the
  evaluated queue as JSON at `/api/events`.
- `index.html`, `pharmacist/`, `md/`, `how-it-works/` — static pages,
  no framework and no build step, sharing one stylesheet in `assets/`.

## Run it locally

```bash
python3 scripts/serve.py 8099   # static pages + /api/events
```

## Run the tests

```bash
python3 -m unittest discover -s tests
```

Covers the ingestion and transform pipeline, all three rules, the
clinical math (age, sig parsing, days supply), the DEA checksum, the
drug interaction screen, and the computed queue summary.

## Deployment

The project deploys on Vercel with zero configuration: static files are
served from the project root and `api/*.py` run as Python serverless
functions. No build step, no environment variables.
