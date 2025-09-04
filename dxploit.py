#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReconBuddy v2 – Stealth Recon/Scanning/Enumeration (Tanpa Nmap)
================================================================

Tujuan:
- Melakukan scanning & enumeration ringan untuk pembelajaran/pentest yang berizin
- Tanpa ketergantungan ke Nmap/Wireshark; murni Python + opsional Scapy (SYN)
- "Silent" mode: rate-limit, delay + jitter, urutan acak, timeout ketat
- Dukungan SOCKS proxy (PySocks) agar bisa routing via proxy (mirip proxychains)
- Output rapi (tabel & JSON) + rekomendasi lanjutan untuk eksploitasi (high-level)

ETIKA/LEGAL:
- Gunakan HANYA pada aset milik sendiri atau dengan izin tertulis (Rules of Engagement).
- Penulis tidak bertanggung jawab atas penyalahgunaan.

Dependensi opsional:
- PySocks  (untuk SOCKS proxy) -> pip install PySocks
- scapy    (opsional untuk SYN scan) -> pip install scapy  (butuh root)

Contoh pakai:
  python3 reconbuddy_v2.py -t 127.0.0.1
  python3 reconbuddy_v2.py -t 10.10.10.5 --safe --delay 150 --jitter 75
  python3 reconbuddy_v2.py -t 192.168.1.10 -p 22,80,443,5432 --socks 127.0.0.1:9050
  sudo python3 reconbuddy_v2.py -t 192.168.1.10 --syn   # gunakan SYN scan (scapy)
  python3 reconbuddy_v2.py -t host --export hasil.json

Catatan:
- Mode SYN memerlukan hak root dan scapy. Jika tidak tersedia, fallback ke TCP connect scan.
- Tool ini tidak mengeksekusi eksploit; hanya memberi rekomendasi high-level berbasis deteksi layanan.
"""

import argparse
import json
import random
import socket
import ssl
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ====== Konfigurasi default ======
COMMON_PORTS = [
    21,22,23,25,53,80,110,111,123,135,139,143,161,389,443,445,465,587,993,995,
    1025,1080,1433,1521,2049,2375,2376,3000,3306,3389,3690,4000,4200,4444,5000,
    5432,5601,5672,5900,5985,5986,6379,6443,6667,7001,7002,8000,8008,8080,8081,
    8088,8181,8443,8888,9000,9200,9300,11211,27017
]

SERVICE_BY_PORT = {
    21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns', 80: 'http', 110: 'pop3',
    111: 'rpcbind', 123: 'ntp', 135: 'msrpc', 139: 'smb', 143: 'imap', 161: 'snmp',
    389: 'ldap', 443: 'https', 445: 'smb', 465: 'smtps', 587: 'smtp', 993: 'imaps',
    995: 'pop3s', 1433: 'mssql', 1521: 'oracle', 2049: 'nfs', 2375: 'docker', 2376: 'docker',
    3000: 'http', 3306: 'mysql', 3389: 'rdp', 3690: 'svn', 4000: 'http', 4200: 'http',
    4444: 'msf', 5000: 'http', 5432: 'postgresql', 5601: 'kibana', 5672: 'amqp',
    5900: 'vnc', 5985: 'winrm', 5986: 'winrm', 6379: 'redis', 6443: 'kube-apiserver',
    6667: 'irc', 7001: 'weblogic', 7002: 'weblogic', 8000: 'http', 8008: 'http', 8080: 'http',
    8081: 'http', 8088: 'http', 8181: 'http', 8443: 'https', 8888: 'http', 9000: 'http',
    9200: 'elasticsearch', 9300: 'elasticsearch', 11211: 'memcached', 27017: 'mongodb'
}

RECOMMENDATION_MAP = {
    'http': [
        ("gobuster", "Enumerasi direktori/virtual host untuk menemukan attack surface."),
        ("nikto", "Baseline scan misconfig/vuln umum pada server web."),
        ("nuclei", "Template-based CVE/misconfig scanning untuk endpoint web."),
        ("burp suite", "Testing manual parameter, auth, dan logic flaw.")
    ],
    'https': [
        ("gobuster", "Enumerasi direktori pada situs HTTPS."),
        ("sslscan", "Audit cipher/TLS misconfiguration."),
        ("nuclei", "Scan template CVE pada endpoint TLS/HTTPS."),
        ("burp suite", "Intercept & test manual over TLS.")
    ],
    'ssh': [
        ("hydra", "Uji kredensial lemah (berizin) dengan rate-limit."),
        ("ssh-audit", "Audit KEX/cipher/versi untuk hardening/weakness."),
    ],
    'ftp': [
        ("hydra", "Bruteforce kredensial (berizin)."),
        ("nmap ftp-anon NSE", "Cek anonymous login & enum banner (opsional).")
    ],
    'smb': [
        ("enum4linux-ng", "Enumerasi user/share/policy Windows/SMB."),
        ("smbclient", "Listing share; akses file dengan kredensial/anon."),
    ],
    'rdp': [
        ("rdp-sec-check", "Audit konfigurasi keamanan RDP."),
    ],
    'mysql': [
        ("hydra", "Uji kredensial lemah MySQL (berizin)."),
        ("sqlmap", "Jika ditemukan endpoint web ke backend MySQL."),
    ],
    'postgresql': [
        ("hydra", "Uji kredensial lemah PostgreSQL (berizin)."),
        ("psql", "Validasi akses & enumerasi skema jika memiliki kredensial."),
    ],
    'redis': [
        ("redis-cli", "Uji akses tanpa auth & enum keys; cek misconfig."),
    ],
    'mongodb': [
        ("mongo", "Coba koneksi tanpa auth; enum DB (lab only)."),
    ],
    'ldap': [
        ("ldapsearch", "Enumerasi schema/entry jika anon bind diizinkan."),
    ],
}

# ====== Utilitas ======

def now_iso() -> str:
    return datetime.utcnow().isoformat() + 'Z'

@dataclass
class SockConfig:
    host: Optional[str] = None
    port: Optional[int] = None

# ====== Core scanning ======

class StealthScanner:
    def __init__(self, target: str, ports: List[int], timeout: float = 1.5,
                 safe: bool = False, delay_ms: int = 0, jitter_ms: int = 0,
                 socks: Optional[SockConfig] = None, syn: bool = False):
        self.target = target
        self.ports = ports[:]
        self.timeout = timeout
        self.safe = safe
        self.delay_ms = delay_ms
        self.jitter_ms = jitter_ms
        self.socks = socks
        self.syn = syn
        random.shuffle(self.ports)

        # Setup SOCKS if requested
        self._use_socks = False
        self._socks_mod = None
        if self.socks and self.socks.host and self.socks.port:
            try:
                import socks  # PySocks
                self._socks_mod = socks
                self._use_socks = True
            except Exception:
                self._use_socks = False

    def _sleep_safe(self):
        base = max(self.delay_ms, 0) / 1000.0
        jit = max(self.jitter_ms, 0) / 1000.0
        if base > 0 or jit > 0:
            time.sleep(base + random.uniform(0, jit))

    def _tcp_connect_probe(self, ip: str, port: int) -> Tuple[bool, bytes]:
        buf = b""
        s = None
        try:
            if self._use_socks:
                s = self._socks_mod.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                s.set_proxy(self._socks_mod.SOCKS5, self.socks.host, int(self.socks.port))
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout if not self.safe else max(self.timeout, 2.5))
            s.connect((ip, port))
            # Banner grabs ringan per layanan umum
            try:
                s.settimeout(0.8)
                if port in (80, 8000, 8008, 8080, 8081, 8888, 5000, 3000, 4200):
                    s.sendall(b"HEAD / HTTP/1.0\r\nHost: %b\r\n\r\n" % self.target.encode('ascii', 'ignore'))
                elif port in (443, 8443):
                    # Coba TLS handshake minimal untuk dapatkan server hello/cert CN
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    s = context.wrap_socket(s, server_hostname=self.target)
                elif port == 21:  # FTP
                    pass  # biasanya banner langsung dikirim server
                elif port == 22:  # SSH
                    pass  # banner SSH segera tersedia
                elif port == 25:  # SMTP
                    s.sendall(b"EHLO reconbuddy\r\n")
                elif port == 110:  # POP3
                    s.sendall(b"QUIT\r\n")
                elif port == 143:  # IMAP
                    s.sendall(b"A1 CAPABILITY\r\n")
                elif port == 3306:  # MySQL: server kirim handshake greeting
                    pass
                elif port == 5432:  # PostgreSQL: kirim startup packet untuk dapat FATAL versi
                    # Minimal startup packet: length(4) + protocol(4) + paramz... (empty)
                    pkt = b"\x00\x00\x00\x08" + b"\x00\x03\x00\x00"
                    s.sendall(pkt)
                elif port == 6379:  # Redis
                    s.sendall(b"PING\r\n")
                elif port == 11211:  # Memcached
                    s.sendall(b"version\r\n")
                # read
                try:
                    buf = s.recv(4096)
                except Exception:
                    buf = b""
            except Exception:
                pass
            return True, buf
        except Exception:
            return False, b""
        finally:
            try:
                if s:
                    s.close()
            except Exception:
                pass

    def _syn_probe(self, ip: str, port: int) -> bool:
        # SYN scan opsional via scapy
        try:
            from scapy.all import IP, TCP, sr1, conf
            conf.verb = 0
            pkt = IP(dst=ip)/TCP(dport=port, flags='S', seq=random.randint(0,2**32-1))
            ans = sr1(pkt, timeout=self.timeout if not self.safe else max(self.timeout, 2.5))
            if ans is None:
                return False
            if ans.haslayer(TCP):
                fl = ans.getlayer(TCP).flags
                # SYN-ACK (0x12) berarti open
                return (fl & 0x12) == 0x12
            return False
        except Exception:
            return False

    def scan(self) -> Dict:
        # Resolve terlebih dahulu
        try:
            ip = socket.gethostbyname(self.target)
        except Exception:
            ip = self.target
        results = {
            "target": self.target,
            "resolved_ip": ip,
            "scanned_at": now_iso(),
            "tool": "reconbuddy-v2",
            "ports": []
        }

        for port in self.ports:
            is_open = False
            banner = b""
            if self.syn:
                is_open = self._syn_probe(ip, port)
                # pada mode SYN, kita tidak melakukan banner grab. Jika open, opsional TCP connect singkat.
                if is_open:
                    ok, banner = self._tcp_connect_probe(ip, port)
                    if not ok:
                        banner = b""
            else:
                is_open, banner = self._tcp_connect_probe(ip, port)

            if is_open:
                service_guess = SERVICE_BY_PORT.get(port, '')
                product = ''
                version = ''
                extra = ''
                decoded = banner.decode('utf-8', 'ignore') if banner else ''
                # heuristik ringan dari banner/content
                low = decoded.lower()
                if 'postgresql' in low or 'postgre' in low or 'unsupported frontend protocol' in low:
                    service_guess = 'postgresql'
                elif 'mysql' in low or 'mysqld' in low:
                    service_guess = 'mysql'
                elif 'redis' in low:
                    service_guess = 'redis'
                elif 'ssh-' in low:
                    service_guess = 'ssh'
                    # SSH banner pattern: SSH-2.0-OpenSSH_8.9p1 Ubuntu-3
                    product = decoded.strip().split('\n')[0]
                elif 'smtp' in low or 'ehlo' in low:
                    service_guess = 'smtp'
                elif 'http/' in low or 'server:' in low or port in (80,8000,8008,8080,8081,5000,3000,4200):
                    if port in (443, 8443):
                        service_guess = 'https'
                    else:
                        service_guess = 'http'
                    # coba ambil "Server: Apache/2.4.41" dsb
                    for line in decoded.splitlines():
                        if line.lower().startswith('server:'):
                            product = line.split(':',1)[1].strip()
                            break
                elif 'memcached' in low:
                    service_guess = 'memcached'
                # versi/extra sederhana
                if not product and decoded:
                    # ambil potongan awal saja
                    product = decoded[:60].replace('\r',' ').replace('\n',' ')

                results["ports"].append({
                    "port": port,
                    "protocol": "tcp",
                    "service": service_guess,
                    "product": product,
                    "version": version,
                    "extrainfo": extra
                })

            # jeda aman
            if self.safe:
                self._sleep_safe()

        # sort hasil by port
        results["ports"].sort(key=lambda x: x["port"])
        return results

# ====== Output & Rekomendasi ======

def format_table(results: Dict) -> str:
    target = results.get('target', '?')
    ip = results.get('resolved_ip', '?')
    scanned_at = results.get('scanned_at', '?')
    tool = results.get('tool', '?')

    header = f"\nHasil Scan – Target: {target} ({ip})\n"
    header += f"Tool: {tool} | Waktu: {scanned_at}\n"

    ports = results.get('ports', []) or []

    cols = ["Port", "Proto", "Service", "Product", "Version", "Extra"]

    rows: List[List[str]] = []
    for item in ports:
        rows.append([
            str(item.get('port', '')),
            str(item.get('protocol', '') or ''),
            str(item.get('service', '') or SERVICE_BY_PORT.get(item.get('port'), '')),
            str(item.get('product', '') or ''),
            str(item.get('version', '') or ''),
            str(item.get('extrainfo', '') or '')
        ])

    widths: List[int] = []
    for i, col in enumerate(cols):
        maxw = len(col)
        for r in rows:
            if len(r[i]) > maxw:
                maxw = len(r[i])
        widths.append(maxw)

    sep = " | "
    header_line = sep.join(cols[i].ljust(widths[i]) for i in range(len(cols)))
    divider = "-" * (sum(widths) + len(sep) * (len(cols) - 1))

    lines: List[str] = [header, header_line, divider]

    if rows:
        for r in rows:
            lines.append(sep.join(r[i].ljust(widths[i]) for i in range(len(cols))))
    else:
        lines.append("(Tidak ada port terbuka yang terdeteksi pada daftar port yang diuji)")

    return "\n".join(lines)

def build_recommendations(results: Dict) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []
    seen = set()
    for item in results.get('ports', []):
        service = (item.get('service') or SERVICE_BY_PORT.get(item.get('port')) or '').lower()
        if not service:
            continue
        base = service
        # normalisasi sederhana
        if base in ('http-proxy', 'kibana', 'elasticsearch', 'weblogic'):
            base = 'http'
        if base in ('https-alt',):
            base = 'https'
        if base in ('microsoft-ds',):
            base = 'smb'
        for tool, reason in RECOMMENDATION_MAP.get(base, []):
            key = (tool, base)
            if key in seen:
                continue
            seen.add(key)
            recs.append({
                'service': base,
                'tool': tool,
                'reason': reason
            })
    return recs

# ====== CLI ======

def parse_ports(spec: Optional[str]) -> List[int]:
    if not spec:
        return COMMON_PORTS[:]
    ports: List[int] = []
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a,b = part.split('-',1)
            a = int(a); b = int(b)
            if a<=b:
                ports.extend(range(a,b+1))
        else:
            ports.append(int(part))
    # unique + clamp to valid
    ports = sorted({p for p in ports if 1 <= p <= 65535})
    return ports


def main():
    ap = argparse.ArgumentParser(description='ReconBuddy v2 – Stealth Recon/Scanning/Enumeration (tanpa Nmap)')
    ap.add_argument('-t','--target', required=True, help='IP/Hostname target (contoh: 192.168.1.10)')
    ap.add_argument('-p','--ports', help='Daftar port, misal: 22,80,443 atau 1-1024')
    ap.add_argument('--timeout', type=float, default=1.5, help='Timeout per koneksi (detik). Default 1.5')
    ap.add_argument('--safe', action='store_true', help='Aktifkan mode aman: jeda + jitter antara koneksi')
    ap.add_argument('--delay', type=int, default=0, help='Delay dasar antar percobaan (ms)')
    ap.add_argument('--jitter', type=int, default=0, help='Jitter acak tambahan (ms)')
    ap.add_argument('--socks', help='SOCKS5 proxy host:port (contoh 127.0.0.1:9050)')
    ap.add_argument('--syn', action='store_true', help='Gunakan SYN scan (butuh root & scapy). Fallback ke TCP connect bila gagal')
    ap.add_argument('--export', help='Simpan hasil ke file JSON')

    args = ap.parse_args()

    ports = parse_ports(args.ports)
    socks_conf = None
    if args.socks:
        try:
            shost, sport = args.socks.split(':',1)
            socks_conf = SockConfig(shost, int(sport))
        except Exception:
            print('[!] Format --socks harus host:port, contoh 127.0.0.1:9050', file=sys.stderr)
            sys.exit(2)

    scanner = StealthScanner(
        target=args.target,
        ports=ports,
        timeout=args.timeout,
        safe=args.safe,
        delay_ms=args.delay,
        jitter_ms=args.jitter,
        socks=socks_conf,
        syn=args.syn,
    )

    results = scanner.scan()
    print(format_table(results))

    recs = build_recommendations(results)
    if recs:
        print('\nRekomendasi Lanjutan (berdasarkan service terdeteksi):')
        for r in recs:
            print(f"- [{r['service']}] {r['tool']} → {r['reason']}")
    else:
        print('\nTidak ada rekomendasi khusus (service tidak terpetakan atau tidak ada port terbuka).')

    if args.export:
        try:
            bundle = {
                'meta': {
                    'generated_by': 'ReconBuddy v2',
                    'timestamp': now_iso(),
                    'target': args.target,
                },
                'results': results,
                'recommendations': recs,
            }
            with open(args.export, 'w', encoding='utf-8') as f:
                json.dump(bundle, f, ensure_ascii=False, indent=2)
            print(f"\n[+] Hasil disimpan ke {args.export}")
        except Exception as e:
            print(f"[!] Gagal menyimpan JSON: {e}")

if __name__ == '__main__':
    main()
