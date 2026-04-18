# netpulse

real-time network packet visualizer

## Requirements

- Python 3.8+
- Npcap (Windows packet capture driver)
- Administrator privileges

## Installation

### 1. Install Npcap

Download and install Npcap from https://npcap.com/

Make sure to enable "WinPcap API-compatible mode" during installation.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

Run as Administrator:

```bash
python main.py
```

You can optionally provide a BPF capture filter when prompted, for example:

```bash
tcp port 443
udp port 53
host 8.8.8.8
```

Controls while running:

- P: pause/resume packet processing
- R: reset statistics counters and graph history
- C: clear live graph history only
- Q: quit cleanly
- Ctrl+C: force stop

## TODO

- [ ] Protocol identification (HTTP/Green, UDP/Blue, Encrypted/Red)
- [ ] Color-coded pulses based on traffic type
- [x] Interface selection
