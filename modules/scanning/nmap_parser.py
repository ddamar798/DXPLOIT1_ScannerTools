# modules/scanning/nmap_parser.py
import xml.etree.ElementTree as ET
from typing import Dict, Any

def parse_nmap_xml(xml_text: str) -> Dict[str, Any]:
    out = {"hosts": []}
    try:
        root = ET.fromstring(xml_text)
    except Exception as e:
        return {"hosts": [], "error": str(e)}
    for host in root.findall("host"):
        addr_el = host.find("address")
        addr = addr_el.get("addr") if addr_el is not None else None
        host_obj = {"address": addr, "ports": []}
        ports_el = host.find("ports")
        if ports_el is not None:
            for port_el in ports_el.findall("port"):
                portid = int(port_el.get("portid", "0"))
                proto = port_el.get("protocol", "")
                state_el = port_el.find("state")
                state = state_el.get("state") if state_el is not None else ""
                svc_el = port_el.find("service")
                svc = svc_el.get("name") if svc_el is not None else ""
                product = svc_el.get("product") if svc_el is not None else ""
                version = svc_el.get("version") if svc_el is not None else ""
                extrainfo = svc_el.get("extrainfo") if svc_el is not None else ""
                host_obj["ports"].append({
                    "port": portid,
                    "protocol": proto,
                    "state": state,
                    "service": svc,
                    "product": product,
                    "version": version,
                    "extrainfo": extrainfo
                })
        out["hosts"].append(host_obj)
    return out
