import subprocess
import json

def scan_with_rustscan(target, mode="normal"):
    """
    Jalankan RustScan terhadap target.
    mode:
      - normal: default (balanced)
      - silent: stealth (pakai --ulimit rendah + tanpa banner)
      - brutal: cepat/agresif (pakai --ulimit tinggi + timeout rendah)
    """

    try:
        if mode == "silent":
            cmd = [
                "rustscan", "-a", target,
                "--ulimit", "100",
                "--", "-Pn", "-sV"
            ]
        elif mode == "brutal":
            cmd = [
                "rustscan", "-a", target,
                "--ulimit", "10000",
                "--timeout", "1000",
                "--", "-Pn", "-sV"
            ]
        else:  # normal
            cmd = [
                "rustscan", "-a", target,
                "--ulimit", "5000",
                "--", "-Pn", "-sV"
            ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        return {"raw_output": result.stdout}

    except FileNotFoundError:
        return {"error": "RustScan tidak ditemukan. Install dulu dengan: cargo install rustscan"}
    except Exception as e:
        return {"error": str(e)}
