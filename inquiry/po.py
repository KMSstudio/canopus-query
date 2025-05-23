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
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.select('td')]
        if len(cols) >= 4:
            try:
                dt = datetime.strptime(cols[0] + " " + cols[1], "%Y.%m.%d %H:%M")
                timestamp = int(time.mktime(dt.timetuple()))
            except ValueError:
                continue

            table.append({
                "location": cols[2],
                "status": re.sub(r'\s*\(.*?\)', '', cols[3]),
                "timestamp": timestamp
            })

    return {
        "success": True,
        "finish": bool(table and '완료' in table[-1]['status']),
        "table": table
    }
