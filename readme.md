DXPLOIT – Stealth Recon/Scanning/Enumeration
================================================================

# 🔥 About DXploit : 

DXploit adalah framework pentesting modern berbasis CLI yang menggabungkan tools canggih, akurat, dan stabil yang biasa digunakan para profesional.
Didesain untuk mempercepat workflow pentester: 
mulai dari Recon → Scanning → Vulnerability Mapping → Exploitation → Reporting, 
dalam satu framework otomatis namun tetap fleksibel.

Dengan DXploit, kamu bisa melakukan pentest dengan gaya real offensive security seperti para expert tanpa harus membuka banyak tools manual.

=================================================================

# ✨ Features :

## ✔️ Advanced Scanning Engine :
        - RustScan + Nmap → ultra-fast & detailed service discovery
        - Shodan API integration → intel langsung dari internet

## ✔️ Smart Vulnerability Mapping :
        - Service otomatis dicocokkan ke database exploit (CVE/CWE/Exploit-DB)
        - Prioritas berdasarkan CVSS score

## ✔️ Auto Exploitation (with Confirmation) :
        - sqlmap, Nikto, CrackMapExec, custom exploit integration
        - CLI-friendly menu → pilih metode exploit sebelum jalan
        - Multi-mode scan: normal, silent, brutal :

## ✔️ Credential & Service Attacks :
        - Brute-force & spray dengan CME (CrackMapExec)
        - Support SMB, RDP, SSH, FTP, HTTP login attack

## ✔️ Reporting Ready :
        - Hasil scan & exploit otomatis diexport ke Markdown/PDF
        - Cocok untuk laporan POC ke klien

=================================================================

# 🚀 Installation :

## Clone repository
git clone https://github.com/yourusername/DXPLOIT1_ScannerTools.git
cd DXPLOIT1_ScannerTools

## Buat virtual environment
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

## Install dependencies
pip install -r requirements.txt

=================================================================

# 🛠️ Usage

## Run DXploit:
   -> python3 main.py

## Example CLI Flow:
[1] Recon & Scanning  
[2] Vulnerability Mapping  
[3] Exploitation (SQLi, RCE, Brute Force, etc.)  
[4] Reporting  

Choose option: 1
> Target: 192.168.1.10
> Scan Mode: Brutal
> Engine: RustScan + Nmap + Shodan API

=================================================================

# ⚠️ Disclaimer :

DXploit dibuat untuk tujuan pembelajaran, riset, dan pentest legal.
🚫 Jangan digunakan pada sistem tanpa izin tertulis.
Pengembang tidak bertanggung jawab atas penyalahgunaan tool ini.

=================================================================

# ❤️ Author
### 👤 Damar Prasetyo
Pentester | Offensive Security Enthusiast | Builder of DXploit