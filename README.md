# Redflood v1.0
Catatan Penting: Redflood bukan Ddos 
RedFlood adalah simulator serangan DoS (Denial of Service), bukan DDoS.

Tool ini bekerja dari satu mesin (single source) untuk mensimulasikan tekanan terhadap server target, tanpa menggunakan sistem terdistribusi atau botnet.

Tujuannya adalah untuk:

Pengujian lokal

Latihan pribadi

Demonstrasi keamanan jaringan secara legal

  
_By [@nimendp](https://github.com/nimendp) – For Ethical Hacking & Educational Purposes Only_

---

## 🚀 Deskripsi Singkat

**RedFlood** adalah tool berbasis terminal (CLI) yang ditulis dengan Python untuk kebutuhan pengujian keamanan dan edukasi. Tool ini memungkinkan pengintaian terhadap target website dan simulasi serangan (stress testing) terhadap server, guna:

- Mengidentifikasi kelemahan keamanan
- Menguji ketahanan server terhadap beban ekstrem
- Mengevaluasi efektivitas sistem pertahanan seperti WAF (Web Application Firewall)

---

## 🧠 Fitur Utama

- ✅ **Dual Mode CLI**: Otomatisasi via argumen CLI atau mode interaktif
- 🔍 **Reconnaissance Lengkap**:
  - Deteksi server (Apache, Nginx), backend (PHP, WordPress, Laravel)
  - Deteksi WAF (Cloudflare, Sucuri)
  - Pemindaian port umum (80, 443, 3306, dll.)
- 💥 **Beragam Mode Serangan**:
  - Layer 7 (HTTP): `http-get`, `goldeneye`
  - Layer 4: `udp-flood`, `syn-flood`
  - Layer 3: `icmp-flood`
- 🛡️ **Support Proxy**:
  - Proxy tunggal (`--proxy`)
  - File list proxy (`--proxy-file proxies.txt`)
- 📊 **Live Dashboard (TUI)** dengan [rich](https://github.com/Textualize/rich):
  - Statistik real-time (RPS, sukses/gagal)
  - Grafik permintaan (RPS)
  - Log kejadian saat serangan berlangsung
- 📁 **Laporan HTML Otomatis** setelah serangan selesai
- 🔐 **Cek Otomatis Hak Akses** (misal: `sudo` untuk `syn-flood`, `icmp`)

---

## 🧪 Cara Install

### 1. Buat Virtual Environment (Opsional Tapi Disarankan)

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
-----------------------------------------
2. Install Dependencies
Buat file requirements.txt:

txt
Copy
Edit
requests
rich
matplotlib
h2
pysocks
Lalu install:

bash
Copy
Edit
pip install -r requirements.txt
---------------------------------------
Cara Menjalankan
🔹 Mode Interaktif (GUI CLI)
bash
Copy
Edit
python redflood.py
Kamu akan diminta memasukkan target, mode serangan, jumlah thread, dan durasi.

🔹 Mode Argumen (Cepat)
bash
Copy
Edit
python redflood.py <target> <mode> <threads> <duration> [opsi]
Contoh:

Serangan HTTP:

bash
Copy
Edit
python redflood.py http://example.com http-get 100 60
Serangan SYN (butuh sudo):

bash
Copy
Edit
sudo python redflood.py 192.168.1.1 syn-flood 50 120
Gunakan file proxy:

bash
Copy
Edit
python redflood.py https://target.com goldeneye 200 300 --proxy-file proxies.txt
Hanya Recon:

bash
Copy
Edit
python redflood.py http://example.com --recon-only
📄 Parameter CLI
Parameter	Deskripsi	Contoh
target	URL/IP target	http://example.com
mode	Metode serangan (lihat bawah)	http-get
threads	Jumlah thread	100
duration	Durasi serangan dalam detik	60
--port	(Opsional) Port spesifik	--port 8080
--proxy	(Opsional) Proxy tunggal	--proxy socks5h://127.0.0.1:9050
--proxy-file	(Opsional) File list proxy	--proxy-file proxies.txt
--recon-only	Hanya lakukan reconnaissance, tanpa serangan	--recon-only

🖥️ Contoh Output (Live Dashboard)
yaml
Copy
Edit
RedFlood v1.0 - Live Attack Dashboard

┏━━━━━━━━━━ Info Serangan ━━━━━━━━━━┓ ┏━━━━━━ Statistik ━━━━━━┓
┃ 🎯 Target: http://example.com     ┃ ┃ Total Permintaan: 15,834 ┃
┃ 💥 Mode:   HTTP-GET               ┃ ┃ RPS:           263.90 ┃
┃ ⏳ Durasi: 60 detik               ┃ ┃ ✅ Berhasil:   15,834 ┃
┃ 🧵 Threads: 100                  ┃ ┃ ❌ Gagal:          0 ┃
┃ 🛰️ Proxy: Tidak ada              ┃ ┃ 📤 Data:    0.0000 GB ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┗━━━━━━━━━━━━━━━━━━━━━━━┛
📊 Laporan HTML
Setelah serangan selesai, laporan HTML otomatis akan disimpan di folder saat ini dengan format:

php-template
Copy
Edit
RedFlood_Report_<target>_<timestamp>.html
⚠️ Hak Akses
Untuk beberapa serangan (seperti syn-flood, icmp-flood), kamu harus menjalankan script sebagai root / sudo:

bash
Copy
Edit
sudo python redflood.py 192.168.1.1 syn-flood 100 60
📝 Lisensi
MIT License

---------------------------------------------
Copyright (c) 2024 URWAH

Permission is hereby granted, free of charge, to any person obtaining a copy...
Lihat file LICENSE untuk detail lengkap.

👨‍💻 Author
Dibuat oleh: URWAH (@nimendp)
Tool ini dikembangkan untuk keperluan edukasi dan ethical hacking.

⚠️ Disclaimer: RedFlood hanya untuk pengujian keamanan legal dan edukasi. Jangan gunakan di sistem tanpa izin eksplisit.
