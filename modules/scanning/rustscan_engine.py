import subprocess

def scan(target, mode):
    cmd = ["rustscan", "-a", target, "--ulimit", "5000", "--timeout", "1500"]

    if mode == "silent":
        cmd += ["--tries", "2", "--scan-order", "serial"]
    elif mode == "brutal":
        cmd += ["--tries", "5", "--scan-order", "random"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.splitlines()

    findings = []
    for line in lines:
        if "Open" in line:
            port = line.split(" ")[-1]
            findings.append({"port": port, "service": "unknown", "product": "", "version": ""})

    return findings
