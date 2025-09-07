# core/modes.py
from dataclasses import dataclass


@dataclass
class Mode:
    key: str
    display: str
    description: str
    delay_ms: int
    jitter_ms: int
    aggressive: bool


MODES = {
    "normal": Mode("normal", "Normal", "Balanced speed and stealth", delay_ms=0, jitter_ms=0, aggressive=False),
    "silent": Mode("silent", "Silent", "Slow and stealthy (recommended for live targets)", delay_ms=150, jitter_ms=75, aggressive=False),
    "brutal": Mode("brutal", "Brutal", "Aggressive & fast (noisy). Use only with permission", delay_ms=0, jitter_ms=0, aggressive=True),
}


def choose_mode():
    from core.utils import safe_input
    print("\nPilih mode serangan:")
    for k, m in MODES.items():
        warn = " ⚠️" if m.aggressive else ""
        print(f" - {m.key}: {m.display} - {m.description}{warn}")
    while True:
        pick = safe_input("Masukkan mode (normal/silent/brutal) [normal]: ").strip().lower() or "normal"
        if pick in MODES:
            if MODES[pick].aggressive:
                confirm = safe_input("Brutal mode akan sangat noisy. Pastikan izin tersedia. Ketik YES untuk lanjut: ")
                if confirm.strip().upper() != "YES":
                    print("Batal brutal mode. Kembali ke pilihan.")
                    continue
            return MODES[pick]
        print("[!] Mode tidak dikenali, ulangi.")
