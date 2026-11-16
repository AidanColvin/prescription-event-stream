"""Append-only event log for the synthetic roster.

The roster is written once as JSON lines, one event per line, in append
order. Evaluation becomes a fold over the log: replay reads the events in
order and runs each through the rule engine, so reprocessing the queue
costs nothing beyond reading the file. Replay is idempotent. The same log
always folds to the same state.
"""

import json
import os
import tempfile
from dataclasses import dataclass

from src.ingestion import get_refill_events
from src.transform import evaluate_one, shape_payload

DEFAULT_LOG_PATH = os.path.join(tempfile.gettempdir(),
                                "prescription-roster.jsonl")


@dataclass(frozen=True)
class QueueState:
    """The result of folding the log: the evaluated events and how many
    were read."""
    events: "list[dict]"
    offset: int

    def payload(self) -> dict:
        """Returns the API payload shaped from the evaluated events."""
        return shape_payload(self.events)


def append_event(event: dict, path: str = DEFAULT_LOG_PATH) -> None:
    """Takes one raw event. Appends it to the log as a JSON line."""
    with open(path, "a", encoding="utf-8") as log:
        log.write(json.dumps(event) + "\n")


def read_from(offset: int, path: str = DEFAULT_LOG_PATH) -> "list[dict]":
    """Takes an event offset. Returns the raw events from that offset on,
    or an empty list when the log does not exist."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as log:
        lines = [line for line in log if line.strip()]
    return [json.loads(line) for line in lines[offset:]]


def seed_roster_log(path: str = DEFAULT_LOG_PATH) -> None:
    """Writes the roster to the log once. Rewrites it whenever the event
    count drifts from the roster, so a cold start always has the full,
    current queue without duplicating events."""
    roster = get_refill_events()
    if len(read_from(0, path)) == len(roster):
        return
    if os.path.exists(path):
        os.remove(path)
    for event in roster:
        append_event(event, path)


def replay(path: str = DEFAULT_LOG_PATH, limit: "int | None" = None) -> QueueState:
    """Takes the log path. Folds the log into evaluated queue state. An
    optional limit folds only the first events, matching the count the
    events API accepts."""
    raw = read_from(0, path)
    if limit is not None:
        raw = raw[:limit]
    return QueueState([evaluate_one(event) for event in raw], len(raw))


def replay_roster(limit: "int | None" = None,
                  path: str = DEFAULT_LOG_PATH) -> QueueState:
    """Seeds the roster log if needed, then folds it into queue state."""
    seed_roster_log(path)
    return replay(path, limit)
