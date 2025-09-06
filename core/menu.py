from modules.scanning.rustscan_engine import run_rustscan
from modules.scanning.nmap_engine import run_nmap
from modules.scanning.shodan_engine import run_shodan
from core.utils import validate_ip

def main_menu():
    print("\n=== DXploit Main Menu ===")
    print("[1] Scanning")
    print("[2] Exploitation (coming soon)")
    print("[3] Reporting (coming soon)")
    print("[0] Exit")

    choice = input(">> Pilih opsi: ").strip()

    if choice == "1":
        ip = input(">> Masukkan IP target: ").strip()
        if not validate_ip(ip):
            print("[!] IP tidak valid!")
            return
        
        print("\nPilih metode scanning:")
        print("[1] RustScan (super cepat)")
        print("[2] Nmap (detail & akurat)")
        print("[3] Shodan API (intelligence)")

        scan_choice = input(">> Pilih metode: ").strip()

        if scan_choice == "1":
            run_rustscan(ip)
        elif scan_choice == "2":
            run_nmap(ip)
        elif scan_choice == "3":
            run_shodan(ip)
        else:
            print("[!] Pilihan tidak valid!")

    elif choice == "2":
        print("[*] Modul exploitation masih dalam pengembangan.")
    elif choice == "3":
        print("[*] Modul reporting masih dalam pengembangan.")
    elif choice == "0":
        print("[*] Keluar...")
        exit(0)
    else:
        print("[!] Pilihan tidak valid!")
