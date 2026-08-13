import pandas as pd
from sqlalchemy import text

def run_sql(engine, sql_text):

    with engine.connect() as conn:

        return pd.read_sql(
            text(sql_text),
            conn
        )