import os
import socket
import json
import datetime
from typing import Any


def is_valid_ip(ip: str) -> bool:
    """Cek apakah IP valid."""
    try:
        socket.inet_aton(ip)
        return True
    except Exception:
        return False


def now_iso() -> str:
    """Return waktu sekarang dalam format ISO 8601 (UTC)."""
    return datetime.datetime.utcnow().isoformat() + "Z"


def ensure_dir(path: str):
    """Buat folder jika belum ada."""
    os.makedirs(path, exist_ok=True)


def save_json(path: str, obj: Any):
    """Simpan object Python ke file JSON."""
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> Any:
    """Load file JSON jadi object Python."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
