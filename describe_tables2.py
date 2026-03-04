import argparse
from sqlalchemy import create_engine, text

def main():
    uri = "postgresql+psycopg2://postgres:zfMnJVFAbaxsav4M@postgresql01.toservers.com:5432/towebs"
    engine = create_engine(uri)
    with engine.connect() as conn:
        tables = ['core.app', 'market.shop_item', 'market.purchase', 'external.plugin_config']
        for t in tables:
            schema, name = t.split('.')
            print(f"--- Schema for {t} ---")
            res = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='{name}';"))
            for row in res:
                print(f"{row[0]}: {row[1]}")
            print("\n")

if __name__ == "__main__":
    main()
