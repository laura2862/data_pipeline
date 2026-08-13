from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd

def get_fenergo_engine():

    server = "wvdbsp01160.bns.bns,5150"
    database = "FenergoData"

    conn_str = quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={conn_str}"
    )


if __name__ == "__main__":

    from sqlalchemy import text

    print("Testing Fenergo Connection...")

    try:

        engine = get_fenergo_engine()

        with engine.connect() as conn:

            df = pd.read_sql(
                text("""
                    SELECT TOP 3 Id
                    FROM LegalEntity
                """),
                conn
            )

            print("Connected successfully")
            print(f"Rows returned: {len(df)}")
            print(df.head())

    except Exception as e:

        print("Connection failed")
        print(e)