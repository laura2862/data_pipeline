# pipeline/05_final_im.py

import pandas as pd
from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv
from _01_config.settings import OUTPUT_FOLDER,TEMP_FOLDER


def main():

    doc_im_to_fen = load_csv(
        OUTPUT_FOLDER / "doc_im_to_fen.csv"
    )

    client_im_to_fen = load_csv(
        OUTPUT_FOLDER / "client_im_to_fen.csv"
    )

    print(
        "Before:",
        len(client_im_to_fen)
    )

    print(
        "Distinct c1alias:",
        client_im_to_fen["c1alias"]
        .nunique()
    )
    print(
        "Duplicate c1alias:",
        client_im_to_fen["c1alias"]
        .duplicated()
        .sum()
    )



    client_im_to_fen = (
        client_im_to_fen[
            [
                "c1alias",
                 "C_DESCRIPT",
                "ClientMatchBoolean",
                "ClientMatchedBy",
                "ClientMatchLayer",
                "RefClientID"
            ]
        ]
        .sort_values(
            ["c1alias", "ClientMatchLayer"]
        )
 
        
        .reset_index(drop=True)
   
    )

    print(
        "After:",
        len(client_im_to_fen)
    )

    final_im_to_fen = doc_im_to_fen.merge(
        client_im_to_fen ,
        on="c1alias",
        how="left"
    )

    final_im_to_fen = (
        final_im_to_fen
        .drop(columns=["C_DESCRIPT_y"])
        .rename(
        columns={ "C_DESCRIPT_x": "C_DESCRIPT"}))


    # final_im_to_fen.to_csv(
    #     OUTPUT_FOLDER / "final_im_to_fen.csv",
    #     index=False
    # )
    save_to_csv(  final_im_to_fen, OUTPUT_FOLDER / "final_im_to_fen.csv")
    # ==================================================
    # Summary
    # ==================================================

    print("\n==================================================")
    print("FINAL IM TO FEN SUMMARY")
    print("==================================================")

    print("Rows   :", len(final_im_to_fen))
    print("Columns:", len(final_im_to_fen.columns))

    if "DocMatchedBy" in final_im_to_fen.columns:

        print("\nDocument Match Breakdown")
        print(
            final_im_to_fen["DocMatchedBy"]
            .value_counts(dropna=False)
        )

    if "ClientMatchedBy" in final_im_to_fen.columns:

        print("\nClient Match Breakdown")
        print(
            final_im_to_fen["ClientMatchedBy"]
            .value_counts(dropna=False)
        )

    # ==================================================
    # Sample Row
    # ==================================================

    print("\n==================================================")
    print("SAMPLE ROW")
    print("==================================================")

    if not final_im_to_fen.empty:

        sample = (
            final_im_to_fen
            .head(1)
            .to_dict("records")[0]
        )

        print(sample)

    print("final_im_to_fen.csv saved")


if __name__ == "__main__":
    main()
