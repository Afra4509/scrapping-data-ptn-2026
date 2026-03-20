import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://snpmb.id/'}
html = requests.get('https://sidata-ptn.snpmb.id/ptn_sn.php?ptn=111', headers=HEADERS).text
soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')
print('Total tables on ptn=111:', len(tables))

for i, t in enumerate(tables):
    trs = t.find_all('tr')
    if trs:
        headers = [th.text.strip() for th in trs[0].find_all(['th','td'])]
        print(f'Table {i} headers: {headers}')
        if len(trs) > 1:
            first_row = [td.text.strip()[:30] for td in trs[1].find_all('td')]
            print(f'Table {i} first row: {first_row}')

