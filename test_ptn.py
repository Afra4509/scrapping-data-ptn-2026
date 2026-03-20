import requests
from bs4 import BeautifulSoup
import re

HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://snpmb.id/'}
urls = [
    'https://sidata-ptn.snpmb.id/ptn_sn.php?ptn=-1',
    'https://sidata-ptn.snpmb.id/ptn_sn.php?ptn=-2',
    'https://sidata-ptn.snpmb.id/ptn_sn.php?ptn=-3'
]
mapping = {}
for u in urls:
    try:
        html = requests.get(u, headers=HEADERS, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')
        for tr in soup.select("table tbody tr"):
            cols = tr.find_all("td")
            if len(cols) >= 3:
                kode = cols[1].get_text(strip=True)
                nama_raw = cols[2].get_text(separator=' ', strip=True)
                nama = nama_raw.split('(')[0].strip()
                a = tr.find("a", href=re.compile(r"ptn="))
                if a:
                    href = a.get("href").split("ptn=")[1]
                    mapping[href] = {"kode": kode, "nama": nama}
    except Exception as e:
        print("Error", u, e)

print("Total mapping:", len(mapping))
print(list(mapping.items())[:5])
