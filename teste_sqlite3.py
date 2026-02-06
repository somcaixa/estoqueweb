import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "estoque.db")

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("PRAGMA table_info(uso_material);")
for c in cur.fetchall():
    print(c)

conn.commit()
conn.close()

print("Coluna 'tipo' adicionada com sucesso")