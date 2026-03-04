import argparse
from sqlalchemy import create_engine, text

def main():
    uri = "postgresql+psycopg2://postgres:zfMnJVFAbaxsav4M@postgresql01.toservers.com:5432/postgres"
    engine = create_engine(uri)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        print("Databases:")
        for row in res:
            print(f"- {row[0]}")

if __name__ == "__main__":
    main()
