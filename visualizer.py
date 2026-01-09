from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from collections import deque
import time
import os

class Visualizer:
    def __init__(self):
        self.console = Console()
        self.pulse_data = deque(maxlen=500)
        self.total_bytes = 0
        self.tcp_count = 0
        self.udp_count = 0
        self.other_count = 0
        self.start_time = time.time()
        
    def get_terminal_size(self):
        size = os.get_terminal_size()
        return size.columns, size.lines
        
    def add_packet(self, packet):
        self.pulse_data.append({
            'size': packet['size'],
            'protocol': packet['protocol'],
            'time': time.time()
        })
        self.total_bytes += packet['size']
        if packet['protocol'] == 'TCP':
            self.tcp_count += 1
        elif packet['protocol'] == 'UDP':
            self.udp_count += 1
        else:
            self.other_count += 1
        
    def generate_display(self):
        width, height = self.get_terminal_size()
        
        usable_width = width - 4
        display_height = height - 10
        
        if not self.pulse_data:
            return Panel("Listening for packets...", title="NetPulse", subtitle="Packets: 0")
        
        recent_packets = list(self.pulse_data)[-usable_width:]
        
        while len(recent_packets) < usable_width:
            recent_packets.insert(0, {'size': 0, 'protocol': 'OTHER', 'time': 0})
        
        max_size = max(p['size'] for p in recent_packets) if recent_packets else 1500
        max_size = max(max_size, 100)
        
        lines = []
        for row in range(display_height, 0, -1):
            threshold = (row / display_height) * max_size
            line = ""
            for packet in recent_packets:
                if packet['size'] >= threshold:
                    line += "█"
                else:
                    line += " "
            lines.append(line)
        
        visual = "\n".join(lines)
        
        elapsed = time.time() - self.start_time
        total_packets = self.tcp_count + self.udp_count + self.other_count
        pps = total_packets / elapsed if elapsed > 0 else 0
        
        if self.total_bytes >= 1048576:
            size_str = f"{self.total_bytes / 1048576:.2f} MB"
        elif self.total_bytes >= 1024:
            size_str = f"{self.total_bytes / 1024:.2f} KB"
        else:
            size_str = f"{self.total_bytes} B"
        
        stats = f"Packets: {total_packets} | {size_str} | {pps:.1f} pkt/s | TCP: {self.tcp_count} | UDP: {self.udp_count} | Other: {self.other_count}"
        
        return Panel(visual, title="NetPulse", subtitle=stats)
