import argparse
from sqlalchemy import create_engine, text

def main():
    uri = "postgresql+psycopg2://postgres:zfMnJVFAbaxsav4M@postgresql01.toservers.com:5432/towebs"
    engine = create_engine(uri)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT metadata FROM core.contact WHERE metadata IS NOT NULL LIMIT 5;"))
        print("core.contact metadata:")
        for row in res:
            print(row[0])

        res2 = conn.execute(text("SELECT metadata FROM market.market_config WHERE metadata IS NOT NULL LIMIT 5;"))
        print("market.market_config metadata:")
        for row in res2:
            print(row[0])

if __name__ == "__main__":
    main()
