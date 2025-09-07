# modules/reporting/report.py
import os, json, datetime
from core.utils import ensure_dir, now_iso

REPORT_DIR = os.path.join("data","reports")
ensure_dir(REPORT_DIR)

def save_reports(target: str, payload: dict):
    ts = now_iso().replace(":","-")
    json_path = os.path.join(REPORT_DIR, f"report_{target}_{ts}.json")
    md_path = os.path.join(REPORT_DIR, f"report_{target}_{ts}.md")
    with open(json_path,"w",encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    # simple markdown
    with open(md_path,"w",encoding="utf-8") as f:
        f.write(f"# DXploit Report - {target}\nGenerated: {datetime.datetime.utcnow().isoformat()}Z\n\n")
        f.write("## Summary\n")
        f.write(f"- Target: {payload.get('target')}\n- Mode: {payload.get('mode')}\n\n")
        f.write("## Discovered Services\n")
        for h in payload.get("scan", {}).get("hosts", []):
            f.write(f"- Host: {h.get('address')}\n")
            for p in h.get("ports", []):
                f.write(f"  - Port {p.get('port')}/{p.get('protocol')}: {p.get('service')} {p.get('product')} {p.get('version')}\n")
        f.write("\n## Recommendations\n")
        for k,v in (payload.get("recommendations") or {}).items():
            f.write(f"- {k}:\n")
            for item in v:
                f.write(f"  - {item[0]}: {item[1]}\n")
        f.write("\n## CVEs\n")
        for c in payload.get("cves", []):
            f.write(f"- {c.get('id')} {c.get('title')}\n")
    print(f"[+] Reports saved: {json_path}, {md_path}")
    return json_path, md_path
