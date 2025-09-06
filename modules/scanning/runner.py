from modules.scanning import rustscan_engine, nmap_engine, shodan_engine

def run_scan(target, engine, mode):
    print(f"\n🚀 Menjalankan {engine.upper()} scan dengan mode: {mode.upper()} ...")

    if engine == "rustscan":
        return rustscan_engine.scan(target, mode)
    elif engine == "nmap":
        return nmap_engine.scan(target, mode)
    elif engine == "shodan":
        return shodan_engine.scan(target)
    else:
        return []
