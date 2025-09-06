# dxploit_step2.py
import sys
from core.utils import is_valid_ip, pretty_list
from core.scanner_engine import run_passive_then_active
from core.modes import Mode, MODES, choose_mode_interactive
from core.utils import save_json
import os
import argparse


def format_scan_result(res: dict):
    """
    Nicely print nmap parsed results or shodan summary.
    If many ports, print each as numbered list (vertical).
    """
    print("\n=== Scan Summary ===")
    target = res.get("target")
    print(f"Target: {target}")
    if res.get("shodan"):
        ips = res["shodan"].get("ip_str")
        org = res["shodan"].get("org")
        print(f"[Shodan] ip={ips} org={org}")
        # include services from shodan if present
        sh_ports = []
        for svc in res["shodan"].get("data", []) if isinstance(res["shodan"].get("data"), list) else []:
            port = svc.get("port")
            banner = svc.get("data", "")
            sh_ports.append(f"Port {port} | banner: {banner[:80]}")
        if sh_ports:
            print("\nShodan services:")
            pretty_list(sh_ports)

    nmap = res.get("nmap")
    if not nmap:
        print("\nNo Nmap result parsed.")
        return

    for host in nmap.get("hosts", []):
        addr = host.get("address")
        ports = host.get("ports", [])
        if not ports:
            print(f"\nHost {addr} - no open ports detected (by nmap result).")
            continue

        lines = []
        for p in ports:
            if p.get("state") != "open":
                continue
            svc = p.get("service") or p.get("product") or ""
            lines.append(f"Port {p['port']} / {p['protocol']} | service={p.get('service')} | product={p.get('product')} {p.get('version')}")
        if len(lines) > 8:
            # print vertical list
            print(f"\nHost {addr} - {len(lines)} open ports:")
            pretty_list(lines)
        else:
            print(f"\nHost {addr} - open ports:")
            pretty_list(lines)


def main():
    parser = argparse.ArgumentParser(description="DXPLOIT Step2 - Scanning Engine (RustScan + Nmap + Shodan)")
    parser.add_argument("-t", "--target", help="Target IP or hostname", required=False)
    parser.add_argument("--no-passive", action="store_true", help="Skip Shodan passive recon even if key available")
    args = parser.parse_args()

    if args.target:
        target = args.target.strip()
    else:
        target = input("Masukkan target IP/host: ").strip()

    if not is_valid_ip(target):
        print("[!] IP tidak valid. Gunakan format IPv4 (contoh: 10.10.10.5).")
        sys.exit(1)

    # choose mode (currently used for later chaining)
    mode = choose_mode_interactive()
    print(f"Mode dipilih: {mode.key}")

    prefer_passive = not args.no_passive
    result = run_passive_then_active(target, prefer_passive=prefer_passive, nmap_extra_args=None)

    format_scan_result(result)
    print("\n[+] Scan raw saved to:", result.get("saved_to"))


if __name__ == "__main__":
    main()
