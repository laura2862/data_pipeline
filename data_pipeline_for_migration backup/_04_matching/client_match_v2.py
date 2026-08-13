# matching/client_match.py

import re
import pandas as pd
import numpy as np

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from _01_config.settings import TEMP_FOLDER

# ============================================================
# CLEANING HELPERS
# ============================================================

def clean_key(value):
    """
    Clean exact-match key fields.
    Keep IDs as text.
    Remove accidental trailing .0 from CSV import.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    if value.endswith(".0"):
        value = value[:-2]

    return value


def clean_text(value):
    """
    Clean text fields for fuzzy matching.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()
    value = re.sub(r"[^A-Z0-9 ]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value


# ============================================================
# SPARSE TOP-N COSINE HELPER
# ============================================================

def sparse_topn_cosine(
    left_matrix,
    right_matrix,
    top_k=20,
    min_cosine=0.20
):
    """
    Return sparse top-k cosine matrix.

    left_matrix:
        TF-IDF matrix for left side

    right_matrix:
        TF-IDF matrix for right side

    Output:
        sparse matrix C where:
            C[i, j] = cosine similarity
            between left row i and right row j

    Uses sparse_dot_topn if available.
    """

    try:
        from sparse_dot_topn import sp_matmul_topn

        return sp_matmul_topn(
            left_matrix,
            right_matrix.T,
            top_n=top_k,
            threshold=min_cosine,
            sort=True
        )

    except Exception:
        try:
            from sparse_dot_topn import awesome_cossim_topn

            return awesome_cossim_topn(
                left_matrix,
                right_matrix.T,
                ntop=top_k,
                lower_bound=min_cosine
            )

        except Exception as e:
            raise ImportError(
                "sparse-dot-topn is required for scalable fuzzy matching. "
                "Install it using: pip install sparse-dot-topn"
            ) from e


# ============================================================
# TF-IDF + RAPIDFUZZ RESCORING
# ============================================================

def tfidf_rapidfuzz_best_matches(
    left_df,
    right_df,
    left_text_col,
    right_text_col,
    left_id_col,
    right_id_col,
    right_ref_col,
    threshold=85,
    top_k=20,
    min_cosine=0.20,
    layer_no=None,
    layer_name=None,
    direction="fen_to_im"
):
    """
    Scalable fuzzy matching.

    Step 1:
        Use TF-IDF char 3-grams to generate top-k candidates.

    Step 2:
        Rescore only candidates using RapidFuzz token_sort_ratio.

    Step 3:
        Keep best RapidFuzz match >= threshold.

    This avoids O(N*M) matching.

    Returns:
        match dataframe for one fuzzy layer.
    """

    if left_df.empty or right_df.empty:
        if direction == "fen_to_im":
            return pd.DataFrame(
                columns=[
                    "__fen_row_id",
                    "__im_row_id",
                    "ClientMatchBoolean",
                    "ClientMatchedBy",
                    "ClientMatchLayer",
                    "ClientNameScore",
                    "RefClientID"
                ]
            )
        else:
            return pd.DataFrame(
                columns=[
                    "__im_row_id",
                    "__fen_row_id",
                    "ClientMatchBoolean",
                    "ClientMatchedBy",
                    "ClientMatchLayer",
                    "ClientNameScore",
                    "RefClientID"
                ]
            )

    left_work = left_df[
        left_df[left_text_col] != ""
    ].copy()

    right_work = right_df[
        right_df[right_text_col] != ""
    ].copy()

    if left_work.empty or right_work.empty:
        if direction == "fen_to_im":
            return pd.DataFrame(
                columns=[
                    "__fen_row_id",
                    "__im_row_id",
                    "ClientMatchBoolean",
                    "ClientMatchedBy",
                    "ClientMatchLayer",
                    "ClientNameScore",
                    "RefClientID"
                ]
            )
        else:
            return pd.DataFrame(
                columns=[
                    "__im_row_id",
                    "__fen_row_id",
                    "ClientMatchBoolean",
                    "ClientMatchedBy",
                    "ClientMatchLayer",
                    "ClientNameScore",
                    "RefClientID"
                ]
            )

    left_work = left_work.reset_index(drop=True)
    right_work = right_work.reset_index(drop=True)

    left_text = left_work[left_text_col].fillna("").astype(str)
    right_text = right_work[right_text_col].fillna("").astype(str)

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 3),
        lowercase=False,
        dtype=np.float32,
        min_df=1
    )

    vectorizer.fit(
        pd.concat(
            [
                left_text,
                right_text
            ],
            ignore_index=True
        )
    )

    left_matrix = vectorizer.transform(left_text)
    right_matrix = vectorizer.transform(right_text)

    cosine_matrix = sparse_topn_cosine(
        left_matrix=left_matrix,
        right_matrix=right_matrix,
        top_k=top_k,
        min_cosine=min_cosine
    ).tocsr()

    records = []

    for left_pos in range(cosine_matrix.shape[0]):

        start = cosine_matrix.indptr[left_pos]
        end = cosine_matrix.indptr[left_pos + 1]

        candidate_positions = cosine_matrix.indices[start:end]

        if len(candidate_positions) == 0:
            continue

        left_value = left_text.iloc[left_pos]

        best_score = 0
        best_right_pos = None

        for right_pos in candidate_positions:

            right_value = right_text.iloc[right_pos]

            score = fuzz.token_sort_ratio(
                left_value,
                right_value
            )

            if score > best_score:
                best_score = score
                best_right_pos = right_pos

        if best_right_pos is None:
            continue

        if best_score < threshold:
            continue

        left_row = left_work.iloc[left_pos]
        right_row = right_work.iloc[best_right_pos]

        if direction == "fen_to_im":
            records.append(
                {
                    "__fen_row_id": left_row[left_id_col],
                    "__im_row_id": right_row[right_id_col],
                    "ClientMatchBoolean": 1,
                    "ClientMatchedBy": layer_name,
                    "ClientMatchLayer": layer_no,
                    "ClientNameScore": best_score,
                    "RefClientID": right_row[right_ref_col]
                }
            )
        else:
            records.append(
                {
                    "__im_row_id": left_row[left_id_col],
                    "__fen_row_id": right_row[right_id_col],
                    "ClientMatchBoolean": 1,
                    "ClientMatchedBy": layer_name,
                    "ClientMatchLayer": layer_no,
                    "ClientNameScore": best_score,
                    "RefClientID": right_row[right_ref_col]
                }
            )

    return pd.DataFrame(records)


# ============================================================
# PREPARE CLIENT MATCH DATA
# ============================================================

def prepare_client_match_data(
    fen_client_doc,
    im_client_doc
):
    """
    Prepare client-level matching data.

    Required Fen columns:
        LegalEntityId
        LegalEntityName
        ReferenceId
        Alias1
        Alias2
        Alias3
        Alias4

    Required IM columns:
        c1alias
        C_DESCRIPT
    """

    cfen_cols = [
        "LegalEntityId",
        "LegalEntityName",
        "ReferenceId",
        "Alias1",
        "Alias2",
        "Alias3",
        "Alias4"
    ]

    cim_cols = [
        "c1alias",
        "C_DESCRIPT"
    ]

    missing_fen_cols = [
        col for col in cfen_cols
        if col not in fen_client_doc.columns
    ]

    missing_im_cols = [
        col for col in cim_cols
        if col not in im_client_doc.columns
    ]

    if missing_fen_cols:
        raise KeyError(
            f"Missing columns in fen_client_doc: {missing_fen_cols}"
        )

    if missing_im_cols:
        raise KeyError(
            f"Missing columns in im_client_doc: {missing_im_cols}"
        )

    cfen = fen_client_doc[cfen_cols].copy()
    cim = im_client_doc[cim_cols].copy()

    cfen = cfen.reset_index(drop=True)
    cim = cim.reset_index(drop=True)

    cfen["__fen_row_id"] = cfen.index
    cim["__im_row_id"] = cim.index

    # Exact keys
    cfen["__key_LegalEntityId"] = cfen["LegalEntityId"].apply(clean_key)
    cfen["__key_ReferenceId"] = cfen["ReferenceId"].apply(clean_key)
    cim["__key_c1alias"] = cim["c1alias"].apply(clean_key)

    # Fuzzy text
    cfen["__txt_LegalEntityName"] = cfen["LegalEntityName"].apply(clean_text)
    cfen["__txt_Alias1"] = cfen["Alias1"].apply(clean_text)
    cfen["__txt_Alias2"] = cfen["Alias2"].apply(clean_text)
    cfen["__txt_Alias3"] = cfen["Alias3"].apply(clean_text)
    cfen["__txt_Alias4"] = cfen["Alias4"].apply(clean_text)

    cim["__txt_C_DESCRIPT"] = cim["C_DESCRIPT"].apply(clean_text)

    return cfen, cim


# ============================================================
# CLIENT REFERENCE TABLES
# ============================================================

def build_client_reference_tables(
    cfen,
    cim
):
    """
    Build one-row-per-client reference tables.

    This is critical for performance.

    Client matching should not run at document-row grain.
    """

    cfen_ref = (
        cfen[cfen["__key_LegalEntityId"] != ""]
        .sort_values("__fen_row_id")
        .drop_duplicates(
            subset=["__key_LegalEntityId"],
            keep="first"
        )
        .copy()
    )

    cim_ref = (
        cim[cim["__key_c1alias"] != ""]
        .sort_values("__im_row_id")
        .drop_duplicates(
            subset=["__key_c1alias"],
            keep="first"
        )
        .copy()
    )

    return cfen_ref, cim_ref


# ============================================================
# FEN -> IM CLIENT MATCH
# ============================================================

def client_match_fen_to_im(
    cfen,
    cim,
    threshold=85,
    top_k=20,
    min_cosine=0.20
):
    """
    Fen client left match to IM client.

    Layers:
        1. LegalEntityId = c1alias
        2. ReferenceId = c1alias
        3. LegalEntityName fuzzy C_DESCRIPT
        4. Alias1 fuzzy C_DESCRIPT
        5. Alias2 fuzzy C_DESCRIPT
        6. Alias3 fuzzy C_DESCRIPT
        7. Alias4 fuzzy C_DESCRIPT
    """

    matched_fen_ids = set()
    match_frames = []

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    # --------------------------------------------------------
    # Layer 1: LegalEntityId = c1alias
    # --------------------------------------------------------

    layer1 = cfen_ref.merge(
        cim_ref[
            [
                "__im_row_id",
                "__key_c1alias",
                "c1alias"
            ]
        ],
        left_on="__key_LegalEntityId",
        right_on="__key_c1alias",
        how="inner"
    )

    layer1 = layer1.drop_duplicates(
        subset=["__fen_row_id"],
        keep="first"
    )

    if not layer1.empty:
        tmp = layer1[
            [
                "__fen_row_id",
                "__im_row_id"
            ]
        ].copy()

        tmp["ClientMatchBoolean"] = 1
        tmp["ClientMatchedBy"] = "Layer1_LegalEntityId_c1alias"
        tmp["ClientMatchLayer"] = 1
        tmp["ClientNameScore"] = 100
        tmp["RefClientID"] = layer1["c1alias"].values

        match_frames.append(tmp)

        matched_fen_ids.update(
            tmp["__fen_row_id"].tolist()
        )

    print(f"Client Layer 1 matched: {len(layer1):,}")

    # --------------------------------------------------------
    # Layer 2: ReferenceId = c1alias
    # --------------------------------------------------------

    unmatched_fen = cfen_ref[
        ~cfen_ref["__fen_row_id"].isin(matched_fen_ids)
    ]

    layer2 = unmatched_fen.merge(
        cim_ref[
            [
                "__im_row_id",
                "__key_c1alias",
                "c1alias"
            ]
        ],
        left_on="__key_ReferenceId",
        right_on="__key_c1alias",
        how="inner"
    )

    layer2 = layer2.drop_duplicates(
        subset=["__fen_row_id"],
        keep="first"
    )

    if not layer2.empty:
        tmp = layer2[
            [
                "__fen_row_id",
                "__im_row_id"
            ]
        ].copy()

        tmp["ClientMatchBoolean"] = 1
        tmp["ClientMatchedBy"] = "Layer2_ReferenceId_c1alias"
        tmp["ClientMatchLayer"] = 2
        tmp["ClientNameScore"] = 100
        tmp["RefClientID"] = layer2["c1alias"].values

        match_frames.append(tmp)

        matched_fen_ids.update(
            tmp["__fen_row_id"].tolist()
        )

    print(f"Client Layer 2 matched: {len(layer2):,}")

    # --------------------------------------------------------
    # Fuzzy layers 3-7
    # --------------------------------------------------------

    fuzzy_layers = [
        (
            3,
            "Layer3_LegalEntityName_C_DESCRIPT_fuzzy",
            "__txt_LegalEntityName"
        ),
        (
            4,
            "Layer4_Alias1_C_DESCRIPT_fuzzy",
            "__txt_Alias1"
        ),
        (
            5,
            "Layer5_Alias2_C_DESCRIPT_fuzzy",
            "__txt_Alias2"
        ),
        (
            6,
            "Layer6_Alias3_C_DESCRIPT_fuzzy",
            "__txt_Alias3"
        ),
        (
            7,
            "Layer7_Alias4_C_DESCRIPT_fuzzy",
            "__txt_Alias4"
        )
    ]

    for layer_no, layer_name, fen_text_col in fuzzy_layers:

        unmatched_fen = cfen_ref[
            ~cfen_ref["__fen_row_id"].isin(matched_fen_ids)
        ]

        layer_df = tfidf_rapidfuzz_best_matches(
            left_df=unmatched_fen,
            right_df=cim_ref,
            left_text_col=fen_text_col,
            right_text_col="__txt_C_DESCRIPT",
            left_id_col="__fen_row_id",
            right_id_col="__im_row_id",
            right_ref_col="c1alias",
            threshold=threshold,
            top_k=top_k,
            min_cosine=min_cosine,
            layer_no=layer_no,
            layer_name=layer_name,
            direction="fen_to_im"
        )

        if not layer_df.empty:
            match_frames.append(layer_df)

            matched_fen_ids.update(
                layer_df["__fen_row_id"].tolist()
            )

        print(f"Client Layer {layer_no} matched: {len(layer_df):,}")

    if match_frames:
        match_df = pd.concat(
            match_frames,
            ignore_index=True
        )

        match_df = (
            match_df
            .sort_values(
                [
                    "__fen_row_id",
                    "ClientMatchLayer"
                ]
            )
            .drop_duplicates(
                subset=["__fen_row_id"],
                keep="first"
            )
            .reset_index(drop=True)
        )
    else:
        match_df = pd.DataFrame(
            columns=[
                "__fen_row_id",
                "__im_row_id",
                "ClientMatchBoolean",
                "ClientMatchedBy",
                "ClientMatchLayer",
                "ClientNameScore",
                "RefClientID"
            ]
        )

    return match_df


# ============================================================
# IM -> FEN CLIENT MATCH
# ============================================================

def client_match_im_to_fen(
    cfen,
    cim,
    threshold=85,
    top_k=20,
    min_cosine=0.20
):
    """
    IM client left match to Fen client.
    """

    matched_im_ids = set()
    match_frames = []

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    # --------------------------------------------------------
    # Layer 1: c1alias = LegalEntityId
    # --------------------------------------------------------

    layer1 = cim_ref.merge(
        cfen_ref[
            [
                "__fen_row_id",
                "__key_LegalEntityId",
                "LegalEntityId"
            ]
        ],
        left_on="__key_c1alias",
        right_on="__key_LegalEntityId",
        how="inner"
    )

    layer1 = layer1.drop_duplicates(
        subset=["__im_row_id"],
        keep="first"
    )

    if not layer1.empty:
        tmp = layer1[
            [
                "__im_row_id",
                "__fen_row_id"
            ]
        ].copy()

        tmp["ClientMatchBoolean"] = 1
        tmp["ClientMatchedBy"] = "Layer1_c1alias_LegalEntityId"
        tmp["ClientMatchLayer"] = 1
        tmp["ClientNameScore"] = 100
        tmp["RefClientID"] = layer1["LegalEntityId"].values

        match_frames.append(tmp)

        matched_im_ids.update(
            tmp["__im_row_id"].tolist()
        )

    print(f"Client Layer 1 matched: {len(layer1):,}")

    # --------------------------------------------------------
    # Layer 2: c1alias = ReferenceId
    # --------------------------------------------------------

    unmatched_im = cim_ref[
        ~cim_ref["__im_row_id"].isin(matched_im_ids)
    ]

    layer2 = unmatched_im.merge(
        cfen_ref[
            [
                "__fen_row_id",
                "__key_ReferenceId",
                "LegalEntityId"
            ]
        ],
        left_on="__key_c1alias",
        right_on="__key_ReferenceId",
        how="inner"
    )

    layer2 = layer2.drop_duplicates(
        subset=["__im_row_id"],
        keep="first"
    )

    if not layer2.empty:
        tmp = layer2[
            [
                "__im_row_id",
                "__fen_row_id"
            ]
        ].copy()

        tmp["ClientMatchBoolean"] = 1
        tmp["ClientMatchedBy"] = "Layer2_c1alias_ReferenceId"
        tmp["ClientMatchLayer"] = 2
        tmp["ClientNameScore"] = 100
        tmp["RefClientID"] = layer2["LegalEntityId"].values

        match_frames.append(tmp)

        matched_im_ids.update(
            tmp["__im_row_id"].tolist()
        )

    print(f"Client Layer 2 matched: {len(layer2):,}")

    # --------------------------------------------------------
    # Fuzzy layers 3-7
    # --------------------------------------------------------

    fuzzy_layers = [
        (
            3,
            "Layer3_C_DESCRIPT_LegalEntityName_fuzzy",
            "__txt_LegalEntityName"
        ),
        (
            4,
            "Layer4_C_DESCRIPT_Alias1_fuzzy",
            "__txt_Alias1"
        ),
        (
            5,
            "Layer5_C_DESCRIPT_Alias2_fuzzy",
            "__txt_Alias2"
        ),
        (
            6,
            "Layer6_C_DESCRIPT_Alias3_fuzzy",
            "__txt_Alias3"
        ),
        (
            7,
            "Layer7_C_DESCRIPT_Alias4_fuzzy",
            "__txt_Alias4"
        )
    ]

    for layer_no, layer_name, fen_text_col in fuzzy_layers:

        unmatched_im = cim_ref[
            ~cim_ref["__im_row_id"].isin(matched_im_ids)
        ]

        layer_df = tfidf_rapidfuzz_best_matches(
            left_df=unmatched_im,
            right_df=cfen_ref,
            left_text_col="__txt_C_DESCRIPT",
            right_text_col=fen_text_col,
            left_id_col="__im_row_id",
            right_id_col="__fen_row_id",
            right_ref_col="LegalEntityId",
            threshold=threshold,
            top_k=top_k,
            min_cosine=min_cosine,
            layer_no=layer_no,
            layer_name=layer_name,
            direction="im_to_fen"
        )

        if not layer_df.empty:
            match_frames.append(layer_df)

            matched_im_ids.update(
                layer_df["__im_row_id"].tolist()
            )

        print(f"Client Layer {layer_no} matched: {len(layer_df):,}")

    if match_frames:
        match_df = pd.concat(
            match_frames,
            ignore_index=True
        )

        match_df = (
            match_df
            .sort_values(
                [
                    "__im_row_id",
                    "ClientMatchLayer"
                ]
            )
            .drop_duplicates(
                subset=["__im_row_id"],
                keep="first"
            )
            .reset_index(drop=True)
        )
    else:
        match_df = pd.DataFrame(
            columns=[
                "__im_row_id",
                "__fen_row_id",
                "ClientMatchBoolean",
                "ClientMatchedBy",
                "ClientMatchLayer",
                "ClientNameScore",
                "RefClientID"
            ]
        )

    return match_df


# ============================================================
# BUILD FEN -> IM RESULT
# ============================================================

def build_fen_to_im_client_result(
    cfen,
    cim,
    match_df
):
    """
    Build final Fen -> IM client result.
    One row per LegalEntityId.
    """

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    result = cfen_ref.merge(
        match_df,
        on="__fen_row_id",
        how="left"
    )

    cim_prefixed = cim_ref.copy()

    cim_prefixed.columns = [
        col
        if col.startswith("__")
        else f"im_{col}"
        for col in cim_prefixed.columns
    ]

    result = result.merge(
        cim_prefixed,
        on="__im_row_id",
        how="left"
    )

    result["ClientMatchBoolean"] = (
        result["ClientMatchBoolean"]
        .fillna(0)
        .astype(int)
    )

    result["ClientMatchedBy"] = (
        result["ClientMatchedBy"]
        .fillna("No Client Match")
    )

    result["ClientMatchLayer"] = (
        result["ClientMatchLayer"]
        .fillna(0)
        .astype(int)
    )

    result["ClientNameScore"] = (
        result["ClientNameScore"]
        .fillna(0)
    )

    result["RefClientID"] = (
        result["RefClientID"]
        .fillna("")
    )

    helper_cols = [
        "__fen_row_id",
        "__im_row_id",
        "__key_LegalEntityId",
        "__key_ReferenceId",
        "__txt_LegalEntityName",
        "__txt_Alias1",
        "__txt_Alias2",
        "__txt_Alias3",
        "__txt_Alias4",
        "__key_c1alias",
        "__txt_C_DESCRIPT"
    ]

    result = result.drop(
        columns=[
            c for c in helper_cols
            if c in result.columns
        ],
        errors="ignore"
    )

    return result.reset_index(drop=True)


# ============================================================
# BUILD IM -> FEN RESULT
# ===========================================================

def build_im_to_fen_client_result(
    cfen,
    cim,
    match_df
):
    """
    Build final IM -> Fen client result.
    One row per c1alias.
    """

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    result = cim_ref.merge(
        match_df,
        on="__im_row_id",
        how="left"
    )

    cfen_prefixed = cfen_ref.copy()

    cfen_prefixed.columns = [
        col
        if col.startswith("__")
        else f"fen_{col}"
        for col in cfen_prefixed.columns
    ]

    result = result.merge(
        cfen_prefixed,
        on="__fen_row_id",
        how="left"
    )

    result["ClientMatchBoolean"] = (
        result["ClientMatchBoolean"]
        .fillna(0)
        .astype(int)
    )

    result["ClientMatchedBy"] = (
        result["ClientMatchedBy"]
        .fillna("No Client Match")
    )

    result["ClientMatchLayer"] = (
        result["ClientMatchLayer"]
        .fillna(0)
        .astype(int)
    )

    result["ClientNameScore"] = (
        result["ClientNameScore"]
        .fillna(0)
    )

    result["RefClientID"] = (
        result["RefClientID"]
        .fillna("")
    )

    helper_cols = [
        "__im_row_id",
        "__fen_row_id",
        "__key_c1alias",
        "__txt_C_DESCRIPT",
        "__key_LegalEntityId",
        "__key_ReferenceId",
        "__txt_LegalEntityName",
        "__txt_Alias1",
        "__txt_Alias2",
        "__txt_Alias3",
        "__txt_Alias4"
    ]

    result = result.drop(
        columns=[
            c for c in helper_cols
            if c in result.columns
        ],
        errors="ignore"
    )

    return result.reset_index(drop=True)


# ============================================================
# UNIT TEST
# ============================================================
# ============================================================
# UNIT TEST / DEBUG REAL DATA FOR LE=180
# ============================================================
# ============================================================
# UNIT TEST / DEBUG REAL DATA FOR LE=180
# ============================================================

if __name__ == "__main__":

    import sys
    from pathlib import Path
    import pandas as pd
    
    from _11_loaders.csv_loader import load_csv

    # --------------------------------------------------------
    # Make project root importable when running this file directly
    # --------------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))


    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    TEST_LE = 180

    print("\n" + "=" * 100)
    print(f"CLIENT MATCH DEBUG TEST FOR LegalEntityId = {TEST_LE}")
    print("=" * 100)

    # --------------------------------------------------------
    # Load real pipeline inputs
    # --------------------------------------------------------

    fen_client_doc = load_csv(TEMP_FOLDER/"fen_client_doc.csv")
    im_client_doc = load_csv(TEMP_FOLDER/"im_client_doc.csv")

    print("\nLoaded files:")
    print("fen_client_doc:", fen_client_doc.shape)
    print("im_client_doc :", im_client_doc.shape)

    # --------------------------------------------------------
    # 1. Show raw fen_client_doc rows for LE=180
    # --------------------------------------------------------

    print("\n" + "=" * 100)
    print(f"RAW fen_client_doc ROLES FOR LE={TEST_LE}")
    print("=" * 100)

    raw_cols = [
        "LegalEntityId",
        "LegalEntityName",
        "ReferenceId",
        "DocumentId",
        "DocumentName",
        "RoleType",
        "RoleStatus"
    ]

    raw_cols = [
        c for c in raw_cols
        if c in fen_client_doc.columns
    ]

    le_raw = (
        fen_client_doc.loc[
            fen_client_doc["LegalEntityId"].astype(str).str.replace(".0", "", regex=False) == str(TEST_LE),
            raw_cols
        ]
        .drop_duplicates()
    )

    print(le_raw.to_string(index=False))

    print("\nRaw distinct RoleType / RoleStatus for LE=180:")
    role_cols = [
        c for c in ["LegalEntityId", "RoleType", "RoleStatus"]
        if c in fen_client_doc.columns
    ]

    print(
        fen_client_doc.loc[
            fen_client_doc["LegalEntityId"].astype(str).str.replace(".0", "", regex=False) == str(TEST_LE),
            role_cols
        ]
        .drop_duplicates()
        .sort_values(
            [c for c in ["RoleType", "RoleStatus"] if c in role_cols]
        )
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # 2. Prepare client match data
    # --------------------------------------------------------

    cfen, cim = prepare_client_match_data(
        fen_client_doc,
        im_client_doc
    )

    print("\nPrepared data:")
    print("cfen:", cfen.shape)
    print("cim :", cim.shape)

    # --------------------------------------------------------
    # 3. Build client reference tables
    #    This is the important step because it keeps one row per LegalEntityId.
    # --------------------------------------------------------

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    print("\nReference tables:")
    print("cfen_ref:", cfen_ref.shape)
    print("cim_ref :", cim_ref.shape)

    le_key = clean_key(TEST_LE)

    selected_ref = cfen_ref[
        cfen_ref["__key_LegalEntityId"] == le_key
    ]

    print("\n" + "=" * 100)
    print(f"SELECTED cfen_ref ROW FOR LE={TEST_LE}")
    print("=" * 100)

    print(
        selected_ref.to_string(index=False)
    )

    # --------------------------------------------------------
    # 4. Map selected __fen_row_id back to original fen_client_doc
    #    This tells us exactly which original row was picked by drop_duplicates.
    # --------------------------------------------------------

    if not selected_ref.empty:

        selected_row_id = int(
            selected_ref.iloc[0]["__fen_row_id"]
        )

        print("\nSelected __fen_row_id:", selected_row_id)

        print("\n" + "=" * 100)
        print("ORIGINAL SOURCE ROW SELECTED BY build_client_reference_tables()")
        print("=" * 100)

        selected_source_cols = [
            "LegalEntityId",
            "LegalEntityName",
            "ReferenceId",
            "DocumentId",
            "DocumentName",
            "RoleType",
            "RoleStatus"
        ]

        selected_source_cols = [
            c for c in selected_source_cols
            if c in fen_client_doc.columns
        ]

        print(
            fen_client_doc.loc[
                [selected_row_id],
                selected_source_cols
            ]
            .to_string(index=False)
        )

    else:

        print(
            f"No cfen_ref row found for LegalEntityId={TEST_LE}"
        )

    # --------------------------------------------------------
    # 5. Run Fen -> IM client matching
    # --------------------------------------------------------

    print("\n" + "=" * 100)
    print("RUNNING CLIENT FEN -> IM MATCH")
    print("=" * 100)

    match_df = client_match_fen_to_im(
        cfen,
        cim
    )

    print("\nMatch rows:", len(match_df))

    match_180 = match_df.merge(
        cfen[
            [
                "__fen_row_id",
                "LegalEntityId",
                "LegalEntityName",
                "ReferenceId"
            ]
        ],
        on="__fen_row_id",
        how="left"
    )

    match_180 = match_180[
        match_180["LegalEntityId"].astype(str).str.replace(".0", "", regex=False) == str(TEST_LE)
    ]

    print("\n" + "=" * 100)
    print(f"MATCH_DF FOR LE={TEST_LE}")
    print("=" * 100)

    if match_180.empty:
        print("No client match found for LE=180")
    else:
        print(
            match_180.to_string(index=False)
        )

    # --------------------------------------------------------
    # 6. Build final client_fen_to_im result
    # --------------------------------------------------------

    client_fen_to_im = build_fen_to_im_client_result(
        cfen,
        cim,
        match_df
    )

    print("\n" + "=" * 100)
    print(f"CLIENT_FEN_TO_IM RESULT FOR LE={TEST_LE}")
    print("=" * 100)

    result_cols = [
        "LegalEntityId",
        "LegalEntityName",
        "ReferenceId",
        "ClientMatchBoolean",
        "ClientMatchedBy",
        "ClientMatchLayer",
        "ClientNameScore",
        "RefClientID",
        "im_c1alias",
        "im_C_DESCRIPT"
    ]

    result_cols = [
        c for c in result_cols
        if c in client_fen_to_im.columns
    ]

    print(
        client_fen_to_im.loc[
            client_fen_to_im["LegalEntityId"].astype(str).str.replace(".0", "", regex=False) == str(TEST_LE),
            result_cols
        ]
        .to_string(index=False)
    )

    print("\n" + "=" * 100)
    print("CLIENT MATCH DEBUG TEST COMPLETE")
    print("=" * 100)