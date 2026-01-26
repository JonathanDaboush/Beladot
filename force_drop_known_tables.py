import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def quote_ident(name):
    return '"' + name.replace('"', '""') + '"'

conn = psycopg2.connect(dbname='divina_dev', user='postgres', password='postgres', host='localhost', port=5432)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Forcibly drop category table if it exists
cur.execute('DROP TABLE IF EXISTS "category" CASCADE;')

# Optionally, drop other known tables that might persist
other_tables = [
    'subcategory', 'user', 'users', 'product', 'product_image', 'product_variant', 'cart', 'order', 'shipment',
    'manager', 'employee', 'department', 'customer_component', 'address_snapshot', 'alembic_version'
]
for tbl in other_tables:
    cur.execute(f"DROP TABLE IF EXISTS {quote_ident(tbl)} CASCADE;")

cur.close()
conn.close()
print('category and other known tables forcibly dropped from divina_dev.')
