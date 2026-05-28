# NxthxWipe – Terminal WiFi Destruction Tool for macOS

**Author:** LXXNDX-PXNDX  
**Version:** 2.0 (CLI)  
**License:** Educational use only / own networks

---

## What is NxthxWipe?

NxthxWipe is a command-line tool that takes down all devices in your local WiFi network.  
It performs:

- **SYN flood** (DoS) on each found device  
- **ARP spoofing** to break traffic  
- **Router reset attempts** (via common default credentials)

**No GUI. Just terminal.** Enter the router IP, press Enter, and watch the network die.

---

## Full Setup (macOS)

### 1. Prerequisites
- macOS (Monterey or newer)
- Python 3.7+
- Admin rights (`sudo`)
- Homebrew (install if missing: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)

### 2. Install required system packages
```bash
brew install python-tk
3. Clone or download the repository
bash
git clone https://github.com/LXXNDX-PXNDX/Nxthx-Wipe.git
cd Nxthx-Wipe
4. Set up a virtual environment
bash
python3 -m venv venv
source venv/bin/activate
5. Install Python dependencies
bash
pip install scapy requests
6. Make the script executable
bash
chmod +x NxthxWipe.py
How to Use
Start the tool with root privileges (required for raw packet sending):

bash
sudo env PATH="$PATH" python3 NxthxWipe.py
Note: sudo env PATH="$PATH" ensures that sudo inherits the virtual environment’s Python.

Step by step
You see a banner and a prompt:
Router IP (e.g. 192.168.1.1):
– Enter your router’s IP and press Enter.

The tool scans the network for devices.

It launches SYN flood + ARP spoofing on every device.

It attempts to factory reset the router via admin panel URLs.

The attack runs until you press Enter again.

Example output
text
╔═══════════════════════════════════════╗
║       NxthWipe – Terminal Edition     ║
║         von LXXNDX-PXNDX              ║
╚═══════════════════════════════════════╝

Router IP (z.B. 192.168.1.1): 192.168.1.1

Angriff startet in 3 Sekunden... Drücke Ctrl+C zum Abbrechen.

[23:15:01] Starte Zerstörung auf Router 192.168.1.1
[23:15:01] Scanne 192.168.1.0/24
[23:15:04] Gefunden: 5 Geräte
[23:15:04] SYN Flood auf 192.168.1.10 für 60s
[23:15:04] ARP-Spoofing gestartet: 192.168.1.10 <-> 192.168.1.1
...
[23:15:10] Alle Angriffe gestartet. Drücke Enter, um zu stoppen.
Press Enter → attacks stop.

Important Notes
Use only on your own network – attacking others is illegal.

Root privileges are mandatory.

Devices recover shortly after you stop the attack.

Some routers may resist reset attempts if they use non‑default credentials.

For best results, run the tool from a machine connected via Ethernet (WiFi works too but may be less stable).

Troubleshooting
Problem	Solution
ModuleNotFoundError: No module named 'scapy'	Activate venv: source venv/bin/activate then pip install scapy
Operation not permitted	Always use sudo
No devices found	Check that you are on the same WiFi network as the router
_tkinter error	This is the CLI version – ignore or run brew install python-tk
Files in this repository
NxthxWipe.py – main script (CLI version)

requirements.txt – Python dependencies (scapy, requests)

install.sh – optional setup script

README.md – this file

Disclaimer
This tool is for educational purposes only. You may only test it on networks you own or have explicit permission to assess. The author assumes no liability for any misuse or damage.

