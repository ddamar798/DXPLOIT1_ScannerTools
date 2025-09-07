# core/menu.py
from core.utils import safe_input, validate_ip, pretty_list, now_iso
from core.modes import choose_mode_interactive
from modules.scanning.runner import run_scan
from modules.exploitation.mapper import recommend_for_scan
from modules.exploitation.executor import choose_tool_and_run_for_service
from modules.reporting.report import save_reports
from modules.intel.cve_lookup import search_cve
from modules.post_exploit.intel import collect_post_intel

def main_menu():
    print("="*60)
    print("DXPLOIT - Pentest Automation Toolkit")
    print("="*60)

    target = safe_input("Masukkan target IP/Host: ").strip()
    if not validate_ip(target):
        print("[!] IP tidak valid. Gunakan IPv4. Exit.")
        return

    mode = choose_mode_interactive()
    print(f"[+] Mode: {mode.key}")

    # run scan
    print("[*] Running scan...")
    scan_result = run_scan(target, mode)
    print("\n[*] Scan complete. Results:")
    lines = []
    for host in scan_result.get("hosts", []):
        addr = host.get("address")
        for p in host.get("ports", []):
            if p.get("state") == "open":
                lines.append(f"{addr}:{p['port']}/{p['protocol']} => {p.get('service') or ''} {p.get('product','')}")
    if not lines:
        print("(no open ports found)")
    else:
        pretty_list(lines)

    # recommend exploits
    rec_map = recommend_for_scan(scan_result)
    if rec_map:
        print("\n[+] Recommendations:")
        for svc, recs in rec_map.items():
            print(f"- Service: {svc}")
            for r in recs:
                print(f"    * {r[0]} -> {r[1]}")
    else:
        print("\n[!] No exploit recommendations.")

    # ask to run exploit (auto per-service)
    for svc_name, recs in rec_map.items():
        ans = safe_input(f"Jalankan exploit untuk service {svc_name}? (y/N): ").strip().lower()
        if ans != "y":
            continue
        # find sample service info (pick first matching port)
        service_info = None
        for host in scan_result.get("hosts", []):
            for p in host.get("ports", []):
                if p.get("state")=="open" and (p.get("service") or "").lower().find(svc_name.lower())!=-1:
                    service_info = dict(p)
                    service_info["address"] = host.get("address")
                    break
            if service_info:
                break
        # if none, ask user to input target port
        if not service_info:
            port = safe_input("Masukkan port untuk service ini: ").strip()
            service_info = {"address": target, "port": int(port), "service": svc_name}

        choose_tool_and_run_for_service(service_info, recs, mode.key)

    # CVE lookup summary
    print("\n[*] Performing CVE lookup for discovered services...")
    cves = []
    for host in scan_result.get("hosts", []):
        for p in host.get("ports", []):
            svc = p.get("service") or p.get("product") or ""
            vers = p.get("version") or ""
            if svc:
                found = search_cve(svc, vers)
                if found:
                    cves.extend(found)
    if cves:
        print("\n[+] CVE matches:")
        pretty_list([f"{c['id']} - {c.get('title','')}" for c in cves])
    else:
        print("No CVEs found (or lookup not configured).")

    # post-exploit gather prompt
    do_post = safe_input("\nJalankan post-exploit intel collection (local simulated)? (y/N): ").strip().lower()
    post_results = {}
    if do_post == "y":
        post_results = collect_post_intel()
        print("[+] Post exploit intel collected.")
    # save reports
    meta = {
        "target": target,
        "mode": mode.key,
        "scan": scan_result,
        "recommendations": rec_map,
        "cves": cves,
        "post_exploit": post_results,
        "generated_at": now_iso()
    }
    save_reports(target, meta)
    print("\nAll done. Reports saved.")
