from config import get_db
import os

base_dir = os.path.dirname(__file__)
seed_file = os.path.join(base_dir, 'seed_data.sql')
schema_file = os.path.join(base_dir, 'schema.sql')

sql_file = seed_file if os.path.exists(seed_file) else schema_file
label = 'seed_data.sql' if os.path.exists(seed_file) else 'schema.sql'

db = get_db()
db.autocommit = True
cur = db.cursor()

with open(sql_file) as f:
    # Strip psql meta-commands (lines starting with \) which only work in the psql CLI
    lines = [line for line in f if not line.strip().startswith('\\')]
    content = ''.join(lines)

cur.execute(content)
cur.close()
db.close()
print(f"Database initialized from {label}")
