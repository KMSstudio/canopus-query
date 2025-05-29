# constructor/show.py

import sqlite3
import os
import sys

def dump(database_name='database.db', output_file=''):
    """
    Print or save all contents of a SQLite database.

    Parameters:
        database_name (str): Name of the SQLite database file.
        output_file (str): If given, write output to file. If empty, print to console.
    """
    
    main_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    db_path = database_name if os.path.isabs(database_name) else os.path.join(main_dir, database_name)

    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    output_lines = []

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        output_lines.append(f"# Table: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cursor.fetchall()]
        output_lines.append(" | ".join(columns))

        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        for row in rows:
            output_lines.append(" | ".join(str(cell) for cell in row))
        output_lines.append("")

    conn.close()

    if output_file:
        output_path = output_file if os.path.isabs(output_file) else os.path.join(main_dir, output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(output_lines))
    else:
        print("\n".join(output_lines))
