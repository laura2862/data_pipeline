# pipeline/03_match_clients.py

import pandas as pd
from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv

from _10_analysis.compare import (
    build_client_fen_to_im,
    build_client_im_to_fen
)

from _01_config.settings import OUTPUT_FOLDER,TEMP_FOLDER


def main():


    fen_client_doc =load_csv(TEMP_FOLDER / "fen_client_doc.csv")
    im_client_doc =load_csv(TEMP_FOLDER / "im_client_doc.csv")

    print("Running client matching...")

    client_fen_to_im = build_client_fen_to_im(
        fen_client_doc,
        im_client_doc
    )

    client_im_to_fen = build_client_im_to_fen(
        fen_client_doc,
        im_client_doc
    )



    save_to_csv(client_fen_to_im,OUTPUT_FOLDER / "client_fen_to_im.csv")
    save_to_csv(client_im_to_fen, OUTPUT_FOLDER / "client_im_to_fen.csv")


    print(f"\nSaved as csv in {OUTPUT_FOLDER}")

    # ==================================================
    # Summary
    # ==================================================

    print("\n==================================================")
    print("CLIENT MATCH SUMMARY")
    print("==================================================")

    print(f"Client Fen -> IM rows : {len(client_fen_to_im):,}")
    print(f"Client IM  -> Fen rows: {len(client_im_to_fen):,}")

    if "ClientMatchBoolean" in client_fen_to_im.columns:

        matched = int(client_fen_to_im["ClientMatchBoolean"].sum())

        print(f"\nFen -> IM Matched     : {matched:,}")
        print(f"Fen -> IM Not Matched : {len(client_fen_to_im)-matched:,}")

        print("\nMatch Breakdown:")
        print(
            client_fen_to_im["ClientMatchedBy"]
            .value_counts(dropna=False)
        )

    if "ClientMatchBoolean" in client_im_to_fen.columns:

        matched = int(client_im_to_fen["ClientMatchBoolean"].sum())

        print(f"\nIM -> Fen Matched     : {matched:,}")
        print(f"IM -> Fen Not Matched : {len(client_im_to_fen)-matched:,}")

    # ==================================================
    # Sample records
    # ==================================================

    print("\n==================================================")
    print("CLIENT_FEN_TO_IM SAMPLE")
    print("==================================================")

    if not client_fen_to_im.empty:

        sample = (
            client_fen_to_im
            .head(1)
            .to_dict("records")[0]
        )

        print(sample)

    print("\n==================================================")
    print("CLIENT_IM_TO_FEN SAMPLE")
    print("==================================================")

    if not client_im_to_fen.empty:

        sample = (
            client_im_to_fen
            .head(1)
            .to_dict("records")[0]
        )

        print(sample)

    print("\nDone.")


if __name__ == "__main__":
    main()