import sys
from core.modes import choose_mode
from core.utils import is_valid_ip

def main_menu():
    print("=" * 60)
    print("🔥 DXPLOIT - Pentest Automation Framework 🔥")
    print("=" * 60)

    # Input target IP
    target_ip = input("\n[?] Masukkan target IP: ").strip()
    while not is_valid_ip(target_ip):
        print("[!] IP tidak valid. Coba lagi...")
        target_ip = input("[?] Masukkan target IP: ").strip()

    print(f"[✓] Target diset: {target_ip}")

    # Pilih mode scan/attack
    mode = choose_mode()

    # Jalankan scan sesuai mode
    print("\n[⚡] Menjalankan scanning engine...\n")
    from modules.scanner import run_scan
    results = run_scan(target_ip, mode)

    # Output hasil scan
    print("\n" + "=" * 60)
    print("📊 Hasil Scanning")
    print("=" * 60)
    for r in results:
        print(f"Port {r['port']}/{r['proto']} | Service: {r['service']} | Product: {r['product']} {r['version']}")
    
    print("\n[✓] Scanning selesai!")

    # Opsi eksploitasi
    lanjut = input("\n[?] Mau lanjut eksploitasi? (y/n): ").lower()
    if lanjut == "y":
        from modules.exploit import exploit_menu
        exploit_menu(results, target_ip)
    else:
        print("[!] Exit. Bye!")
        sys.exit(0)
