<div align="center">
  <h1>🎓 SNBP 2026 Modern PTN Data Scraper</h1>
  <p>
    <b>Maximal. Powerful. Zero Data Miss.</b> <br>
    <i>Scraping lebih dari 4.000+ data program studi dan 76+ PTN se-Indonesia secara rapi dalam hitungan detik.</i>
  </p>

  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
  [![BS4](https://img.shields.io/badge/BeautifulSoup4-Enabled-success?style=for-the-badge)](https://pypi.org/project/beautifulsoup4/)
  [![Pandas](https://img.shields.io/badge/Pandas-Data%20Extraction-orange?style=for-the-badge&logo=pandas)](https://pandas.pydata.org/)
  [![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)](LICENSE)
</div>

<hr>

## 💡 Tentang Project

Scraper ini dirancang secara khusus untuk mengambil keseluruhan data **Daya Tampung SNBP 2026** dan **Peminat 2025** langsung dari portal antarmuka resmi [SNPMB](https://snpmb.id/snbp/daftar-ptn-snbp). 

Memanfaatkan penelusuran multithreading tingkat lanjut, script ini mendeteksi endpoint master pada website *frontend*, sekaligus menelusuri endpoint backend (Cloud Run) untuk membypass redudansi tabel. Strategi hibrida ini dirancang demi **menjamin 100% akurasi data tanpa *miss* (menghindari PTN yang tertukar dengan Master list) dan menyapu bersih data yang dulunya berlabel *Unknown***.

Berbeda dengan implementasi *scraping* serial tradisional, script ini bekerja secara paralel (Async) dengan kapabilitas eksekusi yang tak terhentikan meskipun ada *connection block* dari server.

## ✨ Fitur Utama

- **🚀 Ultra-Fast Concurrency**: Dilengkapi dengan arsitektur `ThreadPoolExecutor` (Multi-Threading) yang mengeksekusi *request* secara async. Script ini siap menyedot seluruh 76 Kampus dalam < 5 detik!
- **🔗 Hybrid Endpoint Lookup**: Mengekstrak Kode Asli kampus dari front-end (`snpmb.id`) demi penamaan *file* yang sangat akurat, dan menembak *original source API* untuk ketepatan baris data prodi.
- **🛡️ Rock-Solid Resilience**: Menggunakan `requests.Session()` lengkap dengan `HTTPAdapter` & `urllib3 Retry`. Tahan banting 100% terhadap interupsi server seperti HTTP 403, 429, dan 500 limit.
- **📁 Multi-Format Export**: Sistem cerdas yang mengompresi data menjadi Individual Output (Per Kampus) dan Master Rekapitulasi (Seluruh Kampus Tergabung).

## 🚀 Instalasi & Cara Penggunaan

1. **Clone repository ini**
   ```bash
   git clone https://github.com/Afra4509/scrapping-data-ptn-2026.git
   cd scrapping-data-ptn-2026
   ```

2. **Install dependensi yang dibutuhkan**
   Kamu hanya membutuhkan beberapa library populer Python:
   ```bash
   pip install requests beautifulsoup4 pandas tqdm
   ```

3. **Jalankan Scraper**
   Jalankan mesin utamanya untuk segera memanen data ke komputer Anda:
   ```bash
   python alok.py
   ```

## 📂 Struktur Output

Setelah proses scraping selesai dan status progres mencapai 100%, sistem akan secara otomatis membuat folder bersih dengan *timestamp* waktu nyata (real-time):

```text
scrape_results_20260321_010720/
├── csv/
│   ├── 1111_UNIVERSITAS_SYIAH_KUALA.csv
│   ├── 1112_UNIVERSITAS_MALIKUSSALEH.csv
│   └── ...
├── json/
│   ├── 1111_UNIVERSITAS_SYIAH_KUALA.json
│   ├── 1112_UNIVERSITAS_MALIKUSSALEH.json
│   └── ...
├── MASTER_all_prodi.csv     <-- Kompilasi Lengkap Seluruh PTN
└── MASTER_all_prodi.json    <-- Kompilasi Lengkap Seluruh PTN
```

## 📈 Metadata Ekstraksi

Setiap *record* (baris program studi) di-design untuk memastikan kemudahan baca dan konversi ke SQL/NoSQL masa depan dengan atribut berikut yang sangat presisi:
- `NO`: Nomor urut prodi di dalam PTN tersebut
- `KODE_PTN`: ID Resmi Kampus (Cth: 1111)
- `NAMA_PTN`: Nama Lengkap Universitas TANPA URL (Cth: UNIVERSITAS SYIAH KUALA)
- `KODE_PRODI`: Kode identitas jurusan skala nasional
- `NAMA_PRODI`: Nama jurusan penerima SNBP
- `JENJANG`: Sarjana / Sarjana Terapan / Diploma Tiga dsb.
- `DAYA_TAMPUNG_2026`: Kuota mahasiswa baru penerimaan tahun 2026 update
- `PEMINAT_2025`: Histori keketatan dan total peminat jurusan di tahun sebelumnya
- `JENIS_PORTOFOLIO`: Syarat keterampilan khusus program studi

---
<div align="center">
  <b>Dibuat dengan 💻 dan ⚡.</b> <br> Jangan lupa tinggalkan Bintang (⭐️) pada <a href="https://github.com/Afra4509/scrapping-data-ptn-2026">repo ini</a> jika pekerjaan ini membantu Anda!
</div>
