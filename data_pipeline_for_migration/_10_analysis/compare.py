# analysis/compare.py

from _04_matching.document_match import (
    prepare_document_match_data,
    document_exact_match_fen_to_im,
    document_exact_match_im_to_fen,
    build_doc_fen_to_im_result,
    build_doc_im_to_fen_result
)

from _04_matching.client_match_v2 import (
    prepare_client_match_data,
    client_match_fen_to_im,
    client_match_im_to_fen,
    build_fen_to_im_client_result,
    build_im_to_fen_client_result
)


# ============================================================
# DOCUMENT : FEN -> IM
# ============================================================

def build_doc_fen_to_im(
    fen_client_doc,
    im_client_doc
):

    fen, im = prepare_document_match_data(
        fen_client_doc,
        im_client_doc
    )

    match_df = document_exact_match_fen_to_im(
        fen,
        im
    )

    return build_doc_fen_to_im_result(
        fen,
        im,
        match_df
    )


# ============================================================
# DOCUMENT : IM -> FEN
# ============================================================

def build_doc_im_to_fen(
    fen_client_doc,
    im_client_doc
):

    fen, im = prepare_document_match_data(
        fen_client_doc,
        im_client_doc
    )

    match_df = document_exact_match_im_to_fen(
        fen,
        im
    )

    return build_doc_im_to_fen_result(
        fen,
        im,
        match_df
    )


# ============================================================
# CLIENT : FEN -> IM
# ============================================================

def build_client_fen_to_im(
    fen_client_doc,
    im_client_doc
):

    cfen, cim = prepare_client_match_data(
        fen_client_doc,
        im_client_doc
    )

    match_df = client_match_fen_to_im(
        cfen,
        cim
    )

    return build_fen_to_im_client_result(
        cfen,
        cim,
        match_df
    )


# ============================================================
# CLIENT : IM -> FEN
# ============================================================

def build_client_im_to_fen(
    fen_client_doc,
    im_client_doc
):

    cfen, cim = prepare_client_match_data(
        fen_client_doc,
        im_client_doc
    )

    match_df = client_match_im_to_fen(
        cfen,
        cim
    )

    return build_im_to_fen_client_result(
        cfen,
        cim,
        match_df
    )

if __name__ == "__main__":

    import pandas as pd

    from _10_analysis.build_fen_client_doc import (
        build_fen_client_doc
    )

    pd.set_option(
        "display.max_columns",
        None
    )

    pd.set_option(
        "display.width",
        None
    )

    pd.set_option(
        "display.max_colwidth",
        None
    )

    print(
        "\nBuilding real fen_client_doc..."
    )

    fen_client_doc = build_fen_client_doc()

    print("\n" + "=" * 80)
    print("FEN_CLIENT_DOC - LE=180")
    print("=" * 80)

    cols = [
        "LegalEntityId",
        "DocumentId",
        "RoleType",
        "RoleStatus"
    ]

    existing_cols = [
        c
        for c in cols
        if c in fen_client_doc.columns
    ]

    print(
        fen_client_doc.loc[
            fen_client_doc["LegalEntityId"] == 180,
            existing_cols
        ]
        .drop_duplicates()
        .sort_values(
            existing_cols
        )
        .to_string(index=False)
    )

    print(
        "\nRows:",
        len(
            fen_client_doc[
                fen_client_doc["LegalEntityId"] == 180
            ]
        )
    )


# if __name__ == "__main__":

    import pandas as pd

    print("Testing compare.py")

    fen_test = pd.DataFrame(
        {
            "LegalEntityId": [
                "1001",
                "1002"
            ],
            "LegalEntityName": [
                "ABC CAPITAL INC",
                "XYZ HOLDINGS LTD"
            ],
            "ReferenceId": [
                "",
                "2002"
            ],
            "Alias1": [
                "ABC CAPITAL",
                ""
            ],
            "Alias2": [
                "",
                "XYZ HOLDINGS"
            ],
            "Alias3": [
                "",
                ""
            ],
            "Alias4": [
                "",
                ""
            ],
            "DocumentName": [
                "KYC FORM",
                "AML FORM"
            ],
            "iManage_Doc_Num": [
                "101",
                ""
            ]
        }
    )

    im_test = pd.DataFrame(
        {
            "c1alias": [
                "1001",
                "2002"
            ],
            "C_DESCRIPT": [
                "ABC CAPITAL INC",
                "XYZ HOLDINGS LIMITED"
            ],
            "docname": [
                "KYC FORM",
                "AML FORM"
            ],
            "docnum": [
                "101",
                "999"
            ]
        }
    )

    print("\n--------------------------------")
    print("DOCUMENT FEN -> IM")
    print("--------------------------------")

    doc_fen_to_im = build_doc_fen_to_im(
        fen_test,
        im_test
    )

    print(doc_fen_to_im.head())

    print("\n--------------------------------")
    print("DOCUMENT IM -> FEN")
    print("--------------------------------")

    doc_im_to_fen = build_doc_im_to_fen(
        fen_test,
        im_test
    )

    print(doc_im_to_fen.head())

    print("\n--------------------------------")
    print("CLIENT FEN -> IM")
    print("--------------------------------")

    client_fen_to_im = build_client_fen_to_im(
        fen_test,
        im_test
    )

    print(client_fen_to_im.head())

    print("\n--------------------------------")
    print("CLIENT IM -> FEN")
    print("--------------------------------")

    client_im_to_fen = build_client_im_to_fen(
        fen_test,
        im_test
    )

    print(client_im_to_fen.head())

    print("\n--------------------------------")
    print("FINAL FEN -> IM")
    print("--------------------------------")

    final_fen_to_im = doc_fen_to_im.merge(
        client_fen_to_im[
            [
                "LegalEntityId",
                "ClientMatchBoolean",
                "ClientMatchedBy",
                "ClientMatchLayer",
                "ClientNameScore",
                "RefClientID"
            ]
        ],
        on="LegalEntityId",
        how="left",
        suffixes=("", "_client")
    )

    print(final_fen_to_im.head())

    print("\n--------------------------------")
    print("FINAL IM -> FEN")
    print("--------------------------------")

    final_im_to_fen = doc_im_to_fen.merge(
        client_im_to_fen[
            [
                "c1alias",
                "ClientMatchBoolean",
                "ClientMatchedBy",
                "ClientMatchLayer",
                "ClientNameScore",
                "RefClientID"
            ]
        ],
        on="c1alias",
        how="left",
        suffixes=("", "_client")
    )

    print(final_im_to_fen.head())

    print("\ncompare.py unit test completed.")