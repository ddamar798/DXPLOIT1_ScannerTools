# modules/scanning/shodan_engine.py
import os
import shodan

def shodan_scan(ip: str):
    """
    Lakukan Shodan lookup untuk IP target.
    Membutuhkan SHODAN_API_KEY di environment variable.
    """
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        print("[!] SHODAN_API_KEY belum di-set di environment.")
        return None

    api = shodan.Shodan(api_key)
    try:
        result = api.host(ip)
        print(f"[+] Shodan data for {ip}:")
        for item in result['data']:
            print(f"  - {item['port']}/tcp => {item.get('product', 'Unknown')} {item.get('version', '')}")
        return result
    except shodan.APIError as e:
        print(f"[!] Shodan API error: {e}")
        return None
