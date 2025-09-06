# core/utils.py
import os
import socket
import json
import datetime
from typing import Any, Dict


def is_valid_ip(ip: str) -> bool:
    try:
        socket.inet_aton(ip)
        return True
    except Exception:
        return False


def now_iso() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_json(path: str, obj: Any):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pretty_list(lines):
    for i, l in enumerate(lines, start=1):
        print(f"[{i:02d}] {l}")
