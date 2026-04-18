import os
import time
from collections import Counter, deque

from rich.console import Group
from rich.panel import Panel
from rich.table import Table


class Visualizer:
    GRAPH_WINDOW_SECONDS = 30
    RATE_WINDOW_SECONDS = 1
    TOP_TALKERS_LIMIT = 5

    def __init__(self):
        self.recent_packets = deque()
        self.total_bytes = 0
        self.protocol_counts = Counter()
        self.protocol_bytes = Counter()
        self.host_counts = Counter()
        self.host_bytes = Counter()
        self.service_counts = Counter()
        self.start_time = time.time()
        self.peak_pps = 0
        self.peak_bps = 0
        self.peak_size = 0
        self.paused = False

    def get_terminal_size(self):
        size = os.get_terminal_size()
        return size.columns, size.lines

    def format_bytes(self, bytes_val):
        if bytes_val >= 1048576:
            return f"{bytes_val / 1048576:.2f} MB"
        if bytes_val >= 1024:
            return f"{bytes_val / 1024:.2f} KB"
        return f"{bytes_val} B"

    def _prune_old_packets(self, now):
        cutoff = now - self.GRAPH_WINDOW_SECONDS
        while self.recent_packets and self.recent_packets[0]["time"] < cutoff:
            self.recent_packets.popleft()

    def _build_traffic_bins(self, width, now):
        usable_width = max(width - 4, 1)
        bin_width = self.GRAPH_WINDOW_SECONDS / usable_width
        window_start = now - self.GRAPH_WINDOW_SECONDS
        bins = [0] * usable_width

        for packet in self.recent_packets:
            if packet["time"] < window_start:
                continue

            bin_index = int((packet["time"] - window_start) / bin_width)
            if bin_index >= usable_width:
                bin_index = usable_width - 1
            bins[bin_index] += packet["size"]

        return bins

    def _render_graph(self, bins, display_height):
        max_bin_value = max(max(bins, default=0), 1)
        lines = []

        for row in range(display_height, 0, -1):
            threshold = (row / display_height) * max_bin_value
            line = "".join("#" if value >= threshold else " " for value in bins)
            lines.append(line)

        return "\n".join(lines), max_bin_value

    def _current_rate_snapshot(self, now):
        cutoff = now - self.RATE_WINDOW_SECONDS
        recent_1s = [packet for packet in self.recent_packets if packet["time"] >= cutoff]
        current_pps = len(recent_1s)
        current_bps = sum(packet["size"] for packet in recent_1s)
        return current_pps, current_bps

    def _format_count_bytes(self, protocol):
        return (
            f"{self.protocol_counts[protocol]} "
            f"({self.format_bytes(self.protocol_bytes[protocol])})"
        )

    def _top_services_summary(self, limit=3):
        if not self.service_counts:
            return "None"

        return " | ".join(
            f"{service} {count}"
            for service, count in self.service_counts.most_common(limit)
        )

    def add_packet(self, packet):
        packet_time = packet.get("time", time.time())
        packet_entry = {
            "time": packet_time,
            "size": packet["size"],
            "protocol": packet["protocol"],
        }
        self.recent_packets.append(packet_entry)
        self._prune_old_packets(packet_time)

        self.total_bytes += packet["size"]
        self.peak_size = max(self.peak_size, packet["size"])

        protocol = packet["protocol"]
        self.protocol_counts[protocol] += 1
        self.protocol_bytes[protocol] += packet["size"]

        host = packet.get("endpoint")
        if host:
            self.host_counts[host] += 1
            self.host_bytes[host] += packet["size"]

        service = packet.get("service")
        if service:
            self.service_counts[service] += 1

    def set_paused(self, paused):
        self.paused = paused

    def reset_statistics(self):
        self.recent_packets.clear()
        self.total_bytes = 0
        self.protocol_counts.clear()
        self.protocol_bytes.clear()
        self.host_counts.clear()
        self.host_bytes.clear()
        self.service_counts.clear()
        self.start_time = time.time()
        self.peak_pps = 0
        self.peak_bps = 0
        self.peak_size = 0

    def clear_live_statistics(self):
        self.recent_packets.clear()

    def _build_stats_table(self, now):
        elapsed = max(now - self.start_time, 0)
        total_packets = sum(self.protocol_counts.values())

        current_pps, current_bps = self._current_rate_snapshot(now)
        self.peak_pps = max(self.peak_pps, current_pps)
        self.peak_bps = max(self.peak_bps, current_bps)

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        stats_table = Table.grid(expand=True, padding=(0, 2))
        stats_table.add_column(justify="left")
        stats_table.add_column(justify="left")
        stats_table.add_column(justify="left")
        stats_table.add_column(justify="left")

        stats_table.add_row(
            f"[bold]Packets:[/] {total_packets}",
            f"[bold]Total:[/] {self.format_bytes(self.total_bytes)}",
            f"[bold]Current:[/] {current_pps} pkt/s | {self.format_bytes(current_bps)}/s",
            f"[bold]Uptime:[/] {uptime}",
        )
        stats_table.add_row(
            f"[cyan]TCP:[/] {self._format_count_bytes('TCP')}",
            f"[blue]UDP:[/] {self._format_count_bytes('UDP')}",
            f"[green]ICMP:[/] {self._format_count_bytes('ICMP')}",
            f"[magenta]ARP:[/] {self._format_count_bytes('ARP')}",
        )
        stats_table.add_row(
            f"[yellow]Other:[/] {self._format_count_bytes('OTHER')}",
            f"[bold]Services:[/] {self._top_services_summary()}",
            f"[bold]Largest:[/] {self.peak_size} B",
            f"[bold]Peak:[/] {self.peak_pps} pkt/s | {self.format_bytes(self.peak_bps)}/s",
            "",
        )

        return stats_table

    def generate_display(self):
        width, height = self.get_terminal_size()
        now = time.time()
        self._prune_old_packets(now)

        stats_height = 5
        display_height = max(height - stats_height - 4, 1)

        bins = self._build_traffic_bins(width, now)
        visual, max_bin_value = self._render_graph(bins, display_height)

        state = "[yellow]Paused[/]" if self.paused else "[green]Running[/]"
        graph = Panel(
            visual,
            title="NetPulse",
            subtitle=(
                f"{state} | Window: {self.GRAPH_WINDOW_SECONDS}s | "
                f"Peak bin: {self.format_bytes(max_bin_value)} | "
                "P pause/resume | R reset | C clear | Q quit"
            ),
        )

        stats_panel = Panel(self._build_stats_table(now), title="Statistics")

        return Group(graph, stats_panel)
