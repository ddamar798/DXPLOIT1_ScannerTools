import subprocess

def scan_with_nmap(target, mode="normal"):
    """
    Jalankan Nmap scan terhadap target.
    mode:
      - normal: balanced, service & version detection
      - silent: stealth (pakai -sS SYN scan + tanpa ping)
      - brutal: full + aggressive (-A)
    """

    try:
        if mode == "silent":
            cmd = ["nmap", "-sS", "-Pn", "-T2", "-sV", target]
        elif mode == "brutal":
            cmd = ["nmap", "-A", "-T4", target]
        else:  # normal
            cmd = ["nmap", "-sV", "-T3", target]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        return {"raw_output": result.stdout}

    except FileNotFoundError:
        return {"error": "Nmap tidak ditemukan. Install dulu dengan: sudo apt install nmap"}
    except Exception as e:
        return {"error": str(e)}
