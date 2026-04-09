from config import get_db
import os

base_dir = os.path.dirname(__file__)
schema_file = os.path.join(base_dir, 'schema.sql')

db = get_db()
cur = db.cursor()

with open(schema_file) as f:
    cur.execute(f.read())

db.commit()
cur.close()
db.close()
print("Database schema initialized successfully.")
