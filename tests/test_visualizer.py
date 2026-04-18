import unittest

from visualizer import Visualizer


class VisualizerTests(unittest.TestCase):
    def test_current_rate_uses_one_second_window(self):
        visualizer = Visualizer()
        visualizer.add_packet(
            {
                "time": 100.0,
                "size": 200,
                "protocol": "TCP",
                "service": "HTTPS",
                "endpoint": "1.1.1.1",
            }
        )
        visualizer.add_packet(
            {
                "time": 100.4,
                "size": 300,
                "protocol": "UDP",
                "service": "DNS",
                "endpoint": "8.8.8.8",
            }
        )
        visualizer.add_packet(
            {
                "time": 98.5,
                "size": 500,
                "protocol": "ARP",
                "service": "OTHER",
                "endpoint": "192.168.1.1",
            }
        )

        current_pps, current_bps = visualizer._current_rate_snapshot(100.5)

        self.assertEqual(current_pps, 2)
        self.assertEqual(current_bps, 500)

    def test_top_talkers_are_sorted_by_bytes(self):
        visualizer = Visualizer()
        visualizer.add_packet(
            {
                "time": 100.0,
                "size": 100,
                "protocol": "TCP",
                "service": "HTTP",
                "endpoint": "10.0.0.1",
            }
        )
        visualizer.add_packet(
            {
                "time": 100.2,
                "size": 900,
                "protocol": "TCP",
                "service": "HTTPS",
                "endpoint": "10.0.0.2",
            }
        )

        summary = visualizer._top_talkers_summary(limit=2)

        self.assertTrue(summary.startswith("10.0.0.2"))
        self.assertIn("10.0.0.1", summary)


if __name__ == "__main__":
    unittest.main()
