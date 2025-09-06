def choose_engine():
    print("\n🔎 Pilih Engine Scanning:")
    print("1. RustScan (cepat & akurat)")
    print("2. Nmap (detail, service detection)")
    print("3. Shodan API (OSINT mode, butuh API key)")
    choice = input("👉 Pilihan [1-3]: ").strip()

    engines = {"1": "rustscan", "2": "nmap", "3": "shodan"}
    return engines.get(choice, "nmap")

def choose_mode():
    print("\n⚡ Pilih Mode Scanning:")
    print("1. Normal → default balance (akurasi & kecepatan seimbang)")
    print("2. Silent → stealthy, dengan delay & evasion (minim jejak)")
    print("3. Brutal → cepat & agresif (cocok stress-test)")
    choice = input("👉 Pilihan [1-3]: ").strip()

    modes = {"1": "normal", "2": "silent", "3": "brutal"}
    return modes.get(choice, "normal")
