"""
modules/reporting/report.py
Advanced reporting system for DXploit.
Exports scan, mapping, exploit results into JSON/Markdown/HTML.
"""

import os, json, datetime
from core.utils import ensure_dir

REPORT_DIR = os.path.join("data", "reports")
ensure_dir(REPORT_DIR)

def save_json_report(data, filename="report.json"):
    path = os.path.join(REPORT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] JSON report saved: {path}")
    return path

def save_markdown_report(data, filename="report.md"):
    path = os.path.join(REPORT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# DXploit Report\n\nGenerated: {datetime.datetime.now()}\n\n")
        for section, content in data.items():
            f.write(f"## {section}\n")
            if isinstance(content, list):
                for item in content:
                    f.write(f"- {item}\n")
            elif isinstance(content, dict):
                for k,v in content.items():
                    f.write(f"- **{k}**: {v}\n")
            else:
                f.write(str(content)+"\n")
            f.write("\n")
    print(f"[+] Markdown report saved: {path}")
    return path
