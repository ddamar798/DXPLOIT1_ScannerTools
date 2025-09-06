# modules/scanner/rustscan_nmap.py
import shutil
import subprocess
from typing import Tuple, Optional


def which_binary(name: str) -> bool:
    return shutil.which(name) is not None


def run_rustscan_then_nmap(target: str, nmap_extra_args: Optional[list] = None, timeout: int = 120) -> Tuple[bool, str]:
    """
    Run rustscan as front-end and let it call nmap for detailed fingerprinting.
    We instruct rustscan to pass nmap arguments via `--`.
    Return (success, nmap_xml_output_or_error_message)
    """
    if not which_binary("rustscan"):
        return False, "rustscan not found on PATH"

    # build nmap args; ensure we request XML to stdout (-oX -)
    nmap_args = ["-oX", "-", "-sV"]
    if nmap_extra_args:
        nmap_args.extend(nmap_extra_args)

    # Full rustscan command: rustscan -a <target> -- <nmap args...>
    cmd = ["rustscan", "-a", target, "--"] + nmap_args

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "rustscan timed out"
    except Exception as e:
        return False, f"failed to run rustscan: {e}"

    # rustscan typically prints nmap XML to stdout if nmap args include -oX -
    xml_out = proc.stdout.strip()
    if not xml_out:
        # return stderr for debugging
        return False, proc.stderr.strip() or "rustscan returned empty output"
    return True, xml_out
