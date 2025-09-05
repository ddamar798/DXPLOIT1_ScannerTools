DXPLOIT – Stealth Recon/Scanning/Enumeration
================================================================

Tujuan:
- Melakukan scanning & enumeration ringan untuk pembelajaran/pentest yang berizin
- Tanpa ketergantungan ke Nmap/Wireshark; murni Python + opsional Scapy (SYN)
- "Silent" mode: rate-limit, delay + jitter, urutan acak, timeout ketat
- Dukungan SOCKS proxy (PySocks) agar bisa routing via proxy (mirip proxychains)
- Output rapi (tabel & JSON) + rekomendasi lanjutan untuk eksploitasi (high-level)

ETIKA/LEGAL:
- Gunakan HANYA pada aset milik sendiri atau dengan izin tertulis (Rules of Engagement).
- Penulis tidak bertanggung jawab atas penyalahgunaan.

Dependensi opsional:
- PySocks  (untuk SOCKS proxy) -> pip install PySocks
- scapy    (opsional untuk SYN scan) -> pip install scapy  (butuh root)

Contoh pakai:
  python3 dxploit.py

Catatan:
- Mode SYN memerlukan hak root dan scapy. Jika tidak tersedia, fallback ke TCP connect scan.
- Tool ini tidak mengeksekusi eksploit; hanya memberi rekomendasi high-level berbasis deteksi layanan.
