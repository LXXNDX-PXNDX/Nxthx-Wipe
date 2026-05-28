#!/bin/bash
echo "NetherWipe Installer für macOS"

# Homebrew Prüfung
if ! command -v brew &> /dev/null; then
    echo "Homebrew wird installiert..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Abhängigkeiten über brew
echo "Installiere hping3, arpspoof, aircrack-ng, python-tk..."
brew install hping3 arpspoof aircrack-ng python-tk

# Python Pakete
echo "Installiere Python Pakete..."
pip3 install -r requirements.txt

# Ausführbarkeit des GUI-Skripts
chmod +x NetherWipe.py

echo "Fertig. Starte mit: sudo python3 NetherWipe.py"