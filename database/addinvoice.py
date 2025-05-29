# @/constructor/add.py

import os
import sqlite3
from datetime import datetime
import inquiry
import time

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
INQUIRY_FUNCTIONS = {
    'cj': inquiry.cj_inquiry,
    'po': inquiry.po_inquiry,
}

def add_invoice(company: str, invoice: str, window_size: int = 1):
    """
    指定された送り状番号を中心に、window_sizeの範囲で複数の配送データを処理し、SQLiteデータベースに追加します。

    パラメータ:
        company (str): 配送会社のコード（例: 'cj', 'po'）
        invoice (str): 送り状番号（数値文字列）
        window_size (int): 処理する範囲（デフォルトは1）

    戻り値:
        list[dict]: 各送り状の処理結果（success, finishを含む辞書）
    """
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
    """
    タイムスタンプの形式に応じて、datetimeオブジェクトに変換します。

    パラメータ:
        ts (Union[str, int]): 日時を表す文字列またはUNIXタイムスタンプ（秒）

    戻り値:
        datetime or None: 変換に成功した場合はdatetime、失敗した場合はNone
    """
    try: 
        if isinstance(ts, int): return datetime.fromtimestamp(ts)
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def _update_database(pairs, cur):
    """
    location_identifierごとに、timedeltaの値をデータベースに保存または更新します。

    パラメータ:
        pairs (list[tuple[str, str]]): 位置識別子と対応するtimedeltaのペアのリスト
        cur (sqlite3.Cursor): アクティブなカーソルオブジェクト
    """
    for loc_id, delta in pairs:
        cur.execute('SELECT timedeltas FROM raw WHERE location_identifier = ?', (loc_id,))
        row = cur.fetchone()

        if row:
            updated = row[0] + ";" + delta
            cur.execute('UPDATE raw SET timedeltas = ? WHERE location_identifier = ?', (updated, loc_id))
        else:
            cur.execute('INSERT INTO raw (location_identifier, timedeltas) VALUES (?, ?)', (loc_id, delta))

    print(f"[DEBUG] updated {len(pairs)} entries")
