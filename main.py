import sys
from core import menu
from modules.scanning.runner import run_scan
from core.utils import validate_ip
from modules.exploitation import mapper

def main():
    print("🔥 DXploit v4 – Pentest Automation Framework 🔥")
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

    # Step 6: Auto-Mapping ke Exploit
    print("\n🎯 Rekomendasi Eksploitasi:")
    for r in results:
        recs = mapper.recommend(r)
        if recs:
            print(f"  - Port {r['port']} ({r['service']}) →")
            for tool, reason in recs:
                print(f"      ⚡ {tool} → {reason}")
        else:
            print(f"  - Port {r['port']} ({r['service']}) → Tidak ada rekomendasi khusus")

    print("\n✅ Selesai! Gunakan exploit sesuai rekomendasi di atas dengan bijak.")

if __name__ == "__main__":
    main()