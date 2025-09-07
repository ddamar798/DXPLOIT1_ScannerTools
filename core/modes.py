# core/modes.py
from dataclasses import dataclass

@dataclass
class Mode:
    key: str
    label: str
    delay_ms: int
    jitter_ms: int
    aggressive: bool

MODES = {
    "normal": Mode("normal", "Normal (balanced)", 0, 0, False),
    "silent": Mode("silent", "Silent (stealthy)", 150, 75, False),
    "brutal": Mode("brutal", "Brutal (aggressive)", 0, 0, True),
}

from core.utils import safe_input

def choose_mode_interactive():
    print("\nPilih mode:")
    for k,m in MODES.items():
        warn = " ⚠️" if m.aggressive else ""
        print(f" - {k}: {m.label}{warn}")
    while True:
        pick = safe_input("Mode (normal/silent/brutal) [normal]: ").strip().lower() or "normal"
        if pick in MODES:
            if MODES[pick].aggressive:
                confirm = safe_input("Brutal mode is noisy. Type YES to confirm: ")
                if confirm.strip() != "YES":
                    print("Cancelled brutal mode selection.")
                    continue
            return MODES[pick]
        print("[!] Unknown mode.")
