import sys
from core.utils import is_valid_ip
from core.modes import select_mode
from core.report import save_report
from modules.scanner.normal_scan import normal_scan
from modules.scanner.silent_scan import silent_scan
from modules.exploit.ssh_bruteforce import run_exploit as ssh_exploit
from modules.exploit.postgres_exploit import run_exploit as postgres_exploit
from data.exploits_map import EXPLOITS_MAP


def auto_chain(target: str, mode: str):
    """Auto-chain: scan lalu langsung coba exploit sesuai hasil."""
    print(f"\n[+] Auto-Chain dimulai untuk target {target}\n")

    if mode == "normal":
        results = normal_scan(target)
    else:
        results = silent_scan(target)

    save_report(target, results)

    open_ports = [r["port"] for r in results.get("ports", [])]
    print("\nPort terbuka:", ", ".join(str(p) for p in open_ports))

    # Jalankan exploit sesuai mapping
    for service in results.get("ports", []):
        port = service["port"]
        svc = service["service"]

        if str(port) in EXPLOITS_MAP:
            exploits = EXPLOITS_MAP[str(port)]
            for exp in exploits:
                print(f"\n[+] Menjalankan exploit {exp} untuk {svc} di port {port}")
                if exp == "ssh_bruteforce":
                    ssh_exploit(target, port, mode)
                elif exp == "postgres_exploit":
                    postgres_exploit(target, port, mode)

    print("\n[+] Auto-Chain selesai.\n")


def main():
    print("=== DXploit Framework ===")
    target = input("Masukkan target IP: ").strip()

    if not is_valid_ip(target):
        print("[-] IP tidak valid.")
        sys.exit(1)

    mode = select_mode()

    choice = input("Jalankan Auto-Chain? (y/n): ").lower()
    if choice == "y":
        auto_chain(target, mode)
    else:
        if mode == "normal":
            results = normal_scan(target)
        else:
            results = silent_scan(target)

        save_report(target, results)
        print("\nScan selesai. Report disimpan.")


if __name__ == "__main__":
    main()
