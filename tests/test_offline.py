"""Run with: py -m unittest discover -s tests -v (does not need a broker)."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import TOPIC_ROOT, light_topic, light_topic_filter  # noqa: E402
from measurement import create_measurement, decode_measurement, encode_measurement  # noqa: E402


class MQTTDemoOfflineTests(unittest.TestCase):
    def test_publish_topic(self):
        self.assertEqual(light_topic(1), f"{TOPIC_ROOT}/area/1/light")
        self.assertEqual(light_topic(2), f"{TOPIC_ROOT}/area/2/light")

    def test_subscribe_filter(self):
        self.assertEqual(light_topic_filter(), f"{TOPIC_ROOT}/area/+/light")

    def test_payload_roundtrip(self):
        data = create_measurement(2, 450)
        self.assertEqual(set(data), {"timestamp", "area", "lux"})
        self.assertEqual(data["area"], 2)
        self.assertEqual(data["lux"], 450)
        result = decode_measurement(encode_measurement(data).encode("utf-8"))
        self.assertEqual(result, data)

    def test_invalid_area(self):
        with self.assertRaises(ValueError):
            light_topic(0)
        with self.assertRaises(ValueError):
            create_measurement(-1, 100)

    def test_invalid_payload(self):
        bad = json.dumps({"timestamp": "2025-05-02 05:44:35", "area": "1", "lux": 500})
        with self.assertRaises(ValueError):
            decode_measurement(bad.encode("utf-8"))
        with self.assertRaises(ValueError):
            decode_measurement(b"not json")


if __name__ == "__main__":
    unittest.main()
