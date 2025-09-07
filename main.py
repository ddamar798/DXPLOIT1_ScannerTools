#!/usr/bin/env python3
"""
DXploit Main Entry Point
Step 6 – Advanced Reporting, CVE Auto-Mapping, Post-Exploitation Intel
"""

import sys
import json
from core.menu import main_menu
from modules.scanning import runner
from modules.exploitation import mapper
from modules.exploitation.executor import run_exploit
from modules.reporting import report
from modules.intel import cve_lookup
from modules.post_exploit import intel
from core.utils import validate_ip, now_iso


def main():
    print("=== DXploit – Offensive Security Toolkit ===")
    print("Step 6 – Advanced Reporting & Intel Gathering\n")

    # 1. Input Target
    target = input("Masukkan target IP: ").strip()
    if not validate_ip(target):
        print("[!] Invalid IP, keluar...")
        sys.exit(1)

    # 2. Pilih mode
    mode = main_menu("Pilih mode scanning", [
        "Normal (default scan)",
        "Silent (stealth, lambat, minim jejak)",
        "Brutal (agresif & cepat, noisy)"
    ])

    # 3. Jalankan scan
    print(f"\n[+] Menjalankan scan pada {target} dengan mode {mode}...\n")
    scan_results = runner(target, mode=mode)

    # 4. Mapping eksploit
    print("\n[+] Menganalisis hasil scan & mencari eksploit yang cocok...")
    exploit_recs = mapper(scan_results)

    # 5. Lookup CVE otomatis
    print("\n[+] Melakukan pencarian CVE terkait service terdeteksi...")
    cve_results = []
    for svc in scan_results:
        service = svc.get("service")
        version = svc.get("version")
        if service:
            cves = cve_lookup.search_cve(service, version)
            if cves:
                cve_results.extend(cves)

    # 6. Konfirmasi exploit
    if exploit_recs:
        print("\n[?] Rekomendasi exploit ditemukan:")
        for idx, exp in enumerate(exploit_recs, 1):
            print(f"  {idx}. {exp['tool']} → {exp['desc']}")

        choice = input("\nApakah ingin menjalankan exploit sekarang? (y/n): ").lower()
        if choice == "y":
            idx = int(input("Pilih exploit (nomor): ")) - 1
            if 0 <= idx < len(exploit_recs):
                run_exploit(target, exploit_recs[idx], mode)
            else:
                print("[!] Pilihan tidak valid, melewati exploit.")

    # 7. Post-exploit intel gathering
    choice = input("\nApakah ingin melakukan post-exploit intel gathering? (y/n): ").lower()
    intel_results = {}
    if choice == "y":
        intel_results = intel.run_intel_collection()

    # 8. Simpan laporan
    all_results = {
        "target": target,
        "timestamp": now_iso(),
        "scan_results": scan_results,
        "exploit_recommendations": exploit_recs,
        "cve_results": cve_results,
        "post_exploit_intel": intel_results
    }

    report.save_json_report(all_results, f"report_{target}.json")
    report.save_markdown_report(all_results, f"report_{target}.md")

    print("\n[+] Proses selesai! Report tersimpan di folder data/reports.\n")


if __name__ == "__main__":
    main()
