import time
from queue import Empty, Queue

from scapy.all import ARP, DNS, ICMP, IP, IPv6, TCP, UDP, AsyncSniffer


class PacketCapture:
    SERVICE_PORTS = {
        20: "FTP-DATA",
        21: "FTP",
        22: "SSH",
        25: "SMTP",
        53: "DNS",
        67: "DHCP",
        68: "DHCP",
        80: "HTTP",
        110: "POP3",
        123: "NTP",
        143: "IMAP",
        443: "HTTPS",
        3389: "RDP",
    }

    def __init__(self, iface=None, capture_filter=None):
        self.packet_queue = Queue()
        self.sniffer = None
        self.packet_count = 0
        self.iface = iface
        self.capture_filter = capture_filter
        self.paused = False

    def _classify_protocol(self, packet):
        if ARP in packet:
            return "ARP"
        if ICMP in packet:
            return "ICMP"
        if TCP in packet:
            return "TCP"
        if UDP in packet:
            return "UDP"
        if IP in packet or IPv6 in packet:
            return "IP"
        return "OTHER"

    def _classify_service(self, packet):
        if DNS in packet:
            return "DNS"

        if TCP in packet or UDP in packet:
            ports = []
            if hasattr(packet, "sport"):
                ports.append(packet.sport)
            if hasattr(packet, "dport"):
                ports.append(packet.dport)

            for port in ports:
                service = self.SERVICE_PORTS.get(port)
                if service:
                    return service

        return "OTHER"

    def _extract_endpoint(self, packet):
        if IP in packet:
            return packet[IP].dst
        if IPv6 in packet:
            return packet[IPv6].dst
        if ARP in packet:
            return packet[ARP].pdst
        return None

    def build_packet_summary(self, packet):
        return {
            "time": time.time(),
            "size": len(packet),
            "protocol": self._classify_protocol(packet),
            "service": self._classify_service(packet),
            "endpoint": self._extract_endpoint(packet),
        }

    def packet_handler(self, packet):
        if self.paused:
            return

        self.packet_count += 1
        self.packet_queue.put(self.build_packet_summary(packet))

    def start(self):
        self.sniffer = AsyncSniffer(
            prn=self.packet_handler,
            store=False,
            iface=self.iface,
            filter=self.capture_filter,
        )
        self.sniffer.start()

    def stop(self):
        if self.sniffer:
            self.sniffer.stop()

    def pause(self):
        self.paused = True
        self.clear_queue()

    def resume(self):
        self.paused = False

    def reset_count(self):
        self.packet_count = 0

    def clear_queue(self):
        while True:
            try:
                self.packet_queue.get_nowait()
            except Empty:
                break

    def get_packets(self):
        packets = []
        while not self.packet_queue.empty():
            packets.append(self.packet_queue.get())
        return packets
