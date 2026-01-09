from capture import PacketCapture
from visualizer import Visualizer
from rich.live import Live
from scapy.all import conf
import time

def main():
    capture = PacketCapture()
    visualizer = Visualizer()
    
    print("Starting NetPulse...")
    print(f"Capturing on interface: {conf.iface}")
    print("Press Ctrl+C to stop\n")
    
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
