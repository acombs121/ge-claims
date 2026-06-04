import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hr_data import get_sprint_backlog, get_pos_checkout

class TestShowcaseComponents(unittest.TestCase):

    def test_get_sprint_backlog(self):
        payload = get_sprint_backlog("BOARD-TEST")
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload.get("board_id"), "BOARD-TEST")
        self.assertIn("steps", payload)
        
        steps = payload["steps"]
        self.assertIsInstance(steps, list)
        self.assertGreaterEqual(len(steps), 3)
        for s in steps:
            self.assertIn("title", s)
            self.assertIn("category", s)
            self.assertIn("value", s)
            self.assertIn("description", s)

    def test_get_pos_checkout(self):
        payload = get_pos_checkout("REC-TEST")
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload.get("receipt_id"), "REC-TEST")
        self.assertIn("returned_item", payload)
        self.assertIn("exchange_item", payload)
        self.assertIn("reason_code", payload)
        
        ret_item = payload["returned_item"]
        self.assertIn("name", ret_item)
        self.assertIn("price", ret_item)
        self.assertIsInstance(ret_item["price"], (int, float))
        
        exch_item = payload["exchange_item"]
        self.assertIn("name", exch_item)
        self.assertIn("price", exch_item)
        self.assertIsInstance(exch_item["price"], (int, float))
        self.assertIn("image_url", exch_item)


if __name__ == '__main__':
    unittest.main()
