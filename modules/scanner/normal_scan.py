import socket


def normal_scan(target: str) -> dict:
    """Scan sederhana: cek port umum terbuka."""
    common_ports = [22, 80, 443, 5432]
    results = {"target": target, "ports": []}

    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                results["ports"].append({
                    "port": port,
                    "service": "unknown"
                })
            sock.close()
        except Exception:
            continue

    return results
