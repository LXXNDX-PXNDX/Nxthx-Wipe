#!/bin/bash
echo "NetherWipe Installer für macOS"

# Homebrew Abhängigkeiten (ohne hping3)
brew install dsniff aircrack-ng python-tk

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# Python Pakete in venv installieren
pip install scapy requests

echo "Fertig. Starte mit:"
echo "source venv/bin/activate"
echo "sudo env PATH=\"\$PATH\" python3 NetherWipe.py"
