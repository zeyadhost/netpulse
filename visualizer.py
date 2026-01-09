from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from collections import deque
import time
import os

class Visualizer:
    def __init__(self):
        self.console = Console()
        self.pulse_data = deque(maxlen=100)
        self.max_pulse_height = 20
        
    def get_terminal_size(self):
        size = os.get_terminal_size()
        return size.columns, size.lines
        
    def add_packet(self, packet):
        self.pulse_data.append({
            'size': packet['size'],
            'protocol': packet['protocol'],
            'time': time.time()
        })
        
    def generate_display(self):
        width, height = self.get_terminal_size()
        
        display_height = min(height - 5, self.max_pulse_height)
        
        if not self.pulse_data:
            return Panel("Listening for packets... (Open a webpage to generate traffic)", title="NetPulse", subtitle="Packets: 0")
            
        recent_packets = list(self.pulse_data)[-width//2:]
        
        bars = []
        for packet in recent_packets:
            bar_height = max(1, min(int((packet['size'] / 1500) * display_height), display_height))
            bar = "█" * bar_height
            bars.append(bar)
            
        visual = "\n".join([
            " ".join([bar[i] if i < len(bar) else " " for bar in bars])
            for i in range(display_height)
        ][::-1])
        
        stats = f"Packets: {len(self.pulse_data)} | Total Size: {sum(p['size'] for p in recent_packets)} bytes"
        
        return Panel(visual, title="NetPulse", subtitle=stats)
