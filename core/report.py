import os
from core.utils import now_iso, save_json


def save_report(target: str, results: dict):
    """Simpan hasil scan ke folder reports/"""
    ensure_dir("reports")
    filename = f"reports/{target}_{now_iso()}.json"
    save_json(filename, results)
    print(f"[+] Report disimpan di {filename}")
