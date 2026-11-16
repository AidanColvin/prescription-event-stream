import json
import os
import tempfile
import unittest

from src.event_log import (
    append_event,
    read_from,
    replay,
    replay_roster,
    seed_roster_log,
)
from src.ingestion import get_refill_events
from src.transform import process_events


class TestLogIO(unittest.TestCase):

    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".jsonl")
        os.close(handle)
        os.remove(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_append_then_read_round_trips(self):
        append_event({"event_id": "A", "quantity": 1}, self.path)
        append_event({"event_id": "B", "quantity": 2}, self.path)
        events = read_from(0, self.path)
        self.assertEqual([e["event_id"] for e in events], ["A", "B"])

    def test_read_from_offset_skips_earlier_events(self):
        for i in range(5):
            append_event({"event_id": f"E{i}"}, self.path)
        self.assertEqual([e["event_id"] for e in read_from(3, self.path)],
                         ["E3", "E4"])

    def test_read_from_missing_log_is_empty(self):
        self.assertEqual(read_from(0, self.path), [])


class TestSeedAndReplay(unittest.TestCase):

    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".jsonl")
        os.close(handle)
        os.remove(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_seeding_is_idempotent(self):
        seed_roster_log(self.path)
        first = read_from(0, self.path)
        seed_roster_log(self.path)
        second = read_from(0, self.path)
        self.assertEqual(len(first), len(get_refill_events()))
        self.assertEqual(first, second)

    def test_replay_is_idempotent(self):
        seed_roster_log(self.path)
        one = json.dumps(replay(self.path).payload(), sort_keys=True)
        two = json.dumps(replay(self.path).payload(), sort_keys=True)
        self.assertEqual(one, two)

    def test_replay_payload_is_byte_identical_to_the_old_pipeline(self):
        old = process_events(get_refill_events())
        new = replay_roster(path=self.path).payload()
        self.assertEqual(json.dumps(old), json.dumps(new))

    def test_limit_folds_only_the_first_events(self):
        seed_roster_log(self.path)
        state = replay(self.path, limit=5)
        self.assertEqual(state.offset, 5)
        self.assertEqual(len(state.payload()["events"]), 5)


if __name__ == "__main__":
    unittest.main()
