import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(dbname='divina_dev', user='postgres', password='password', host='localhost', port=5432)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Drop all tables in public schema
cur.execute('''
DO $$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;
''')

# Drop Alembic version table if exists
cur.execute('DROP TABLE IF EXISTS alembic_version CASCADE;')

cur.close()
conn.close()
print('All tables dropped from divina_dev.')
