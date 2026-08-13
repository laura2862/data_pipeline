# _05_pipeline/_03_match_clients.py

from __future__ import annotations

from pathlib import Path

from _01_config.settings import TEMP_FOLDER
from _01_config.settings import OUTPUT_FOLDER

from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv

from _04_matching.client_match import (
    prepare_client_match_data,
    client_match_fen_to_im,
    client_match_im_to_fen,
    build_fen_to_im_client_result,
    build_im_to_fen_client_result,
)


# ============================================================
# Helpers
# ============================================================

def require_file(path: Path) -> None:
    """
    Raise a clear error if a required input file is missing.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Required input file is missing: {path}"
        )


def print_shape(name: str, df) -> None:
    """
    Print dataframe shape in a consistent format.
    """

    print(
        f"{name}: rows={len(df):,}, columns={len(df.columns):,}"
    )


# ============================================================
# Main
# ============================================================

def main() -> None:
    """
    Run Step 03 Client Match.

    Inputs:
        temp/fen_client_doc.csv
        temp/im_client_doc.csv

    Outputs:
        output/client_fen_to_im.csv
        output/client_im_to_fen.csv
    """

    print("\n" + "=" * 100)
    print("STEP 03 - CLIENT MATCH")
    print("=" * 100)

    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    fen_client_doc_path = (
        TEMP_FOLDER /
        "fen_client_doc.csv"
    )

    im_client_doc_path = (
        TEMP_FOLDER /
        "im_client_doc.csv"
    )

    require_file(
        fen_client_doc_path
    )

    require_file(
        im_client_doc_path
    )

    print("\nLoading client document inputs...")

    fen_client_doc = load_csv(
        fen_client_doc_path
    )

    im_client_doc = load_csv(
        im_client_doc_path
    )

    print_shape(
        "fen_client_doc",
        fen_client_doc
    )

    print_shape(
        "im_client_doc",
        im_client_doc
    )

    print("\nPreparing client match data...")

    cfen, cim = prepare_client_match_data(
        fen_client_doc=fen_client_doc,
        im_client_doc=im_client_doc,
    )

    print_shape(
        "prepared FEN clients",
        cfen
    )

    print_shape(
        "prepared IM clients",
        cim
    )

    print("\nRunning FEN -> IM client matching...")

    fen_to_im_match_df = client_match_fen_to_im(
        cfen=cfen,
        cim=cim,
    )

    print_shape(
        "fen_to_im_match_df",
        fen_to_im_match_df
    )

    print("\nRunning IM -> FEN client matching...")

    im_to_fen_match_df = client_match_im_to_fen(
        cfen=cfen,
        cim=cim,
    )

    print_shape(
        "im_to_fen_match_df",
        im_to_fen_match_df
    )

    print("\nBuilding final client match outputs...")

    client_fen_to_im = build_fen_to_im_client_result(
        cfen=cfen,
        cim=cim,
        match_df=fen_to_im_match_df,
    )

    client_im_to_fen = build_im_to_fen_client_result(
        cfen=cfen,
        cim=cim,
        match_df=im_to_fen_match_df,
    )

    print_shape(
        "client_fen_to_im",
        client_fen_to_im
    )

    print_shape(
        "client_im_to_fen",
        client_im_to_fen
    )

    client_fen_to_im_path = (
        OUTPUT_FOLDER /
        "client_fen_to_im.csv"
    )

    client_im_to_fen_path = (
        OUTPUT_FOLDER /
        "client_im_to_fen.csv"
    )

    print("\nSaving client match outputs...")

    save_to_csv(
        client_fen_to_im,
        client_fen_to_im_path
    )

    save_to_csv(
        client_im_to_fen,
        client_im_to_fen_path
    )

    require_file(
        client_fen_to_im_path
    )

    require_file(
        client_im_to_fen_path
    )

    print("\nSaved outputs:")
    print(client_fen_to_im_path)
    print(client_im_to_fen_path)

    print("\n" + "=" * 100)
    print("STEP 03 - CLIENT MATCH COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()