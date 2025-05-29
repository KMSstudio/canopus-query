# @/constructor/add.py

import os
import sqlite3
from datetime import datetime
import inquiry
import time

# 데이터베이스 파일 경로
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# 배송사별 조회 함수 매핑
INQUIRY_FUNCTIONS = {
    'cj': inquiry.cj_inquiry,
    'po': inquiry.po_inquiry,
}

def add_invoice(company: str, invoice: str, window_size: int = 1):
    results = []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS raw (
            location_identifier TEXT PRIMARY KEY,
            timedeltas TEXT
        )
    ''')

    center = int(invoice)
    for offset in range(-(window_size // 2), (window_size + 1) // 2):
        result = add_one_invoice(company, str(center + offset), cur)
        results.append(result)

    conn.commit()
    conn.close()
    return results

def add_one_invoice(company: str, invoice: str, cur=None):
    if company not in INQUIRY_FUNCTIONS:
        print(f"[ERROR] Unknown company: {company}")
        return {'success': False, 'finish': False}
    inquiry_func = INQUIRY_FUNCTIONS[company]

    # get result
    try: result = inquiry_func(invoice)
    except Exception as e:
        print(f"[ERROR] Inquiry failed for {company}:{invoice} - {e}")
        return {'success': False, 'finish': False}
    if not (result.get("success") and result.get("finish")):
        return {'success': result.get("success", False), 'finish': result.get("finish", False)}
    table = result.get("table", [])
    if len(table) < 2: return
    finish_at = _parse_timestamp(table[-1]["timestamp"])
    if finish_at is None: return

    # parse result
    updates = []
    for row in table[:-1]:
        timestamp = _parse_timestamp(row["timestamp"])
        if timestamp is None: continue
        delta = int((finish_at - timestamp).total_seconds())

        location = row["location"]
        status = row["status"]
        weekday = timestamp.weekday()
        hour_band = timestamp.hour // 2
        location_identifier = f"{location}_{status}_{weekday}T{hour_band}"

        updates.append((location_identifier, str(delta)))

    # Update Database
    if cur is None:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS raw (
                location_identifier TEXT PRIMARY KEY,
                timedeltas TEXT
            )
        ''')
        _update_database(updates, cur)
        conn.commit()
        conn.close()
    else:
        _update_database(updates, cur)

    return {'success': True, 'finish': True}

def _parse_timestamp(ts):
    try: 
        if isinstance(ts, int): return datetime.fromtimestamp(ts)
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def _update_database(pairs, cur):
    for loc_id, delta in pairs:
        cur.execute('SELECT timedeltas FROM raw WHERE location_identifier = ?', (loc_id,))
        row = cur.fetchone()

        if row:
            updated = row[0] + ";" + delta
            cur.execute('UPDATE raw SET timedeltas = ? WHERE location_identifier = ?', (updated, loc_id))
        else:
            cur.execute('INSERT INTO raw (location_identifier, timedeltas) VALUES (?, ?)', (loc_id, delta))

    print(f"[DEBUG] updated {len(pairs)} entries")
