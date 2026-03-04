from sqlalchemy import create_engine, text
engine = create_engine("postgresql+psycopg2://postgres:zfMnJVFAbaxsav4M@postgresql01.toservers.com:5432/towebs")
with engine.connect() as conn:
    res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
    tables = [r[0] for r in res]
    match_tables = []
    for t in tables:
        if 'client' in t.lower() or 'dominio' in t.lower() or 'domain' in t.lower() or 'serv' in t.lower() or 'venc' in t.lower():
            match_tables.append(t)
    print("Matched Tables:")
    print(match_tables)
