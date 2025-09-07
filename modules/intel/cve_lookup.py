# modules/intel/cve_lookup.py
import requests
import time

VULNERS_API = "https://vulners.com/api/v3/search/lucene/"

def search_cve(service: str, version: str = None, size: int = 5):
    q = service
    if version:
        q += " " + version
    try:
        resp = requests.post(VULNERS_API, json={"query": q, "size": size}, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            hits = []
            for d in data.get("data", {}).get("search", []):
                hits.append({
                    "id": d.get("_id"),
                    "title": d.get("title"),
                    "href": d.get("_source", {}).get("href"),
                    "cvss": d.get("cvss")
                })
            return hits
    except Exception as e:
        print(f"[!] CVE lookup failed: {e}")
    return []
