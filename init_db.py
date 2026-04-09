from config import get_db
import os
import subprocess
import sys

# Use seed_data.sql if it exists (includes data), otherwise fall back to schema only
base_dir = os.path.dirname(__file__)
seed_file = os.path.join(base_dir, 'seed_data.sql')
schema_file = os.path.join(base_dir, 'schema.sql')

database_url = os.getenv("DATABASE_URL")

if os.path.exists(seed_file):
    result = subprocess.run(
        ['psql', database_url, '-f', seed_file],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error loading seed_data.sql:", result.stderr)
        sys.exit(1)
    print("Database initialized from seed_data.sql")
else:
    db = get_db()
    cur = db.cursor()
    with open(schema_file) as f:
        cur.execute(f.read())
    db.commit()
    cur.close()
    db.close()
    print("Database initialized from schema.sql")
