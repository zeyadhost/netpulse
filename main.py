import ctypes
import os
import sys
import time

from rich.console import Console
from rich.live import Live
from scapy.all import get_working_ifaces

from capture import PacketCapture
from visualizer import Visualizer


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def request_admin_privileges():
    if not is_admin():
        print("NetPulse requires administrator privileges to capture packets.")
        print("Requesting elevated permissions...\n")

        try:
            script_path = os.path.abspath(sys.argv[0])
            params = f'"{script_path}"'

            shell32 = ctypes.windll.shell32
            shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit(0)
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            print("Please run this program as Administrator.")
            sys.exit(1)


def main():
    console = Console()

    print("Available network interfaces:")
    ifaces = get_working_ifaces()
    for i, iface in enumerate(ifaces):
        print(f"{i}: {iface.name} - {iface.description}")

    choice = input(
        "\nEnter interface number to capture (or press Enter for all): "
    ).strip()

    selected_iface = None
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(ifaces):
            selected_iface = ifaces[idx].name
            print(f"\nCapturing on: {selected_iface}")
        else:
            print("Invalid choice, capturing on all interfaces")

    print("Press Ctrl+C to stop\n")

    capture = PacketCapture(iface=selected_iface)
    visualizer = Visualizer()

    capture.start()
    time.sleep(0.5)

    last_size = os.get_terminal_size()

    try:
        with Live(
            visualizer.generate_display(), refresh_per_second=10, console=console
        ) as live:
            while True:
                current_size = os.get_terminal_size()
                if current_size != last_size:
                    console.clear()
                    last_size = current_size

                packets = capture.get_packets()
                for packet in packets:
                    visualizer.add_packet(packet)

                live.update(visualizer.generate_display())
                time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\nStopping NetPulse... (Captured {capture.packet_count} packets)")
        capture.stop()


if __name__ == "__main__":
    request_admin_privileges()
    main()
