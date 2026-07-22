<p align="center">
  <img src="docs/icon-256.png" width="112" alt="Second Look icon: a magnifying glass over a capsule">
</p>

# prescription-event-stream

![tests](https://github.com/AidanColvin/prescription-event-stream/actions/workflows/tests.yml/badge.svg)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)
[![live](https://img.shields.io/badge/demo-live-brightgreen)](https://prescription-event-stream.vercel.app)

A prescription safety engine. Every simulated refill event is checked on
the server against federal dispensing rules and screened for drug-drug
interactions before it reaches any screen. The same finding renders three
ways: plain English for patients, a verdict with citations for
pharmacists, and panel alerts for prescribers.

**Live app:** https://prescription-event-stream.vercel.app

![The pharmacist surface stopping a pediatric zolpidem prescription](docs/second-look.png)

## The pages

| Page | Who it serves | What it answers |
| --- | --- | --- |
| [`/`](https://prescription-event-stream.vercel.app/) | Patients and parents | Is my family okay, and what do I do today? |
| [`/pharmacist`](https://prescription-event-stream.vercel.app/pharmacist) | Pharmacists | Can I legally fill this, and why not? |
| [`/md`](https://prescription-event-stream.vercel.app/md) | Prescribers | Is anything from my panel being stopped? |
| [`/how-it-works`](https://prescription-event-stream.vercel.app/how-it-works) | Everyone | Architecture, rules, and diagrams |

Every page has live search. Type a drug name, generic or brand, and a
medication card answers what it is approved to treat, its common
off-label uses, its drug class, and how it works in the body. Type a
class like "benzodiazepine" or a mechanism like "dopamine" and the
matching drugs surface. Search answers for **any** drug: names outside
the family's data fall through to the live FDA label database via
RxNorm and openFDA. Press `/` to focus search; click any row for full
detail.

## System architecture

```mermaid
flowchart LR
    subgraph Browser
        P1["Patient  /"]
        P2["Pharmacist  /pharmacist"]
        P3["MD  /md"]
        JS["assets/app.js<br/>search controller<br/>filter, cards, 450ms<br/>debounced FDA fallback"]
    end

    subgraph Vercel
        EC["Edge cache<br/>s-maxage 86400"]
        subgraph EV["api/events.py"]
            ING["src/ingestion.py<br/>16 deterministic events"] --> RULES["src/rules/<br/>R1 pediatric · R2 refills · R3 DEA"]
            ING --> SCREEN["interaction screen<br/>per patient, never across"]
            RULES --> SUM["summary computed<br/>read / stopped / cleared"]
            SCREEN --> SUM
        end
        subgraph DR["api/drug.py"]
            VAL["validate term"] --> LBL["openFDA label search"]
            LBL -->|miss| NORM["RxNorm normalize,<br/>retry with ingredient"]
            LBL --> SHAPE["trim to sentences,<br/>strip headings"]
            NORM --> SHAPE
        end
    end

    subgraph Federal["Live sources: NIH / FDA"]
        FDA["openFDA<br/>api.fda.gov"]
        RX["RxNorm<br/>rxnav.nlm.nih.gov"]
        DM["DailyMed<br/>full labels"]
        CFR["eCFR Title 21<br/>rule citations"]
    end

    P1 & P2 & P3 --> JS
    JS -->|"GET /api/events"| EC --> EV
    JS -->|"GET /api/drug?name="| DR
    LBL --> FDA
    NORM --> RX
    SHAPE -.->|links| DM
    SUM -.->|citations| CFR
```

The events pipeline is deterministic and self-contained: same queue,
same verdicts, every request. The drug lookup reaches the live federal
databases, shapes the label server-side, and caches at the edge for a
day so repeat queries never re-hit the upstream APIs.

### A search for a drug nobody here takes

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant P as Page (app.js)
    participant E as Vercel edge
    participant D as api/drug.py
    participant R as RxNorm
    participant F as openFDA

    U->>P: types "xanax"
    P->>P: no match in family data
    Note over P: 450 ms debounce, per-query cache
    P->>E: GET /api/drug?name=xanax
    E->>D: cache miss
    D->>F: label search, generic OR brand
    alt label miss
        D->>R: approximateTerm to ingredient
        D->>F: retry with normalized name
    end
    F-->>D: FDA label JSON
    D-->>E: shaped card, cached 24h
    E-->>P: class, mechanism, uses, links
    P-->>U: "From the FDA label database" card
```

## Rule engine

Each rule is one function in `src/rules/` that takes an event and
returns a `Finding` or `None`. A `Finding` carries one message per
audience, so the same object renders on every surface without any rule
knowing which surface is asking.

| Rule | Checks | Severity | Citation |
| --- | --- | --- | --- |
| R1 | Patient age against the label minimum | blocked | DailyMed SPL 8.4 |
| R2 | Refill count and total days supply against the schedule cap | blocked | 21 CFR 1306.12, 1306.22 |
| R3 | DEA registration presence and check digit | blocked | 21 CFR 1301.13, 1306.03 |

On the current synthetic queue the engine reads 16 prescriptions, clears
13, and stops 3:

- **R1 and R2.** James Smith, age 11, holds a 10 mg zolpidem prescription
  written for 90 tablets with 4 refills. No pediatric indication exists,
  and 450 authorized days exceeds the 180 day Schedule IV window.
- **R3.** A Schedule IV tramadol prescription has no DEA registration
  recorded for its prescriber.
- **R3.** A Schedule IV temazepam prescription carries a registration
  that fails the DEA check digit.

The DEA check digit is real arithmetic, not a lookup: the sum of the
first, third, and fifth digits plus twice the sum of the second, fourth,
and sixth must end in the seventh digit. R2 does real dosage math too,
parsing the sig to get doses per day before computing days supply, so
90 tablets taken twice daily is 45 days, not 90.

![Rule engine](docs/rule-engine.svg)

![Pharmacist surface before and after](docs/pharmacist-before-after.svg)

## Drug interaction screen

The server screens each patient's full regimen for known drug-drug
interactions. The screen runs per person, since an interaction is a
property of two prescriptions in one body, never of the queue. Each
finding carries a severity, the clinical mechanism, a plain-language
version for patients, and a suggested action, sourced from AHFS Drug
Information and FDA prescribing information.

On the current queue it finds three:

| Severity | Pair | Patient | Risk |
| --- | --- | --- | --- |
| Major | Sertraline + Tramadol | Mary Smith | Serotonin syndrome |
| Moderate | Sertraline + Ibuprofen | Mary Smith | GI bleeding |
| Moderate | Omeprazole + Warfarin | Patricia Johnson | Elevated INR |

Warfarin + ibuprofen is a known major interaction but never fires here:
those prescriptions belong to different patients, and a test asserts the
screen never pairs drugs across people.

![Drug interaction screen](docs/interaction-screen.svg)

## Medication knowledge

Every medication answers the questions a patient actually asks:

- **Approved to treat** — FDA-approved indications
- **Common off-label uses** — stated honestly, including "none commonly
  recognized" where that is the truth
- **Drug class** — benzodiazepine, SSRI, statin, ACE inhibitor
- **How it works** — the mechanism in one sentence: raises dopamine and
  norepinephrine, boosts GABA at the GABA-A receptor, blocks histamine H1

All four fields render on the medication card and in row details, and
all four are searchable.

Two data tiers, stated honestly: the family's 16 medications are
hand-curated for plain-English readability; every other drug comes from
the live FDA label via `/api/drug`, trimmed to sentences but never
rewritten, with a link to the full label on DailyMed.

## Design decisions

- **Nothing on any screen is hardcoded.** The clearance line, the stat
  counts, the verdict cards, and the interaction list are all computed
  from the payload. A test asserts `cleared == read - stopped`.
- **Verdict first, evidence second.** The pharmacist surface leads with
  "Do not fill." and numbers its reasons, each with a citation link.
  Red is reserved for blocked; if everything is red, nothing is.
- **One object, three audiences.** Rules produce messages for all three
  surfaces at once, which keeps the surfaces from drifting apart.
- **Data honesty.** The interface once carried a green badge reading
  "SECURE U.S. CLINICAL STREAM." The data is synthetic and the app makes
  no security claim, so the badge is gone. A gray line on every page
  states what the data actually is.
- **No framework.** Four static pages, one shared stylesheet, one shared
  script. The deploy cannot fail on a build because there is no build.

## Quick start

```bash
python3 scripts/serve.py 8099    # static pages + /api/events on :8099
```

```bash
python3 -m unittest discover -s tests    # 33 tests
```

CI runs the full suite on every push. Coverage spans the ingestion and
transform pipeline, all three rules, the clinical math (age, sig
parsing, days supply), the DEA checksum, the interaction screen
including its cross-patient safeguard, the computed queue summary, and
the label shaping for live lookups, which is tested against canned FDA
labels so the suite never needs a network.

## Project structure

```
api/events.py            serverless function serving the evaluated queue
api/drug.py              serverless function for live FDA label lookup
src/ingestion.py         deterministic synthetic roster, 16 events
src/transform.py         evaluates events, attaches findings and summary
src/rules/               one file per rule + the interaction screen
src/constants/           age floors, schedule limits, interaction pairs
src/drug_lookup.py       RxNorm + openFDA client and label shaping
assets/                  shared stylesheet and search/render helpers
index.html, pharmacist/, md/, how-it-works/    the four surfaces
tests/                   unittest suite, run by CI on every push
docs/                    diagrams and screenshots used here
```

## Deployment

Deploys on Vercel with zero configuration: static files from the project
root, `api/*.py` as Python serverless functions. No build step, no
environment variables.
