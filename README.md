# prescription-event-stream

A small demo that streams and processes simulated prescription
medication refill events, with a clean public web interface.

## Live app

- **Frontend:** `/` — an auto-refreshing dashboard of recent events.

## How it works

- `index.html` — a fully self-contained static frontend, styled in a clean,
  Apple-inspired layout. It generates a batch of mock refill events in the
  browser every 5 seconds and renders live stats and a table. The client-side
  ingestion and large-refill transform mirror the modules in `src/`.
- `src/` — the reusable ingestion and transform modules that the frontend logic
  mirrors, covered by the test suite.
- `tests/` — unit tests for the ingestion and transform steps.

## Run the tests

```bash
python -m unittest discover -s tests
```

## Deployment

The project deploys on Vercel with zero configuration:

- Static files (including `index.html`) are served from the project root.
- There is no backend, build step, or runtime dependency, so the deploy
  cannot fail on a build.

No environment variables are required.
