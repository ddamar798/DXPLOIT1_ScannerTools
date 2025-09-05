def select_mode() -> str:
    """Memilih mode scanning/eksploitasi."""
    print("\nPilih mode:")
    print("1. Normal - Kecepatan standar, deteksi biasa")
    print("2. Silent - Lambat, gunakan delay agar lebih stealth")
    print("3. Brutal - Cepat & agresif (tidak disarankan di real test)")

    choice = input("Pilihan (1/2/3): ").strip()

    if choice == "1":
        return "normal"
    elif choice == "2":
        return "silent"
    elif choice == "3":
        confirm = input("Mode brutal bisa terdeteksi. Yakin? (y/n): ").lower()
        if confirm == "y":
            return "brutal"
        else:
            return "normal"
    else:
        print("Input tidak valid, default ke normal.")
        return "normal"
