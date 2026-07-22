import unittest

from src.ingestion import generate_mock_event, fetch_live_batch
from src.transform import flag_high_quantity, transform_batch


class TestPrescriptionPipeline(unittest.TestCase):

    def test_generate_mock_event(self):
        """
        verify generated mock event contains required keys
        """
        event = generate_mock_event()
        self.assertIn("medication", event)
        self.assertIn("quantity", event)

    def test_fetch_live_batch(self):
        """
        verify batch length matches requested parameter
        """
        batch = fetch_live_batch(5)
        self.assertEqual(len(batch), 5)

    def test_flag_high_quantity(self):
        """
        verify quantity threshold correctly flags large refills
        """
        low_event = {"quantity": 30}
        high_event = {"quantity": 90}
        self.assertFalse(flag_high_quantity(low_event)["is_large_refill"])
        self.assertTrue(flag_high_quantity(high_event)["is_large_refill"])

    def test_transform_batch(self):
        """
        verify every event in a batch receives the large-refill flag
        """
        batch = fetch_live_batch(4)
        transformed = transform_batch(batch)
        self.assertEqual(len(transformed), 4)
        self.assertTrue(all("is_large_refill" in e for e in transformed))


if __name__ == "__main__":
    unittest.main()
