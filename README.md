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

Press Ctrl+C to stop.

## TODO

- Protocol identification (HTTP/Green, UDP/Blue, Encrypted/Red)
- Color-coded pulses based on traffic type
- Interface selection
