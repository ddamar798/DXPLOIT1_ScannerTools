import subprocess

def scan(target, mode):
    cmd = ["nmap", "-sV", target]

    if mode == "silent":
        cmd = ["nmap", "-sV", "-T2", "-Pn", target]  # slow, no ping
    elif mode == "brutal":
        cmd = ["nmap", "-sV", "-T5", target]  # max speed

    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.splitlines()

    findings = []
    for line in lines:
        if "/tcp" in line and "open" in line:
            parts = line.split()
            port = parts[0]
            service = parts[2]
            product = " ".join(parts[3:]) if len(parts) > 3 else ""
            findings.append({"port": port, "service": service, "product": product, "version": ""})

    return findings
