import sys
from core import menu
from modules.scanning.runner import run_scan
from core.utils import validate_ip

def main():
    print("🔥 DXploit v3 – Pentest Automation Framework 🔥")
    print("=============================================")

    # Step 1: Input target
    target = input("🎯 Masukkan Target IP/Host: ").strip()
    if not validate_ip(target):
        print("❌ Target tidak valid!")
        sys.exit(1)

    # Step 2: Pilih Engine
    engine = menu.choose_engine()

    # Step 3: Pilih Mode
    mode = menu.choose_mode()

    # Step 4: Jalankan scanning
    results = run_scan(target, engine, mode)

    # Step 5: Output hasil
    print("\n📊 Hasil Scan:")
    for r in results:
        print(f"  - Port {r['port']} | Service: {r['service']} | Product: {r['product']} {r['version']}")

    print("\n✅ Scan selesai! Lanjutkan ke eksploitasi sesuai rekomendasi.")

if __name__ == "__main__":
    main()
