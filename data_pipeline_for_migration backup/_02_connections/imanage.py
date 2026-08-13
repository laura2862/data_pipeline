from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd

def get_imanage_engine():

    server = "wvdbsp02291.bns.bns,5150"
    database = "WS_GCMD"

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

    print("Testing iManage Connection...")

    try:

        engine = get_imanage_engine()

        with engine.connect() as conn:

            df = pd.read_sql(
                text("""
                    SELECT TOP 3 docnum
                    FROM mhgroup.docmaster
                """),
                conn
            )

            print("Connected successfully")
            print(f"Rows returned: {len(df)}")
            print(df.head())

    except Exception as e:

        print("Connection failed")
        print(e)