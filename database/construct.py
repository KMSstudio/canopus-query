# @/database/construct.py

import os
import sqlite3

def construct():
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, "database.db")

    if not os.path.exists(db_path):
        print("[ERROR] database.db not found")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # read from raw table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw'")
    if not cur.fetchone():
        print("[ERROR] 'raw' table not found in database.db")
        conn.close()
        return

    cur.execute("SELECT location_identifier, timedeltas FROM raw")
    rows = cur.fetchall()

    # drop and create hist table
    cur.execute("DROP TABLE IF EXISTS hist")
    cur.execute("CREATE TABLE hist (location_identifier TEXT PRIMARY KEY, " +
                ", ".join([f"'{i}h' INTEGER" for i in range(1, 49)]) +
                ", sum INTEGER)")

    # drop and create medi table
    cur.execute("DROP TABLE IF EXISTS medi")
    cur.execute("CREATE TABLE medi (location_identifier TEXT PRIMARY KEY, q1 INTEGER, q2 INTEGER, q3 INTEGER, p95 INTEGER, p99 INTEGER)")

    for location_identifier, timedeltas_str in rows:
        try:
            values = sorted(int(v) for v in timedeltas_str.split(";") if v.strip().isdigit())
        except ValueError:
            continue

        count = len(values)
        if count == 0:
            continue

        def percentile_index(p):
            return min(count - 1, int(p * count))

        q1 = values[percentile_index(0.25)]
        q2 = values[percentile_index(0.50)]
        q3 = values[percentile_index(0.75)]
        p95 = values[percentile_index(0.95)]
        p99 = values[percentile_index(0.99)]

        cur.execute(
            "INSERT INTO medi VALUES (?, ?, ?, ?, ?, ?)",
            (location_identifier, q1, q2, q3, p95, p99)
        )

        hist_bins = [0] * 48
        for v in values:
            idx = min(v // 3600, 47)
            hist_bins[idx] += 1

        cur.execute(
            "INSERT INTO hist VALUES (" + ", ".join(["?"] * 50) + ")",
            (location_identifier, *hist_bins, count)
        )

    conn.commit()
    conn.close()
