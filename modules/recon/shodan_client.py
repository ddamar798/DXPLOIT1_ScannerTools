# modules/recon/shodan_client.py
import os, requests
from typing import Tuple, Optional, Dict

SHODAN_URL = "https://api.shodan.io/shodan/host/{}"

def get_shodan_api_key() -> Optional[str]:
    key = os.environ.get("SHODAN_APIKEY")
    if key:
        return key
    if os.path.exists(".env"):
        try:
            with open(".env","r",encoding="utf-8") as f:
                for ln in f:
                    if ln.strip().startswith("SHODAN_APIKEY="):
                        return ln.strip().split("=",1)[1].strip()
        except Exception:
            pass
    return None

def query_shodan_host(ip: str) -> Tuple[bool, str, Optional[Dict]]:
    key = get_shodan_api_key()
    if not key:
        return False, "no shodan key", None
    url = SHODAN_URL.format(ip)
    params = {"key": key}
    try:
        r = requests.get(url, params=params, timeout=15)
    except Exception as e:
        return False, f"request failed: {e}", None
    if r.status_code == 200:
        try:
            return True, "ok", r.json()
        except Exception as e:
            return False, f"json parse error: {e}", None
    elif r.status_code == 404:
        return False, "not found", None
    else:
        return False, f"shodan error {r.status_code}", None
