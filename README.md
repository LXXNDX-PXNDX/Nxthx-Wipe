# Nxthx-Wipe
Takes a router IP. Scans the local subnet. Launches SYN flood on every found device. Spoofs ARP to break traffic. Tries to factory reset the router via default creds. If monitor mode available, sends deauth packets to kick all clients.  No GUI fluff. Just functions that call hping3, arpspoof, and requests. Works on macOS with brew deps.
