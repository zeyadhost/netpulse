from capture import PacketCapture
from visualizer import Visualizer
from rich.live import Live
from scapy.all import get_working_ifaces
import time

def main():
    print("Available network interfaces:")
    ifaces = get_working_ifaces()
    for i, iface in enumerate(ifaces):
        print(f"{i}: {iface.name} - {iface.description}")
    
    choice = input("\nEnter interface number to capture (or press Enter for all): ").strip()
    
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
    
    try:
        with Live(visualizer.generate_display(), refresh_per_second=10) as live:
            while True:
                packets = capture.get_packets()
                for packet in packets:
                    visualizer.add_packet(packet)
                
                live.update(visualizer.generate_display())
                time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\nStopping NetPulse... (Captured {capture.packet_count} packets)")
        capture.stop()
        
if __name__ == "__main__":
    main()
