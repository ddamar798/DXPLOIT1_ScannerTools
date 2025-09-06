# modules/recon/shodan_client.py
import os
import requests
from typing import Tuple, Optional, Dict


SHODAN_URL = "https://api.shodan.io/shodan/host/{}"


def get_shodan_api_key() -> Optional[str]:
    # prefer environment variable
    key = os.environ.get("SHODAN_APIKEY")
    if key:
        return key
    # optionally try .env file (lightweight)
    env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("SHODAN_APIKEY="):
                        return line.strip().split("=", 1)[1].strip()
        except Exception:
            pass
    return None


def query_shodan_host(ip: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Query Shodan host API. Returns (available, message, data)
    available True means query ran and returned data (data is dict).
    If not available or error, returns False and error message.
    """
    key = get_shodan_api_key()
    if not key:
        return False, "SHODAN_APIKEY not configured in env or .env", None

    url = SHODAN_URL.format(ip)
    params = {"key": key}
    try:
        r = requests.get(url, params=params, timeout=15)
    except Exception as e:
        return False, f"request to shodan failed: {e}", None

    if r.status_code == 200:
        try:
            return True, "ok", r.json()
        except Exception as e:
            return False, f"failed to parse shodan json: {e}", None
    elif r.status_code == 404:
        return False, "not found on shodan", None
    else:
        return False, f"shodan api error {r.status_code}: {r.text}", None