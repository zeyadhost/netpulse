from scapy.all import sniff, IP, TCP, UDP, ARP, conf, get_if_list
from queue import Queue
import threading

class PacketCapture:
    def __init__(self):
        self.packet_queue = Queue()
        self.running = False
        self.capture_thread = None
        self.packet_count = 0
        
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
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
    def _capture_loop(self):
        try:
            sniff(prn=self.packet_handler, store=False, stop_filter=lambda x: not self.running, count=0)
        except Exception as e:
            print(f"\nCapture error: {e}")
            import traceback
            traceback.print_exc()
        
    def stop(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
            
    def get_packets(self):
        packets = []
        while not self.packet_queue.empty():
            packets.append(self.packet_queue.get())
        return packets
