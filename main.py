#!/usr/bin/env python3
# main.py - DXploit entrypoint (final)

from core.menu import main_menu

def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting.")
    except Exception as e:
        print(f"[!] Fatal error: {e}")

if __name__ == "__main__":
    main()
