# modules/scanning/runner.py
import sys
from modules.scanning import nmap_engine, rustscan_engine, shodan_engine

def run_scan(ip: str, mode: str):
    """
    Jalankan full scan:
    1. RustScan untuk fast port discovery
    2. Nmap untuk service detection
    3. Shodan API untuk intel tambahan
    """
    print("[*] Running RustScan...")
    try:
        rust_results = rustscan_engine.scan_with_rustscan(ip, mode)
    except Exception as e:
        print(f"[!] RustScan error: {e}")
        rust_results = {}

    print("[*] Running Nmap...")
    try:
        nmap_results = nmap_engine.scan_with_nmap(ip, mode)
    except Exception as e:
        print(f"[!] Nmap error: {e}")
        nmap_results = {}

    print("[*] Querying Shodan API...")
    try:
        shodan_results = shodan_engine.shodan_scan(ip)
    except Exception as e:
        print(f"[!] Shodan error: {e}")
        shodan_results = {}

    # Gabungkan hasil semua engine
    results = {
        "rustscan": rust_results,
        "nmap": nmap_results,
        "shodan": shodan_results
    }

    return results