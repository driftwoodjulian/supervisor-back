import argparse
from sqlalchemy import create_engine, text

def main():
    uri = "postgresql+psycopg2://postgres:zfMnJVFAbaxsav4M@postgresql01.toservers.com:5432/towebs"
    engine = create_engine(uri)
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name;
        """))
        print("All tables in towebs:")
        for row in res:
            print(f"{row[0]}.{row[1]}")

if __name__ == "__main__":
    main()
