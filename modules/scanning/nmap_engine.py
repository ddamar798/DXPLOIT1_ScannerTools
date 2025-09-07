# modules/scanning/nmap_engine.py
import shutil, subprocess
from typing import Optional, List

def has_nmap() -> bool:
    return shutil.which("nmap") is not None

def run_nmap_direct(target: str, extra_args: Optional[List[str]] = None, timeout: int = 300) -> str:
    """
    Runs nmap and returns XML output as text.
    Example args: ["-sV", "-p", "1-65535"]
    """
    if not has_nmap():
        raise RuntimeError("nmap not found on PATH")
    args = ["nmap"]
    args.extend(extra_args or ["-sV", "-oX", "-"])
    args.append(target)
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    return proc.stdout
