# core/scanner_engine.py
from typing import Dict, Any, Tuple
from modules.recon.shodan_client import query_shodan_host, get_shodan_api_key
from modules.scanner.rustscan_nmap import run_rustscan_then_nmap, which_binary
from modules.scanner.nmap_parser import parse_nmap_xml
from core.utils import save_json, now_iso
import os


RESULTS_DIR = os.path.join("data", "results")


def run_passive_then_active(target: str, prefer_passive: bool = True, nmap_extra_args: list = None) -> Dict[str, Any]:
    """
    1) If prefer_passive and Shodan API key present -> query Shodan for host info.
       If Shodan returns host data, include it in returned result and optionally skip active scan.
    2) Otherwise run rustscan -> nmap (via rustscan wrapper) to obtain nmap XML -> parse.
    """
    result = {"target": target, "timestamp": now_iso(), "engine": {}, "shodan": None, "nmap": None}

    # 1) passive
    skey = get_shodan_api_key()
    if prefer_passive and skey:
        ok, msg, data = query_shodan_host(target)
        result["engine"]["passive_checked"] = True
        result["engine"]["passive_msg"] = msg
        if ok and data:
            result["shodan"] = data
            # we still allow active scan option; but if Shodan provides ports and user wants no active, we can return early.
            # Here we include shodan data and continue active scan by default (decision for DXploit config).
        else:
            # note: if shodan not found, we continue to active scan
            pass
    else:
        result["engine"]["passive_checked"] = False
        if not skey:
            result["engine"]["passive_msg"] = "no shodan api key configured"

    # 2) active via rustscan -> nmap
    # Prefer rustscan if available
    if which_binary("rustscan"):
        success, out = run_rustscan_then_nmap(target, nmap_extra_args=nmap_extra_args)
        if not success:
            result["engine"]["active_error"] = out
        else:
            parsed = parse_nmap_xml(out)
            result["nmap"] = parsed
    else:
        result["engine"]["active_error"] = "rustscan not found; please install rustscan or run nmap fallback (not implemented here)"

    # persist results
    save_path = os.path.join(RESULTS_DIR, f"{target.replace(':','_')}_scan_{now_iso().replace(':','-')}.json")
    save_json(save_path, result)
    result["saved_to"] = save_path
    return result
