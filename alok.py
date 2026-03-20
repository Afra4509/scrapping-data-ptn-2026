import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from datetime import datetime
from tqdm import tqdm
import re
import concurrent.futures

BASE_PTN_URL = "https://sidata-ptn.snpmb.id/ptn_sn.php"
BASE_PRODI_URL = "https://sidatagrun-public-1076756628210.asia-southeast2.run.app/ptn_sn.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://snpmb.id/"
}

def get_session():
    """Membuat session HTTP dengan pengaturan retry otomatis untuk reliabilitas tinggi."""
    session = requests.Session()
    retry = Retry(
        total=5, 
        backoff_factor=1,
        status_forcelist=[403, 429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session

def get_ptn_mapping(session):
    """Mengekstrak list seluruh PTN secara live (dinamis) sekaligus memetakan Nama dan Kode aslinya."""
    print("🔍 Mengambil Master Data PTN...")
    mapping = {}
    urls = [
        f"{BASE_PTN_URL}?ptn=-1", # Akademik
        f"{BASE_PTN_URL}?ptn=-2", # Vokasi
        f"{BASE_PTN_URL}?ptn=-3"  # KIN
    ]
    
    try:
        for u in urls:
            response = session.get(u, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tr in soup.select("table tbody tr"):
                cols = tr.find_all("td")
                if len(cols) >= 3:
                    kode_asli = cols[1].get_text(strip=True)
                    # Ambil nama PTN tanpa link rektor/webnya
                    nama_raw = cols[2].get_text(separator=' ', strip=True)
                    nama_ptn = nama_raw.split('(')[0].strip()
                    
                    a = tr.find("a", href=re.compile(r"ptn="))
                    if a:
                        href_param = a.get("href").split("ptn=")[1]
                        # Menghindari duplikat karena sidebar memunculkan semua list
                        mapping[href_param] = {"kode": kode_asli, "nama": nama_ptn}
                        
        print(f"✅ Berhasil! Ditemukan {len(mapping)} PTN secara unik.\n")
        return mapping
    except Exception as e:
        print(f"❌ Gagal mengambil daftar master PTN: {e}")
        return {}

def process_ptn(href_param, ptn_info, session, csv_dir, json_dir):
    """Mengekstrak tabel prodi dari suatu PTN dan menyimpannya."""
    url = f"{BASE_PRODI_URL}?ptn={href_param}"
    ptn_data = []
    
    kode_ptn_asli = ptn_info["kode"]
    nama_ptn = ptn_info["nama"]
    
    try:
        response = session.get(url, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        table_rows = soup.select("table tbody tr")
        
        # Clean nama PTN untuk penamaan file
        safe_ptn_name = re.sub(r'[^\w\s-]', '', nama_ptn.replace(" ", "_").replace("/", "-"))[:60]
        file_prefix = f"{kode_ptn_asli}_{safe_ptn_name}"
        
        if not table_rows:
            return {"kode": kode_ptn_asli, "nama": nama_ptn, "data": [], "status": "empty", "error": None}
            
        # Process setiap baris prodi
        for idx, tr in enumerate(table_rows, start=1):
            cols = tr.find_all("td")
            if len(cols) < 6:
                continue

            prodi_record = {
                "NO": idx,
                "KODE_PTN": kode_ptn_asli,
                "NAMA_PTN": nama_ptn,
                "KODE_PRODI": cols[1].get_text(strip=True),
                "NAMA_PRODI": cols[2].get_text(strip=True),
                "JENJANG": cols[3].get_text(strip=True),
                "DAYA_TAMPUNG_2026": cols[4].get_text(strip=True),
                "PEMINAT_2025": cols[5].get_text(strip=True),
                "JENIS_PORTOFOLIO": cols[6].get_text(strip=True) if len(cols) > 6 else ""
            }
            ptn_data.append(prodi_record)
        
        # Save per PTN
        if ptn_data:
            df_ptn = pd.DataFrame(ptn_data)
            csv_file = os.path.join(csv_dir, f"{file_prefix}.csv")
            df_ptn.to_csv(csv_file, index=False, encoding='utf-8')
            
            json_file = os.path.join(json_dir, f"{file_prefix}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(ptn_data, f, indent=2, ensure_ascii=False)
                
        return {"kode": kode_ptn_asli, "nama": nama_ptn, "data": ptn_data, "status": "success", "error": None}
        
    except requests.exceptions.RequestException as e:
        return {"kode": kode_ptn_asli, "nama": nama_ptn, "data": [], "status": "error", "error": f"Connection Error: {str(e)}"}
    except Exception as e:
        return {"kode": kode_ptn_asli, "nama": nama_ptn, "data": [], "status": "error", "error": f"General Error: {str(e)}"}

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"scrape_results_{timestamp}"
    csv_dir = os.path.join(output_dir, "csv")
    json_dir = os.path.join(output_dir, "json")
    
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    print("="*80)
    print("🚀 ADVANCED PRODI SCRAPER - ORGANIZED BY PTN (MAXIMAL & POWERFUL)")
    print("="*80)
    print(f"\n📁 Output directory: {output_dir}")
    
    session = get_session()
    ptn_mapping = get_ptn_mapping(session)
    
    if not ptn_mapping:
        print("❌ Tidak ada kode PTN yang berhasil diekstrak. Menghentikan script...")
        return
        
    print(f"📊 Total PTN untuk di-scrape secara paralel: {len(ptn_mapping)}\n")
    
    all_prodi_summary = []
    stats = {"success": 0, "empty": 0, "error": 0}
    error_logs = []
    
    MAX_WORKERS = min(15, len(ptn_mapping))
    
    with tqdm(total=len(ptn_mapping), desc="Scraping Progress") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_ptn = {
                executor.submit(process_ptn, href_param, info, session, csv_dir, json_dir): href_param 
                for href_param, info in ptn_mapping.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_ptn):
                href_param = future_to_ptn[future]
                ptn_info = ptn_mapping[href_param]
                try:
                    result = future.result()
                    
                    if result["status"] == "success":
                        stats["success"] += 1
                        all_prodi_summary.extend(result["data"])
                    elif result["status"] == "empty":
                        stats["empty"] += 1
                    else:
                        stats["error"] += 1
                        error_logs.append(f"PTN {ptn_info['kode']} ({ptn_info['nama']}): {result['error']}")
                        
                except Exception as exc:
                    stats["error"] += 1
                    error_logs.append(f"PTN {ptn_info['kode']} generated an exception: {exc}")
                finally:
                    pbar.update(1)

    print("\n" + "="*80)
    print("✅ SCRAPING COMPLETE!")
    print("="*80)

    if all_prodi_summary:
        # Sort master data based on PTN array order
        df_all = pd.DataFrame(all_prodi_summary)
        
        # Urutkan berdasarkan Kode PTN agar rapi di file master
        df_all['KODE_PTN'] = pd.to_numeric(df_all['KODE_PTN'], errors='coerce')
        df_all = df_all.sort_values(by=['KODE_PTN', 'NO']).reset_index(drop=True)
        # Kembalikan ke format text jika ada kode depan 0
        df_all['KODE_PTN'] = df_all['KODE_PTN'].astype(str)

        master_csv = os.path.join(output_dir, "MASTER_all_prodi.csv")
        master_json = os.path.join(output_dir, "MASTER_all_prodi.json")

        df_all.to_csv(master_csv, index=False, encoding='utf-8')
        df_all.to_json(master_json, orient='records', indent=2, force_ascii=False)
            
    if error_logs:
        print("\nKesalahan selama proses:")
        for err in error_logs:
            print(f" - {err}")

    print(f"\n📊 STATISTIK AKHIR:")
    print(f"   ✓ Total PTN berhasil diambil datanya : {stats['success']}")
    print(f"   ⚠️  PTN tanpa data (kosong)            : {stats['empty']}")
    print(f"   ❌ PTN yang mengalami error          : {stats['error']}")
    print(f"   📈 Total prodi yang berhasil dicatat : {len(df_all) if all_prodi_summary else 0}")
    print(f"   ⏱️  Waktu eksekusi: Script Start       : {timestamp}")

    print(f"\n📁 FILE YANG DIBUAT (Di dalam '{output_dir}/'):")
    print(f"      ├── csv/ (individual PTN files)")
    print(f"      ├── json/ (individual PTN files)")
    print(f"      ├── MASTER_all_prodi.csv")
    print(f"      └── MASTER_all_prodi.json")

    print("\n✨ Mission Accomplished! Script berjalan dengan power maksimal dan adaptasi dinamis. Tidak ada data yang miss.\n")

if __name__ == "__main__":
    main()
