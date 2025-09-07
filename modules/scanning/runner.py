# modules/scanning/runner.py
from typing import Dict, Any
from core.utils import now_iso, ensure_dir
from modules.scanning.rustscan_engine import run_rustscan_then_nmap, has_rustscan
from modules.scanning.nmap_engine import run_nmap_direct
from modules.recon.shodan_client import query_shodan_host, get_shodan_api_key
import os

RESULTS_DIR = os.path.join("data", "results")
ensure_dir(RESULTS_DIR)

def run_scan(target: str, mode) -> Dict[str, Any]:
    """
    Orchestrate passive (Shodan) then active (RustScan -> Nmap) scanning.
    Returns dict with keys: hosts, raw_nmap_xml, shodan (optional), timestamp
    """
    result = {"target": target, "timestamp": now_iso(), "hosts": [], "raw_nmap_xml": None, "shodan": None}
    # Passive
    skey = get_shodan_api_key()
    if skey:
        ok, msg, data = query_shodan_host(target)
        result["shodan"] = data if ok else None
    # Active
    # prefer rustscan if available
    if has_rustscan():
        ok, xml = run_rustscan_then_nmap(target)
        if ok:
            from modules.scanning.nmap_parser import parse_nmap_xml
            parsed = parse_nmap_xml(xml)
            result["raw_nmap_xml"] = xml
            result["hosts"] = parsed.get("hosts", [])
        else:
            result["error"] = xml
    else:
        # fallback to nmap direct
        xml = run_nmap_direct(target, extra_args=["-sV", "-oX", "-"])
        from modules.scanning.nmap_parser import parse_nmap_xml
        parsed = parse_nmap_xml(xml)
        result["raw_nmap_xml"] = xml
        result["hosts"] = parsed.get("hosts", [])
    # save
    save_path = os.path.join(RESULTS_DIR, f"{target.replace(':','_')}_scan_{now_iso().replace(':','-')}.json")
    from core.utils import save_json
    save_json(save_path, result)
    result["saved_to"] = save_path
    return result
