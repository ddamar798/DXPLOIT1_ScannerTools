# modules/scanning/rustscan_engine.py
import shutil, subprocess
from typing import Tuple, Optional, List

def has_rustscan() -> bool:
    return shutil.which("rustscan") is not None and shutil.which("nmap") is not None

def run_rustscan_then_nmap(target: str, nmap_extra_args: Optional[List[str]] = None, timeout: int = 300) -> Tuple[bool, str]:
    """
    Runs: rustscan -a <target> -- <nmap args>
    We request nmap -oX - -sV to get XML output on stdout.
    """
    if not has_rustscan():
        return False, "rustscan or nmap not found"
    nmap_args = ["-oX", "-", "-sV"]
    if nmap_extra_args:
        nmap_args.extend(nmap_extra_args)
    cmd = ["rustscan", "-a", target, "--", *nmap_args]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "rustscan timed out"
    if proc.returncode != 0 and not proc.stdout:
        return False, proc.stderr.strip() or "rustscan error"
    # rustscan may include banners – but nmap xml expected in stdout
    xml = proc.stdout.strip()
    return True, xml
