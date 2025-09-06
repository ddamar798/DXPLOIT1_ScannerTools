import shodan

API_KEY = "YOUR_SHODAN_API_KEY"

def scan(target):
    api = shodan.Shodan(API_KEY)
    findings = []

    try:
        host = api.host(target)
        for item in host['data']:
            findings.append({
                "port": item['port'],
                "service": item.get('product', 'unknown'),
                "product": item.get('product', ''),
                "version": item.get('version', '')
            })
    except Exception as e:
        print(f"❌ Shodan error: {e}")

    return findings
