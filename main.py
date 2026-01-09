from capture import PacketCapture
from visualizer import Visualizer
from rich.live import Live
from scapy.all import conf, get_if_list, get_working_ifaces
import time

def main():
    print("Available network interfaces:")
    ifaces = get_working_ifaces()
    for i, iface in enumerate(ifaces):
        print(f"{i}: {iface.name} - {iface.description}")
    
    print("\nStarting NetPulse on ALL interfaces...")
    print("Press Ctrl+C to stop\n")
    
    capture = PacketCapture()
    visualizer = Visualizer()
    
    capture.start()
    
    try:
        with Live(visualizer.generate_display(), refresh_per_second=10) as live:
            while True:
                packets = capture.get_packets()
                for packet in packets:
                    visualizer.add_packet(packet)
                
                live.update(visualizer.generate_display())
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping NetPulse...")
        capture.stop()
        
if __name__ == "__main__":
    main()
