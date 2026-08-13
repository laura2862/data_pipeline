import pandas as pd
from pathlib import Path
from _01_config.settings import SQL_FOLDER
from _01_config.settings import TEMP_FOLDER

from _02_connections.imanage import get_imanage_engine
import csv

from _03_extract.sql_runner import run_sql
from _11_loaders.csv_saver import save_to_csv

def main():
    print(f'Extract data from iManage DB, including doc and details...')

    engine = get_imanage_engine()

    queries = [
        "im_doc",
        "im_doc_detail",
        # "im_doc_older_version"
    ]
    
    results = {}

    for q in queries:

        sql = (
            SQL_FOLDER / f"{q}.sql"
        ).read_text(encoding="utf-8")

        df = run_sql(engine, sql)

        # df.to_csv(
        #     TEMP_FOLDER / f"{q}.csv",
        #     index=False,
        #     encoding="utf-8-sig",
        #     quoting=csv.QUOTE_MINIMAL,
        #     quotechar='"',
        #     doublequote=True
        # )
        save_to_csv(df,TEMP_FOLDER / f"{q}.csv")

        print(q, len(df))
        results[q] = df
        print(f"\n{q} sample row:")
        print(df.head(1).to_dict("records")[0] if len(df) else "No rows")

        print(f'\nDone\n')

    return results


if __name__ == "__main__":
    main()

