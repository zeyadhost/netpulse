from scapy.all import AsyncSniffer, IP, TCP, UDP, ARP, Ether
from queue import Queue

class PacketCapture:
    def __init__(self, iface=None):
        self.packet_queue = Queue()
        self.sniffer = None
        self.packet_count = 0
        self.iface = iface
        
    def packet_handler(self, packet):
        self.packet_count += 1
        packet_size = len(packet)
        protocol = "OTHER"
        
        if IP in packet:
            if TCP in packet:
                protocol = "TCP"
            elif UDP in packet:
                protocol = "UDP"
        elif ARP in packet:
            protocol = "ARP"
            
        self.packet_queue.put({
            'size': packet_size,
            'protocol': protocol
        })
    
    def start(self):
        self.sniffer = AsyncSniffer(prn=self.packet_handler, store=False, iface=self.iface)
        self.sniffer.start()
        
    def stop(self):
        if self.sniffer:
            self.sniffer.stop()
            
    def get_packets(self):
        packets = []
        while not self.packet_queue.empty():
            packets.append(self.packet_queue.get())
        return packets
        
    def stop(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
            
    def get_packets(self):
        packets = []
        while not self.packet_queue.empty():
            packets.append(self.packet_queue.get())
        return packets
