import sqlite3

# DB 연결 및 테이블 생성
conn = sqlite3.connect('kvstore.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT
)
''')
conn.commit()

# 데이터 넣기 함수
def set_value(key, value):
    cursor.execute('REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
    conn.commit()

# 데이터 가져오기 함수
def get_value(key):
    cursor.execute('SELECT value FROM kv WHERE key = ?', (key,))
    result = cursor.fetchone()
    return result[0] if result else None

# 사용 예시
# set_value('name', 'Alice')
# set_value('age', '25')

print(get_value('name'))  # 출력: Alice
print(get_value('age'))   # 출력: 25
print(get_value('nonexist'))  # 출력: None

conn.close()
