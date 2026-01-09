from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
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
        self.tcp_bytes = 0
        self.udp_bytes = 0
        self.other_bytes = 0
        self.start_time = time.time()
        self.peak_pps = 0
        self.peak_size = 0
        
    def get_terminal_size(self):
        size = os.get_terminal_size()
        return size.columns, size.lines
    
    def format_bytes(self, bytes_val):
        if bytes_val >= 1048576:
            return f"{bytes_val / 1048576:.2f} MB"
        elif bytes_val >= 1024:
            return f"{bytes_val / 1024:.2f} KB"
        else:
            return f"{bytes_val} B"
        
    def add_packet(self, packet):
        self.pulse_data.append({
            'size': packet['size'],
            'protocol': packet['protocol'],
            'time': time.time()
        })
        self.total_bytes += packet['size']
        if packet['size'] > self.peak_size:
            self.peak_size = packet['size']
        if packet['protocol'] == 'TCP':
            self.tcp_count += 1
            self.tcp_bytes += packet['size']
        elif packet['protocol'] == 'UDP':
            self.udp_count += 1
            self.udp_bytes += packet['size']
        else:
            self.other_count += 1
            self.other_bytes += packet['size']
        
    def generate_display(self):
        width, height = self.get_terminal_size()
        
        usable_width = width - 4
        stats_height = 4
        display_height = height - stats_height - 4
        
        if not self.pulse_data:
            graph = Panel("Listening for packets...", title="NetPulse")
            stats = Panel("Waiting for data...", title="Statistics")
            return Group(graph, stats)
        
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
        if pps > self.peak_pps:
            self.peak_pps = pps
        
        recent_1s = [p for p in self.pulse_data if time.time() - p['time'] < 1]
        current_pps = len(recent_1s)
        current_bps = sum(p['size'] for p in recent_1s)
        
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        graph = Panel(visual, title="NetPulse", subtitle=f"Max: {max_size} bytes")
        
        stats_table = Table.grid(padding=(0, 3))
        stats_table.add_column(justify="left")
        stats_table.add_column(justify="left")
        stats_table.add_column(justify="left")
        stats_table.add_column(justify="left")
        
        stats_table.add_row(
            f"[bold]Packets:[/] {total_packets}",
            f"[bold]Total:[/] {self.format_bytes(self.total_bytes)}",
            f"[bold]Current:[/] {current_pps} pkt/s | {self.format_bytes(current_bps)}/s",
            f"[bold]Uptime:[/] {uptime}"
        )
        stats_table.add_row(
            f"[cyan]TCP:[/] {self.tcp_count} ({self.format_bytes(self.tcp_bytes)})",
            f"[blue]UDP:[/] {self.udp_count} ({self.format_bytes(self.udp_bytes)})",
            f"[yellow]Other:[/] {self.other_count} ({self.format_bytes(self.other_bytes)})",
            f"[bold]Peak:[/] {self.peak_pps:.1f} pkt/s | {self.peak_size} B"
        )
        
        stats_panel = Panel(stats_table, title="Statistics")
        
        return Group(graph, stats_panel)
