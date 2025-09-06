# modules/scanner/nmap_parser.py
import xml.etree.ElementTree as ET
from typing import Dict, List, Any


def parse_nmap_xml(xml_text: str) -> Dict[str, Any]:
    """
    Parse Nmap XML (-oX -) and return dict:
    {
      "hosts": [
        {
          "address": "1.2.3.4",
          "ports": [
            {"port": 22, "protocol": "tcp", "state": "open", "service": "ssh", "product": "...", "version": "...", "extrainfo": "..."}
          ]
        }, ...
      ],
      "raw_xml": "..."
    }
    """
    out = {"hosts": [], "raw_xml": xml_text}
    try:
        root = ET.fromstring(xml_text)
    except Exception as e:
        return {"error": f"failed to parse nmap xml: {e}", "raw_xml": xml_text}

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
                service_el = port_el.find("service")
                service = service_el.get("name") if service_el is not None else ""
                product = service_el.get("product") if service_el is not None else ""
                version = service_el.get("version") if service_el is not None else ""
                extrainfo = service_el.get("extrainfo") if service_el is not None else ""
                host_obj["ports"].append({
                    "port": portid,
                    "protocol": proto,
                    "state": state,
                    "service": service,
                    "product": product,
                    "version": version,
                    "extrainfo": extrainfo
                })
        out["hosts"].append(host_obj)
    return out
