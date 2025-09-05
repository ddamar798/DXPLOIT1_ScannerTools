#!/usr/bin/env python3
# DXPLOIT – Stealth & User-Friendly Recon/Scanning/Enumeration Tool
# Dibangun di atas ReconBuddy V2, dengan flow interaktif agar lebih user-friendly.

import socket
import random
import time
import argparse
import sys
import json
import datetime
from typing import List, Dict

try:
    import socks  # PySocks
except ImportError:
    socks = None

try:
    from scapy.all import IP, TCP, sr1, conf
except ImportError:
    IP = TCP = sr1 = conf = None

# -----------------------------------------------------------------------------
# Service mapping sederhana
SERVICE_BY_PORT = {
    22: "ssh",
    80: "http",
    443: "https",
    5432: "postgresql",
    3306: "mysql",
    6379: "redis",
    27017: "mongodb",
}

EXPLOIT_RECOMMENDATIONS = {
    "ssh": ["hydra → Brute-force password SSH (berizin)", "ssh-audit → Enumerasi konfigurasi SSH"],
    "http": ["nikto → Cari misconfigurations web", "gobuster → Cari hidden directories"],
    "https": ["sslscan → Audit SSL/TLS version & ciphers"],
    "postgresql": ["hydra → Uji kredensial lemah PostgreSQL", "psql → Enumerasi schema jika ada kredensial"],
    "mysql": ["hydra → Brute-force MySQL", "mysql-client → Tes akses manual"],
    "redis": ["redis-cli → Coba akses & info server"],
}

# -----------------------------------------------------------------------------
# Utility Functions

def check_ip_valid(ip: str) -> bool:
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def tcp_connect(ip: str, port: int, timeout=1.0) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False


def grab_banner(ip: str, port: int, timeout=1.5) -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        # Kirim sedikit data untuk memancing banner
        if port in [80, 443]:
            s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
        else:
            s.sendall(b"\r\n")
        data = s.recv(1024)
        s.close()
        return data.decode(errors="ignore").strip()
    except:
        return ""


def detect_service(port: int, banner: str) -> str:
    banner_low = banner.lower()
    if "postgres" in banner_low:
        return "postgresql"
    if "mysql" in banner_low:
        return "mysql"
    if "ssh" in banner_low:
        return "ssh"
    if "redis" in banner_low:
        return "redis"
    return SERVICE_BY_PORT.get(port, "unknown")

# -----------------------------------------------------------------------------
# Scan Core

def scan_ports(ip: str, ports: List[int], mode: str = "normal", delay: float = 0.0, jitter: float = 0.0) -> List[Dict]:
    results = []
    port_list = ports.copy()
    random.shuffle(port_list)

    for port in port_list:
        open_flag = tcp_connect(ip, port, timeout=1.0)
        if open_flag:
            banner = grab_banner(ip, port)
            service = detect_service(port, banner)
            results.append({
                "port": port,
                "protocol": "tcp",
                "service": service,
                "product": banner[:50] if banner else "",
                "version": "",
                "extrainfo": ""
            })

        # Delay + jitter
        if delay > 0:
            sleep_time = delay / 1000.0
            if jitter > 0:
                sleep_time += random.uniform(0, jitter/1000.0)
            time.sleep(sleep_time)

    return results

# -----------------------------------------------------------------------------
# Output Formatting

def format_table(target: str, ip: str, tool: str, results: List[Dict]) -> str:
    scanned_at = datetime.datetime.utcnow().isoformat() + "Z"
    header = f"\nHasil Scan – Target: {target} ({ip})\n"
    header += f"Tool: {tool} | Waktu: {scanned_at}\n\n"

    cols = ["Port", "Proto", "Service", "Product", "Version", "Extra"]
    rows = []
    for item in sorted(results, key=lambda x: x.get("port", 0)):
        rows.append([
            str(item.get("port", "")),
            item.get("protocol", ""),
            item.get("service", ""),
            item.get("product", ""),
            item.get("version", ""),
            item.get("extrainfo", "")
        ])

    widths = [len(c) for c in cols]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], len(c))

    sep = " | "
    header_line = sep.join(cols[i].ljust(widths[i]) for i in range(len(cols)))
    divider = "-" * (sum(widths) + len(sep) * (len(cols) - 1))

    lines = [header, header_line, divider]
    if rows:
        for r in rows:
            lines.append(sep.join(r[i].ljust(widths[i]) for i in range(len(cols))))
    else:
        lines.append("(Tidak ada port terbuka terdeteksi)")

    return "\n".join(lines)


def print_recommendations(results: List[Dict]):
    services = {r["service"] for r in results if r["service"] != "unknown"}
    if not services:
        print("\nTidak ada rekomendasi khusus (service tidak terpetakan atau tidak ada port terbuka).")
        return
    print("\nRekomendasi Lanjutan (berdasarkan service terdeteksi):")
    for svc in services:
        if svc in EXPLOIT_RECOMMENDATIONS:
            for rec in EXPLOIT_RECOMMENDATIONS[svc]:
                print(f"- [{svc}] {rec}")

# -----------------------------------------------------------------------------
# Main Interactive Flow

def main():
    print("\n=== DXPLOIT – Stealth Recon & Exploit Helper ===")
    target_ip = input("Masukkan IP target yang ingin discan: ").strip()

    if not check_ip_valid(target_ip):
        print("[!] IP tidak valid.")
        sys.exit(1)

    print("\nPilih metode scanning:")
    print("1. Normal Scan – cepat, mungkin terdeteksi IDS")
    print("2. Silent Scan – lambat, lebih aman, gunakan delay + jitter")
    choice = input("Masukkan pilihan (1/2): ").strip()

    if choice == "2":
        mode = "silent"
        delay = 150  # ms
        jitter = 100 # ms
    else:
        mode = "normal"
        delay = 0
        jitter = 0

    # Daftar port default (bisa dikembangkan nanti)
    default_ports = [22, 80, 443, 5432, 3306, 6379]

    print(f"\n[+] Melakukan {mode} scan pada {target_ip}...")
    results = scan_ports(target_ip, default_ports, mode=mode, delay=delay, jitter=jitter)

    table_text = format_table(target_ip, target_ip, "dxploit", results)
    print(table_text)
    print_recommendations(results)


if __name__ == "__main__":
    main()
