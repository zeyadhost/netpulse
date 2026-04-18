import unittest

from scapy.all import ARP, DNS, ICMP, IP, TCP, UDP

from capture import PacketCapture


class PacketCaptureTests(unittest.TestCase):
    def setUp(self):
        self.capture = PacketCapture()

    def test_classifies_tcp_https_packet(self):
        packet = IP(dst="1.1.1.1") / TCP(sport=51515, dport=443)

        summary = self.capture.build_packet_summary(packet)

        self.assertEqual(summary["protocol"], "TCP")
        self.assertEqual(summary["service"], "HTTPS")
        self.assertEqual(summary["endpoint"], "1.1.1.1")

    def test_classifies_dns_packet_by_layer(self):
        packet = IP(dst="8.8.8.8") / UDP(sport=53000, dport=53) / DNS()

        summary = self.capture.build_packet_summary(packet)

        self.assertEqual(summary["protocol"], "UDP")
        self.assertEqual(summary["service"], "DNS")
        self.assertEqual(summary["endpoint"], "8.8.8.8")

    def test_classifies_arp_packet(self):
        packet = ARP(pdst="192.168.1.1")

        summary = self.capture.build_packet_summary(packet)

        self.assertEqual(summary["protocol"], "ARP")
        self.assertEqual(summary["service"], "OTHER")
        self.assertEqual(summary["endpoint"], "192.168.1.1")

    def test_classifies_icmp_packet(self):
        packet = IP(dst="10.0.0.5") / ICMP()

        summary = self.capture.build_packet_summary(packet)

        self.assertEqual(summary["protocol"], "ICMP")
        self.assertEqual(summary["service"], "OTHER")
        self.assertEqual(summary["endpoint"], "10.0.0.5")


if __name__ == "__main__":
    unittest.main()
