# _05_pipeline/matching/client_match.py

from __future__ import annotations

import re
import pandas as pd
import numpy as np

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer


# ============================================================
# Constants
# ============================================================

EMPTY_FEN_TO_IM_COLUMNS = [
    "__fen_row_id",
    "__im_row_id",
    "ClientMatchBoolean",
    "ClientMatchedBy",
    "ClientMatchLayer",
    "ClientNameScore",
    "RefClientID",
]

EMPTY_IM_TO_FEN_COLUMNS = [
    "__im_row_id",
    "__fen_row_id",
    "ClientMatchBoolean",
    "ClientMatchedBy",
    "ClientMatchLayer",
    "ClientNameScore",
    "RefClientID",
]


# ============================================================
# Cleaning Helpers
# ============================================================

def clean_key(value) -> str:
    """
    Clean exact-match key fields.

    Examples:
        123.0 -> 123
        abc -> ABC
        None -> ""
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    if value.endswith(".0"):
        value = value[:-2]

    return value


def clean_text(value) -> str:
    """
    Clean business names and aliases for fuzzy matching.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()
    value = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        value
    )
    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    return value


# ============================================================
# Sparse Cosine Helper
# ============================================================

def sparse_topn_cosine(
    left_matrix,
    right_matrix,
    top_k=20,
    min_cosine=0.20,
):
    """
    Return sparse top-k cosine similarity matrix.

    Requires sparse-dot-topn for scalable candidate generation.
    """

    try:
        from sparse_dot_topn import sp_matmul_topn

        return sp_matmul_topn(
            left_matrix,
            right_matrix.T,
            top_n=top_k,
            threshold=min_cosine,
            sort=True,
        )

    except Exception:
        try:
            from sparse_dot_topn import awesome_cossim_topn

            return awesome_cossim_topn(
                left_matrix,
                right_matrix.T,
                ntop=top_k,
                lower_bound=min_cosine,
            )

        except Exception as exc:
            raise ImportError(
                "sparse-dot-topn is required for scalable fuzzy matching. "
                "Install it using: pip install sparse-dot-topn"
            ) from exc


# ============================================================
# Data Preparation
# ============================================================

def prepare_client_match_data(
    fen_client_doc: pd.DataFrame,
    im_client_doc: pd.DataFrame,
):
    """
    Prepare client-level FEN and IM data.

    Required FEN columns:
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

    fen_cols = [
        "LegalEntityId",
        "LegalEntityName",
        "ReferenceId",
        "Alias1",
        "Alias2",
        "Alias3",
        "Alias4",
    ]

    im_cols = [
        "c1alias",
        "C_DESCRIPT",
    ]

    missing_fen_cols = [
        col for col in fen_cols
        if col not in fen_client_doc.columns
    ]

    missing_im_cols = [
        col for col in im_cols
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

    cfen = (
        fen_client_doc[fen_cols]
        .copy()
        .reset_index(drop=True)
    )

    cim = (
        im_client_doc[im_cols]
        .copy()
        .reset_index(drop=True)
    )

    cfen["__fen_row_id"] = cfen.index
    cim["__im_row_id"] = cim.index

    cfen["__key_LegalEntityId"] = (
        cfen["LegalEntityId"]
        .map(clean_key)
    )

    cfen["__key_ReferenceId"] = (
        cfen["ReferenceId"]
        .map(clean_key)
    )

    cim["__key_c1alias"] = (
        cim["c1alias"]
        .map(clean_key)
    )

    cfen["__txt_LegalEntityName"] = (
        cfen["LegalEntityName"]
        .map(clean_text)
    )

    cfen["__txt_Alias1"] = (
        cfen["Alias1"]
        .map(clean_text)
    )

    cfen["__txt_Alias2"] = (
        cfen["Alias2"]
        .map(clean_text)
    )

    cfen["__txt_Alias3"] = (
        cfen["Alias3"]
        .map(clean_text)
    )

    cfen["__txt_Alias4"] = (
        cfen["Alias4"]
        .map(clean_text)
    )

    cim["__txt_C_DESCRIPT"] = (
        cim["C_DESCRIPT"]
        .map(clean_text)
    )

    return cfen, cim


def build_client_reference_tables(
    cfen: pd.DataFrame,
    cim: pd.DataFrame,
):
    """
    Build one-row-per-client reference tables.

    Client matching should happen at client grain,
    not document-row grain.
    """

    cfen_ref = (
        cfen[
            cfen["__key_LegalEntityId"] != ""
        ]
        .sort_values("__fen_row_id")
        .drop_duplicates(
            subset=["__key_LegalEntityId"],
            keep="first",
        )
        .copy()
        .reset_index(drop=True)
    )

    cim_ref = (
        cim[
            cim["__key_c1alias"] != ""
        ]
        .sort_values("__im_row_id")
        .drop_duplicates(
            subset=["__key_c1alias"],
            keep="first",
        )
        .copy()
        .reset_index(drop=True)
    )

    return cfen_ref, cim_ref


# ============================================================
# Fuzzy Candidate Builders
# ============================================================

def build_fen_fuzzy_candidate_table(
    cfen_ref: pd.DataFrame,
):
    """
    Stack LegalEntityName and aliases into one candidate table.

    This allows one fuzzy search instead of running TF-IDF five times.
    """

    fuzzy_specs = [
        (
            3,
            "Layer3_LegalEntityName_C_DESCRIPT_fuzzy",
            "__txt_LegalEntityName",
        ),
        (
            4,
            "Layer4_Alias1_C_DESCRIPT_fuzzy",
            "__txt_Alias1",
        ),
        (
            5,
            "Layer5_Alias2_C_DESCRIPT_fuzzy",
            "__txt_Alias2",
        ),
        (
            6,
            "Layer6_Alias3_C_DESCRIPT_fuzzy",
            "__txt_Alias3",
        ),
        (
            7,
            "Layer7_Alias4_C_DESCRIPT_fuzzy",
            "__txt_Alias4",
        ),
    ]

    frames = []

    for layer_no, layer_name, text_col in fuzzy_specs:
        tmp = cfen_ref[
            [
                "__fen_row_id",
                "LegalEntityId",
                text_col,
            ]
        ].copy()

        tmp = tmp.rename(
            columns={
                text_col: "__candidate_text",
            }
        )

        tmp["ClientMatchLayer"] = layer_no
        tmp["ClientMatchedBy"] = layer_name

        tmp = tmp[
            tmp["__candidate_text"] != ""
        ]

        frames.append(tmp)

    if not frames:
        return pd.DataFrame(
            columns=[
                "__fen_row_id",
                "LegalEntityId",
                "__candidate_text",
                "ClientMatchLayer",
                "ClientMatchedBy",
            ]
        )

    return (
        pd.concat(
            frames,
            ignore_index=True
        )
        .drop_duplicates()
        .reset_index(drop=True)
    )


def build_im_fuzzy_candidate_table(
    cim_ref: pd.DataFrame,
):
    """
    Build IM fuzzy candidate table.

    One candidate per IM client using C_DESCRIPT.
    """

    if cim_ref.empty:
        return pd.DataFrame(
            columns=[
                "__im_row_id",
                "c1alias",
                "__candidate_text",
            ]
        )

    candidates = cim_ref[
        [
            "__im_row_id",
            "c1alias",
            "__txt_C_DESCRIPT",
        ]
    ].copy()

    candidates = candidates.rename(
        columns={
            "__txt_C_DESCRIPT": "__candidate_text",
        }
    )

    candidates = candidates[
        candidates["__candidate_text"] != ""
    ]

    return candidates.reset_index(drop=True)


# ============================================================
# One-Pass Fuzzy Matchers
# ============================================================

def fuzzy_match_fen_candidates_to_im(
    fen_candidates: pd.DataFrame,
    cim_ref: pd.DataFrame,
    threshold=85,
    top_k=20,
    min_cosine=0.20,
):
    """
    Fuzzy match FEN names or aliases to IM C_DESCRIPT.
    """

    output_columns = EMPTY_FEN_TO_IM_COLUMNS

    if fen_candidates.empty or cim_ref.empty:
        return pd.DataFrame(
            columns=output_columns
        )

    right_work = cim_ref[
        cim_ref["__txt_C_DESCRIPT"] != ""
    ].copy()

    if right_work.empty:
        return pd.DataFrame(
            columns=output_columns
        )

    left_text = (
        fen_candidates["__candidate_text"]
        .fillna("")
        .astype(str)
    )

    right_text = (
        right_work["__txt_C_DESCRIPT"]
        .fillna("")
        .astype(str)
    )

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 3),
        lowercase=False,
        dtype=np.float32,
        min_df=1,
    )

    vectorizer.fit(
        pd.concat(
            [
                left_text,
                right_text,
            ],
            ignore_index=True,
        )
    )

    left_matrix = vectorizer.transform(
        left_text
    )

    right_matrix = vectorizer.transform(
        right_text
    )

    cosine_matrix = sparse_topn_cosine(
        left_matrix=left_matrix,
        right_matrix=right_matrix,
        top_k=top_k,
        min_cosine=min_cosine,
    ).tocsr()

    records = []

    for left_pos in range(
        cosine_matrix.shape[0]
    ):
        start = cosine_matrix.indptr[
            left_pos
        ]

        end = cosine_matrix.indptr[
            left_pos + 1
        ]

        candidate_positions = (
            cosine_matrix.indices[start:end]
        )

        if len(candidate_positions) == 0:
            continue

        left_value = left_text.iloc[
            left_pos
        ]

        best_score = 0
        best_right_pos = None

        for right_pos in candidate_positions:
            right_value = right_text.iloc[
                right_pos
            ]

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

        left_row = fen_candidates.iloc[
            left_pos
        ]

        right_row = right_work.iloc[
            best_right_pos
        ]

        records.append(
            {
                "__fen_row_id":
                    left_row["__fen_row_id"],

                "__im_row_id":
                    right_row["__im_row_id"],

                "ClientMatchBoolean":
                    1,

                "ClientMatchedBy":
                    left_row["ClientMatchedBy"],

                "ClientMatchLayer":
                    left_row["ClientMatchLayer"],

                "ClientNameScore":
                    best_score,

                "RefClientID":
                    right_row["c1alias"],
            }
        )

    return pd.DataFrame(
        records,
        columns=output_columns
    )


def fuzzy_match_im_candidates_to_fen(
    im_candidates: pd.DataFrame,
    fen_candidates: pd.DataFrame,
    threshold=85,
    top_k=20,
    min_cosine=0.20,
):
    """
    Fuzzy match IM C_DESCRIPT to FEN names and aliases.
    """

    output_columns = EMPTY_IM_TO_FEN_COLUMNS

    if im_candidates.empty or fen_candidates.empty:
        return pd.DataFrame(
            columns=output_columns
        )

    left_text = (
        im_candidates["__candidate_text"]
        .fillna("")
        .astype(str)
    )

    right_text = (
        fen_candidates["__candidate_text"]
        .fillna("")
        .astype(str)
    )

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 3),
        lowercase=False,
        dtype=np.float32,
        min_df=1,
    )

    vectorizer.fit(
        pd.concat(
            [
                left_text,
                right_text,
            ],
            ignore_index=True,
        )
    )

    left_matrix = vectorizer.transform(
        left_text
    )

    right_matrix = vectorizer.transform(
        right_text
    )

    cosine_matrix = sparse_topn_cosine(
        left_matrix=left_matrix,
        right_matrix=right_matrix,
        top_k=top_k,
        min_cosine=min_cosine,
    ).tocsr()

    records = []

    for left_pos in range(
        cosine_matrix.shape[0]
    ):
        start = cosine_matrix.indptr[
            left_pos
        ]

        end = cosine_matrix.indptr[
            left_pos + 1
        ]

        candidate_positions = (
            cosine_matrix.indices[start:end]
        )

        if len(candidate_positions) == 0:
            continue

        left_value = left_text.iloc[
            left_pos
        ]

        best_score = 0
        best_right_pos = None

        for right_pos in candidate_positions:
            right_value = right_text.iloc[
                right_pos
            ]

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

        left_row = im_candidates.iloc[
            left_pos
        ]

        right_row = fen_candidates.iloc[
            best_right_pos
        ]

        records.append(
            {
                "__im_row_id":
                    left_row["__im_row_id"],

                "__fen_row_id":
                    right_row["__fen_row_id"],

                "ClientMatchBoolean":
                    1,

                "ClientMatchedBy":
                    right_row["ClientMatchedBy"].replace(
                        "_C_DESCRIPT_",
                        "_C_DESCRIPT_to_"
                    ),

                "ClientMatchLayer":
                    right_row["ClientMatchLayer"],

                "ClientNameScore":
                    best_score,

                "RefClientID":
                    right_row["LegalEntityId"],
            }
        )

    return pd.DataFrame(
        records,
        columns=output_columns
    )


# ============================================================
# FEN -> IM Client Match
# ============================================================

def client_match_fen_to_im(
    cfen: pd.DataFrame,
    cim: pd.DataFrame,
    threshold=85,
    top_k=20,
    min_cosine=0.20,
):
    """
    FEN client left match to IM client.
    """

    matched_fen_ids = set()
    match_frames = []

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    # Layer 1
    layer1 = cfen_ref.merge(
        cim_ref[
            [
                "__im_row_id",
                "__key_c1alias",
                "c1alias",
            ]
        ],
        left_on="__key_LegalEntityId",
        right_on="__key_c1alias",
        how="inner",
    )

    layer1 = layer1.drop_duplicates(
        subset=["__fen_row_id"],
        keep="first",
    )

    if not layer1.empty:
        tmp = layer1[
            [
                "__fen_row_id",
                "__im_row_id",
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

    print(
        f"Client FEN->IM Layer 1 matched: {len(layer1):,}"
    )

    # Layer 2
    unmatched_fen = cfen_ref[
        ~cfen_ref["__fen_row_id"].isin(
            matched_fen_ids
        )
    ]

    layer2 = unmatched_fen.merge(
        cim_ref[
            [
                "__im_row_id",
                "__key_c1alias",
                "c1alias",
            ]
        ],
        left_on="__key_ReferenceId",
        right_on="__key_c1alias",
        how="inner",
    )

    layer2 = layer2.drop_duplicates(
        subset=["__fen_row_id"],
        keep="first",
    )

    if not layer2.empty:
        tmp = layer2[
            [
                "__fen_row_id",
                "__im_row_id",
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

    print(
        f"Client FEN->IM Layer 2 matched: {len(layer2):,}"
    )

    # Fuzzy layers 3-7
    unmatched_fen_ref = cfen_ref[
        ~cfen_ref["__fen_row_id"].isin(
            matched_fen_ids
        )
    ]

    fen_candidates = build_fen_fuzzy_candidate_table(
        unmatched_fen_ref
    )

    fuzzy_df = fuzzy_match_fen_candidates_to_im(
        fen_candidates=fen_candidates,
        cim_ref=cim_ref,
        threshold=threshold,
        top_k=top_k,
        min_cosine=min_cosine,
    )

    if not fuzzy_df.empty:
        fuzzy_df = (
            fuzzy_df
            .sort_values(
                [
                    "__fen_row_id",
                    "ClientMatchLayer",
                    "ClientNameScore",
                ],
                ascending=[
                    True,
                    True,
                    False,
                ],
            )
            .drop_duplicates(
                subset=["__fen_row_id"],
                keep="first",
            )
            .reset_index(drop=True)
        )

        match_frames.append(
            fuzzy_df
        )

    for layer_no in range(3, 8):
        count = 0

        if not fuzzy_df.empty:
            count = int(
                (
                    fuzzy_df["ClientMatchLayer"]
                    == layer_no
                ).sum()
            )

        print(
            f"Client FEN->IM Layer {layer_no} matched: {count:,}"
        )

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
                    "ClientMatchLayer",
                    "ClientNameScore",
                ],
                ascending=[
                    True,
                    True,
                    False,
                ],
            )
            .drop_duplicates(
                subset=["__fen_row_id"],
                keep="first",
            )
            .reset_index(drop=True)
        )

    else:
        match_df = pd.DataFrame(
            columns=EMPTY_FEN_TO_IM_COLUMNS
        )

    print(
        f"Total FEN->IM client matched: {len(match_df):,}"
    )

    return match_df


# ============================================================
# IM -> FEN Client Match
# ============================================================

def client_match_im_to_fen(
    cfen: pd.DataFrame,
    cim: pd.DataFrame,
    threshold=85,
    top_k=20,
    min_cosine=0.20,
):
    """
    IM client left match to FEN client.
    """

    matched_im_ids = set()
    match_frames = []

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    # Layer 1
    layer1 = cim_ref.merge(
        cfen_ref[
            [
                "__fen_row_id",
                "__key_LegalEntityId",
                "LegalEntityId",
            ]
        ],
        left_on="__key_c1alias",
        right_on="__key_LegalEntityId",
        how="inner",
    )

    layer1 = layer1.drop_duplicates(
        subset=["__im_row_id"],
        keep="first",
    )

    if not layer1.empty:
        tmp = layer1[
            [
                "__im_row_id",
                "__fen_row_id",
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

    print(
        f"Client IM->FEN Layer 1 matched: {len(layer1):,}"
    )

    # Layer 2
    unmatched_im = cim_ref[
        ~cim_ref["__im_row_id"].isin(
            matched_im_ids
        )
    ]

    layer2 = unmatched_im.merge(
        cfen_ref[
            [
                "__fen_row_id",
                "__key_ReferenceId",
                "LegalEntityId",
            ]
        ],
        left_on="__key_c1alias",
        right_on="__key_ReferenceId",
        how="inner",
    )

    layer2 = layer2.drop_duplicates(
        subset=["__im_row_id"],
        keep="first",
    )

    if not layer2.empty:
        tmp = layer2[
            [
                "__im_row_id",
                "__fen_row_id",
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

    print(
        f"Client IM->FEN Layer 2 matched: {len(layer2):,}"
    )

    # Fuzzy layers 3-7
    unmatched_im_ref = cim_ref[
        ~cim_ref["__im_row_id"].isin(
            matched_im_ids
        )
    ]

    im_candidates = build_im_fuzzy_candidate_table(
        unmatched_im_ref
    )

    fen_candidates = build_fen_fuzzy_candidate_table(
        cfen_ref
    )

    fuzzy_df = fuzzy_match_im_candidates_to_fen(
        im_candidates=im_candidates,
        fen_candidates=fen_candidates,
        threshold=threshold,
        top_k=top_k,
        min_cosine=min_cosine,
    )

    if not fuzzy_df.empty:
        fuzzy_df = (
            fuzzy_df
            .sort_values(
                [
                    "__im_row_id",
                    "ClientMatchLayer",
                    "ClientNameScore",
                ],
                ascending=[
                    True,
                    True,
                    False,
                ],
            )
            .drop_duplicates(
                subset=["__im_row_id"],
                keep="first",
            )
            .reset_index(drop=True)
        )

        match_frames.append(
            fuzzy_df
        )

    for layer_no in range(3, 8):
        count = 0

        if not fuzzy_df.empty:
            count = int(
                (
                    fuzzy_df["ClientMatchLayer"]
                    == layer_no
                ).sum()
            )

        print(
            f"Client IM->FEN Layer {layer_no} matched: {count:,}"
        )

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
                    "ClientMatchLayer",
                    "ClientNameScore",
                ],
                ascending=[
                    True,
                    True,
                    False,
                ],
            )
            .drop_duplicates(
                subset=["__im_row_id"],
                keep="first",
            )
            .reset_index(drop=True)
        )

    else:
        match_df = pd.DataFrame(
            columns=EMPTY_IM_TO_FEN_COLUMNS
        )

    print(
        f"Total IM->FEN client matched: {len(match_df):,}"
    )

    return match_df


# ============================================================
# Build Final Result Tables
# ============================================================

def build_fen_to_im_client_result(
    cfen: pd.DataFrame,
    cim: pd.DataFrame,
    match_df: pd.DataFrame,
):
    """
    Build final FEN -> IM result.
    One row per LegalEntityId.
    """

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    result = cfen_ref.merge(
        match_df,
        on="__fen_row_id",
        how="left",
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
        how="left",
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
        "__txt_C_DESCRIPT",
    ]

    result = result.drop(
        columns=[
            col for col in helper_cols
            if col in result.columns
        ],
        errors="ignore",
    )

    return result.reset_index(drop=True)


def build_im_to_fen_client_result(
    cfen: pd.DataFrame,
    cim: pd.DataFrame,
    match_df: pd.DataFrame,
):
    """
    Build final IM -> FEN result.
    One row per c1alias.
    """

    cfen_ref, cim_ref = build_client_reference_tables(
        cfen,
        cim
    )

    result = cim_ref.merge(
        match_df,
        on="__im_row_id",
        how="left",
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
        how="left",
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
        "__txt_Alias4",
    ]

    result = result.drop(
        columns=[
            col for col in helper_cols
            if col in result.columns
        ],
        errors="ignore",
    )

    return result.reset_index(drop=True)