"""
modules/intel/cve_lookup.py
CVE lookup integration using Vulners API (or local cache).
"""

import requests, os

VULNERS_API = "https://vulners.com/api/v3/search/lucene/"

def search_cve(service: str, version: str = None):
    query = service
    if version:
        query += f" {version}"
    print(f"[+] Searching CVE for: {query}")
    try:
        resp = requests.post(VULNERS_API, json={"query": query, "size": 5})
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for doc in data.get("data", {}).get("search", []):
                results.append({
                    "id": doc["_id"],
                    "title": doc.get("title"),
                    "cvss": doc.get("cvss", "N/A"),
                    "href": doc.get("_source", {}).get("href")
                })
            return results
    except Exception as e:
        print(f"[!] CVE lookup failed: {e}")
    return []
