import argparse
from sqlalchemy import create_engine, text

def main():
    uri = "postgresql+psycopg2://postgres:zfMnJVFAbaxsav4M@postgresql01.toservers.com:5432/towebs"
    engine = create_engine(uri)
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT table_schema, table_name, column_name 
            FROM information_schema.columns 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            AND (column_name ILIKE '%date%'
                 OR column_name ILIKE '%time%'
                 OR column_name ILIKE '%url%'
                 OR column_name ILIKE '%site%');
        """))
        print("Matching columns:")
        for row in res:
            print(f"{row[0]}.{row[1]} -> {row[2]}")

if __name__ == "__main__":
    main()
