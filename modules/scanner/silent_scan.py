import socket
import time


def silent_scan(target: str) -> dict:
    """Scan lambat dengan delay agar lebih stealth."""
    common_ports = [22, 80, 443, 5432]
    results = {"target": target, "ports": []}

    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target, port))
            if result == 0:
                results["ports"].append({
                    "port": port,
                    "service": "unknown"
                })
            sock.close()
            time.sleep(1)  # delay silent mode
        except Exception:
            continue

    return results
