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
            AND (column_name ILIKE '%domain%' 
                 OR column_name ILIKE '%dominio%' 
                 OR column_name ILIKE '%venc%' 
                 OR column_name ILIKE '%client%' 
                 OR column_name ILIKE '%expir%');
        """))
        print("Matching columns:")
        for row in res:
            print(f"{row[0]}.{row[1]} -> {row[2]}")

if __name__ == "__main__":
    main()
