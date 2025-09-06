#!/usr/bin/env python3
"""
DXploit - Main Entry Point
Author: Damarr & Anonim?
Description: Unified entry point untuk DXploit.
"""

import sys
from core.menu import main_menu
from core.utils import banner

def main():
    try:
        banner()
        main_menu()
    except KeyboardInterrupt:
        print("\n[!] User interrupted. Exiting DXploit...")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
