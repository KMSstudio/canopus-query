import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time

def po_inquiry(invoice: str):
    url = f"https://service.epost.go.kr/trace.RetrieveDomRigiTraceList.comm?sid1={invoice}"
    response = requests.get(url)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.select('table.table_col > tbody > tr')

    table = []
    remove_keywords = ["TEL", "("]
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.select('td')]
        if len(cols) >= 4:
            try:
                dt = datetime.strptime(cols[0] + " " + cols[1], "%Y.%m.%d %H:%M")
                timestamp = int(time.mktime(dt.timetuple()))
            except ValueError:
                continue

            location_raw = cols[2]
            cut = [location_raw.find(k) for k in remove_keywords if k in location_raw]
            location = location_raw[:min(cut)].strip() if cut else location_raw.strip()

            table.append({
                "location": location,
                "status": re.sub(r'\s*\(.*?\)', '', cols[3]),
                "timestamp": timestamp
            })

    return {
        "success": True,
        "finish": bool(table and '완료' in table[-1]['status']),
        "table": table
    }
