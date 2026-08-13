# pipeline/02_match_documents.py

import pandas as pd
from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv

from _10_analysis.compare import (
    build_doc_fen_to_im,
    build_doc_im_to_fen
)

from _01_config.settings import OUTPUT_FOLDER,TEMP_FOLDER


def main():

    print("\nLoading csv...")

    # fen_client_doc = pd.read_csv(
    #     TEMP_FOLDER / "fen_client_doc.csv",
    #     low_memory=False
    # )

    fen_client_doc=load_csv( TEMP_FOLDER / "fen_client_doc.csv")

    im_client_doc = pd.read_csv(
        TEMP_FOLDER / "im_client_doc.csv",
        low_memory=False
    )

    print("\nRunning document matching...")


    print("\nBulding doc_fen_to_im...")
    doc_fen_to_im = build_doc_fen_to_im(
        fen_client_doc,
        im_client_doc
    )

    print("\nBulding doc_im_to_fen...")
    doc_im_to_fen = build_doc_im_to_fen(
        fen_client_doc,
        im_client_doc
    )

    # doc_fen_to_im.to_csv(
    #     OUTPUT_FOLDER / "doc_fen_to_im.csv",
    #     index=False
    # )

    # doc_im_to_fen.to_csv(
    #     OUTPUT_FOLDER / "doc_im_to_fen.csv",
    #     index=False
    # )
    save_to_csv(doc_fen_to_im,OUTPUT_FOLDER / "doc_fen_to_im.csv")
    save_to_csv(doc_im_to_fen,OUTPUT_FOLDER / "doc_im_to_fen.csv")

    print(f"\nsaved as csv in {OUTPUT_FOLDER}...")
    print(f"\nSaved as csv in {OUTPUT_FOLDER}")

    # ==================================================
    # Summary
    # ==================================================

    print("\n==================================================")
    print("DOCUMENT MATCH SUMMARY")
    print("==================================================")

    print(f"Doc Fen -> IM rows : {len(doc_fen_to_im):,}")
    print(f"Doc IM  -> Fen rows: {len(doc_im_to_fen):,}")

    if "DocMatchBoolean" in doc_fen_to_im.columns:

        matched = int(doc_fen_to_im["DocMatchBoolean"].sum())

        print(f"\nFen -> IM Matched     : {matched:,}")
        print(f"Fen -> IM Not Matched : {len(doc_fen_to_im)-matched:,}")

        print("\nMatch Breakdown:")
        print(
            doc_fen_to_im["DocMatchedBy"]
            .value_counts(dropna=False)
        )

    if "DocMatchBoolean" in doc_im_to_fen.columns:

        matched = int(doc_im_to_fen["DocMatchBoolean"].sum())

        print(f"\nIM -> Fen Matched     : {matched:,}")
        print(f"IM -> Fen Not Matched : {len(doc_im_to_fen)-matched:,}")

        # ==================================================
        # Sample records
        # ==================================================

        print("\n==================================================")
        print("DOC_FEN_TO_IM SAMPLE")
        print("==================================================")

        if not doc_fen_to_im.empty:
            print(
                doc_fen_to_im.head(1)
                .to_dict("records")[0]
            )

        print("\n==================================================")
        print("DOC_IM_TO_FEN SAMPLE")
        print("==================================================")

        if not doc_im_to_fen.empty:
            print(
                doc_im_to_fen.head(1)
                .to_dict("records")[0]
            )

        print("\nDone.")



if __name__ == "__main__":
    main()
