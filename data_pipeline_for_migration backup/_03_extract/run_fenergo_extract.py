import pandas as pd
from pathlib import Path

from _01_config.settings import SQL_FOLDER
from _01_config.settings import TEMP_FOLDER

from _02_connections.fenergo import get_fenergo_engine

from _03_extract.sql_runner import run_sql
import csv
from _11_loaders.csv_saver import   save_to_csv

def main():
    print(f'Extract data from fenergo DB, including doc, doc detail, client detail, association, product, case...')

    engine = get_fenergo_engine()

    queries = [
        "fen_doc",
        "fen_doc_detail",
        "fen_client_detail_raw",
        "fen_association",
        "fen_product",
        "fen_case",
        "fen_address",
        "fen_contact",
        "fen_taxid",
        "fen_comment"

    ]

    results = {}

    for q in queries:

        sql = (
            SQL_FOLDER / f"{q}.sql"
        ).read_text(encoding="utf-8")

        df = run_sql(engine, sql)
        if q=="fen_client_detail":
            print("\nRoleType Check")
            print(
                
                df["RoleType"]
                .value_counts(dropna=False)
                
                )
        
        if q=="fen_association":
            print("\nAssociation Check")
            print(
                
                df["AssociatedRelationStatus"]
                .value_counts(dropna=False)
            )
                
                
        
        if q=="fen_product":
            print("\nProduct Check")
            print(
                
                df["ProductStatus"]
                .value_counts(dropna=False)
                
                )
            
        if q=="fen_case":
            print("\nCase Check")
            print(
                
                df["CaseType"]
                .value_counts(dropna=False))
        


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