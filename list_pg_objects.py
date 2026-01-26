import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(dbname='divina_dev', user='postgres', password='postgres', host='localhost', port=5432)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# List all objects in public schema
print('Tables:')
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
for row in cur.fetchall():
    print('  table:', row[0])

print('Views:')
cur.execute("SELECT table_name FROM information_schema.views WHERE table_schema = 'public'")
for row in cur.fetchall():
    print('  view:', row[0])

print('Materialized Views:')
cur.execute("SELECT matviewname FROM pg_matviews WHERE schemaname = 'public'")
for row in cur.fetchall():
    print('  matview:', row[0])

print('Sequences:')
cur.execute("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public'")
for row in cur.fetchall():
    print('  sequence:', row[0])

print('Types:')
cur.execute("SELECT t.typname FROM pg_type t LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'public' AND t.typtype = 'e'")
for row in cur.fetchall():
    print('  type:', row[0])

cur.close()
conn.close()
