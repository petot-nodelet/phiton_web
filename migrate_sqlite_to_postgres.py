# migrate_sqlite_to_postgres.py
import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

SRC = os.getenv('SRC_SQLITE', 'sqlite:///users.db')
DST = os.getenv('DATABASE_URL')  # target (Heroku Postgres)

if not DST:
    raise SystemExit("Set DATABASE_URL to target Postgres before running.")

src_engine = create_engine(SRC)
dst_engine = create_engine(DST)

src_meta = MetaData(bind=src_engine)
dst_meta = MetaData(bind=dst_engine)

src_meta.reflect(only=['users'])
dst_meta.reflect()

src_conn = src_engine.connect()
dst_conn = dst_engine.connect()

users = Table('users', src_meta)
rows = src_conn.execute(users.select()).fetchall()
print(f"Found {len(rows)} rows in sqlite 'users' table.")

# If destination doesn't have users table, create using src metadata
if 'users' not in dst_meta.tables:
    print("Creating users table in destination...")
    users.schema = None
    users.metadata = dst_meta
    users.create(bind=dst_engine)
else:
    print("users table exists in destination.")

inserted = 0
for r in rows:
    # Convert to dict
    d = dict(r)
    try:
        dst_conn.execute(users.insert().values(**d))
        inserted += 1
    except Exception as e:
        print("Skipped insert:", e)

print(f"Inserted {inserted} rows to destination.")
src_conn.close()
dst_conn.close()
