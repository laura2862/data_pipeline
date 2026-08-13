import pandas as pd


def clean_key(value):
    """
    ReferenceId and c1alias are TEXT values.
    Never cast to numeric.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    if value.endswith(".0"):
        value = value[:-2]
    if value in ["", "NAN", "NONE", "NULL", "<NA>"]:
        return ""

    return value


def clean_text(value):

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    if value in ["", "NAN", "NONE", "NULL", "<NA>"]:
        return ""
    return value

from pathlib import Path


def validate_unique_key(df, key_col, df_name):
    """
    Check duplicate keys before merge.
    """

    if key_col not in df.columns:
        raise KeyError(
            f"{df_name} missing key column: {key_col}"
        )

    dup_count = df[key_col].duplicated().sum()

    print(
        f"{df_name}: duplicate {key_col}: {dup_count:,}"
    )

    if dup_count > 0:
        print(
            df[
                df[key_col].duplicated(keep=False)
            ][[key_col]]
            .head(20)
        )


def validate_row_count(before_rows, after_rows, step_name):
    """
    Detect row explosion after merge.
    """

    print(
        f"{step_name}: before={before_rows:,}, after={after_rows:,}"
    )

    if after_rows > before_rows:
        print(
            f"[WARNING] Row count increased in {step_name}. "
            f"Check duplicate merge keys."
        )


def save_debug_csv(df, debug_folder, file_name):
    """
    Save intermediate dataframe for inspection.
    """

    if debug_folder is None:
        return

    debug_folder = Path(debug_folder)
    debug_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = debug_folder / file_name

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"[DEBUG SAVED] {output_path}"
    )


def validate_match_map(match_df, left_key, right_key, match_name):
    """
    Validate match_df before merging back to original tables.
    """

    print(f"\nValidating match map: {match_name}")

    print(f"Rows: {len(match_df):,}")

    if match_df.empty:
        return

    left_dup = match_df[left_key].duplicated().sum()
    right_dup = match_df[right_key].duplicated().sum()

    print(f"Duplicate {left_key}: {left_dup:,}")
    print(f"Duplicate {right_key}: {right_dup:,}")

    if left_dup > 0:
        print(
            match_df[
                match_df[left_key].duplicated(keep=False)
            ]
            .sort_values(left_key)
            .head(20)
        )

def prepare_document_match_data(
    fen_client_doc,
    im_client_doc
):
    """
    Prepare document-level matching data.

    IMPORTANT:
    ReferenceId and c1alias are TEXT.
    """

    fen_cols = [
        "LegalEntityId",
        "LegalEntityName",
        "ReferenceId",
        "DocumentName",
        "iManage_Doc_Num"
    ]

    im_cols = [
        "c1alias",
        "C_DESCRIPT",
        "docname",
        "docnum"
    ]

    # -----------------------------
    # Validate columns
    # -----------------------------

    missing_fen = [
        c for c in fen_cols
        if c not in fen_client_doc.columns
    ]

    missing_im = [
        c for c in im_cols
        if c not in im_client_doc.columns
    ]

    if missing_fen:
        raise KeyError(
            f"Missing Fen columns: {missing_fen}"
        )

    if missing_im:
        raise KeyError(
            f"Missing IM columns: {missing_im}"
        )

    # -----------------------------
    # Copy working columns
    # -----------------------------

    fen = fen_client_doc.copy()
    im = im_client_doc.copy()

    fen = fen.reset_index(drop=True)
    im = im.reset_index(drop=True)

    fen["__fen_row_id"] = fen.index
    im["__im_row_id"] = im.index

    # -----------------------------
    # Exact match keys
    # -----------------------------

    fen["__key_iManage_Doc_Num"] = (
        fen["iManage_Doc_Num"]
        .apply(clean_key)
    )

    fen["__key_LegalEntityId"] = (
        fen["LegalEntityId"]
        .apply(clean_key)
    )

    fen["__key_ReferenceId"] = (
        fen["ReferenceId"]
        .apply(clean_key)
    )

    im["__key_docnum"] = (
        im["docnum"]
        .apply(clean_key)
    )

    im["__key_c1alias"] = (
        im["c1alias"]
        .apply(clean_key)
    )

    # -----------------------------
    # Text comparison
    # -----------------------------

    fen["__txt_DocumentName"] = (
        fen["DocumentName"]
        .apply(clean_text)
    )

    fen["__txt_LegalEntityName"] = (
        fen["LegalEntityName"]
        .apply(clean_text)
    )

    im["__txt_docname"] = (
        im["docname"]
        .apply(clean_text)
    )

    im["__txt_C_DESCRIPT"] = (
        im["C_DESCRIPT"]
        .apply(clean_text)
    )

    return fen, im


def document_exact_match_fen_to_im(fen, im):
    """
    Document-level exact matching by 4 ordered layers.

    Layer 1:
        iManage_Doc_Num = docnum

    Layer 2:
        LegalEntityId = c1alias
        AND DocumentName = docname

    Layer 3:
        ReferenceId = c1alias
        AND DocumentName = docname

    Layer 4:
        LegalEntityName = C_DESCRIPT
        AND DocumentName = docname

    Earlier layers win.
    """

    matched_fen_ids = set()
    match_frames = []

    # --------------------------------------------------
    # Layer 1: iManage_Doc_Num = docnum
    # --------------------------------------------------
    layer1 = fen[
        fen["__key_iManage_Doc_Num"] != ""
    ].merge(
        im[
            im["__key_docnum"] != ""
        ][["__im_row_id", "__key_docnum"]],
        left_on="__key_iManage_Doc_Num",
        right_on="__key_docnum",
        how="inner"
    )

    layer1 = layer1.drop_duplicates(
        subset=["__fen_row_id"],
        keep="first"
    )

    if not layer1.empty:
        layer1_match = layer1[["__fen_row_id", "__im_row_id"]].copy()
        layer1_match["DocMatchBoolean"] = 1
        layer1_match["DocMatchedBy"] = "Layer 1: iManage_Doc_Num = docnum"
        layer1_match["DocMatchLayer"] = 1

        match_frames.append(layer1_match)
        matched_fen_ids.update(layer1_match["__fen_row_id"].tolist())

    print(f"Layer 1 matched: {len(layer1):,}")

    # --------------------------------------------------
    # Layer 2: LegalEntityId = c1alias AND DocumentName = docname
    # --------------------------------------------------
    unmatched_fen = fen[
        ~fen["__fen_row_id"].isin(matched_fen_ids)
    ]

    layer2 = unmatched_fen[
        (unmatched_fen["__key_LegalEntityId"] != "")
        &
        (unmatched_fen["__txt_DocumentName"] != "")
    ].merge(
        im[
            (im["__key_c1alias"] != "")
            &
            (im["__txt_docname"] != "")
        ][["__im_row_id", "__key_c1alias", "__txt_docname"]],
        left_on=["__key_LegalEntityId", "__txt_DocumentName"],
        right_on=["__key_c1alias", "__txt_docname"],
        how="inner"
    )

    layer2 = layer2.drop_duplicates(
        subset=["__fen_row_id"],
        keep="first"
    )

    if not layer2.empty:
        layer2_match = layer2[["__fen_row_id", "__im_row_id"]].copy()
        layer2_match["DocMatchBoolean"] = 1
        layer2_match["DocMatchedBy"] = "Layer 2: LegalEntityId = c1alias AND DocumentName = docname"
        layer2_match["DocMatchLayer"] = 2

        match_frames.append(layer2_match)
        matched_fen_ids.update(layer2_match["__fen_row_id"].tolist())

    print(f"Layer 2 matched: {len(layer2):,}")

    # --------------------------------------------------
    # Layer 3: ReferenceId = c1alias AND DocumentName = docname
    # ReferenceId is text
    # --------------------------------------------------
    unmatched_fen = fen[
        ~fen["__fen_row_id"].isin(matched_fen_ids)
    ]

    layer3 = unmatched_fen[
        (unmatched_fen["__key_ReferenceId"] != "")
        &
        (unmatched_fen["__txt_DocumentName"] != "")
    ].merge(
        im[
            (im["__key_c1alias"] != "")
            &
            (im["__txt_docname"] != "")
        ][["__im_row_id", "__key_c1alias", "__txt_docname"]],
        left_on=["__key_ReferenceId", "__txt_DocumentName"],
        right_on=["__key_c1alias", "__txt_docname"],
        how="inner"
    )

    layer3 = layer3.drop_duplicates(
        subset=["__fen_row_id"],
        keep="first"
    )

    if not layer3.empty:
        layer3_match = layer3[["__fen_row_id", "__im_row_id"]].copy()
        layer3_match["DocMatchBoolean"] = 1
        layer3_match["DocMatchedBy"] = "Layer 3: ReferenceId = c1alias AND DocumentName = docname"
        layer3_match["DocMatchLayer"] = 3

        match_frames.append(layer3_match)
        matched_fen_ids.update(layer3_match["__fen_row_id"].tolist())

    print(f"Layer 3 matched: {len(layer3):,}")

    # --------------------------------------------------
    # Layer 4: LegalEntityName = C_DESCRIPT AND DocumentName = docname
    # --------------------------------------------------
    unmatched_fen = fen[
        ~fen["__fen_row_id"].isin(matched_fen_ids)
    ]

    layer4 = unmatched_fen[
        (unmatched_fen["__txt_LegalEntityName"] != "")
        &
        (unmatched_fen["__txt_DocumentName"] != "")
    ].merge(
        im[
            (im["__txt_C_DESCRIPT"] != "")
            &
            (im["__txt_docname"] != "")
        ][["__im_row_id", "__txt_C_DESCRIPT", "__txt_docname"]],
        left_on=["__txt_LegalEntityName", "__txt_DocumentName"],
        right_on=["__txt_C_DESCRIPT", "__txt_docname"],
        how="inner"
    )

    layer4 = layer4.drop_duplicates(
        subset=["__fen_row_id"],
        keep="first"
    )

    if not layer4.empty:
        layer4_match = layer4[["__fen_row_id", "__im_row_id"]].copy()
        layer4_match["DocMatchBoolean"] = 1
        layer4_match["DocMatchedBy"] = "Layer 4: LegalEntityName = C_DESCRIPT AND DocumentName = docname"
        layer4_match["DocMatchLayer"] = 4

        match_frames.append(layer4_match)
        matched_fen_ids.update(layer4_match["__fen_row_id"].tolist())

    print(f"Layer 4 matched: {len(layer4):,}")

    # --------------------------------------------------
    # Combine match map
    # --------------------------------------------------
    if match_frames:
        match_df = pd.concat(match_frames, ignore_index=True)
    else:
        match_df = pd.DataFrame(
            columns=[
                "__fen_row_id",
                "__im_row_id",
                "DocMatchBoolean",
                "DocMatchedBy",
                "DocMatchLayer"
            ]
        )

    match_df = (
        match_df
        .sort_values(["__fen_row_id", "DocMatchLayer"])
        .drop_duplicates(subset=["__fen_row_id"], keep="first")
        .reset_index(drop=True)
    )

    return match_df



def document_exact_match_im_to_fen(fen, im):

    matched_im_ids = set()
    match_frames = []

    # ==================================================
    # Layer 1
    # docnum = iManage_Doc_Num
    # IMPORTANT: exclude blank keys
    # ==================================================

    layer1 = im[
        im["__key_docnum"] != ""
    ].merge(
        fen[
            fen["__key_iManage_Doc_Num"] != ""
        ][
            [
                "__fen_row_id",
                "__key_iManage_Doc_Num"
            ]
        ],
        left_on="__key_docnum",
        right_on="__key_iManage_Doc_Num",
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

        tmp["DocMatchBoolean"] = 1
        tmp["DocMatchedBy"] = "Layer1_docnum_iManageDocNum"
        tmp["DocMatchLayer"] = 1

        match_frames.append(tmp)

        matched_im_ids.update(
            tmp["__im_row_id"].tolist()
        )

    print(f"Layer 1 matched: {len(layer1):,}")

    # ==================================================
    # Layer 2
    # c1alias = LegalEntityId
    # docname = DocumentName
    # ==================================================

    unmatched_im = im[
        ~im["__im_row_id"].isin(matched_im_ids)
    ]

    layer2 = unmatched_im[
        (unmatched_im["__key_c1alias"] != "")
        &
        (unmatched_im["__txt_docname"] != "")
    ].merge(
        fen[
            (fen["__key_LegalEntityId"] != "")
            &
            (fen["__txt_DocumentName"] != "")
        ][
            [
                "__fen_row_id",
                "__key_LegalEntityId",
                "__txt_DocumentName"
            ]
        ],
        left_on=[
            "__key_c1alias",
            "__txt_docname"
        ],
        right_on=[
            "__key_LegalEntityId",
            "__txt_DocumentName"
        ],
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

        tmp["DocMatchBoolean"] = 1
        tmp["DocMatchedBy"] = "Layer2_c1alias_LegalEntityId_AND_docname_DocumentName"
        tmp["DocMatchLayer"] = 2

        match_frames.append(tmp)

        matched_im_ids.update(
            tmp["__im_row_id"].tolist()
        )

    print(f"Layer 2 matched: {len(layer2):,}")

    # ==================================================
    # Layer 3
    # c1alias = ReferenceId
    # docname = DocumentName
    # ==================================================

    unmatched_im = im[
        ~im["__im_row_id"].isin(matched_im_ids)
    ]

    layer3 = unmatched_im[
        (unmatched_im["__key_c1alias"] != "")
        &
        (unmatched_im["__txt_docname"] != "")
    ].merge(
        fen[
            (fen["__key_ReferenceId"] != "")
            &
            (fen["__txt_DocumentName"] != "")
        ][
            [
                "__fen_row_id",
                "__key_ReferenceId",
                "__txt_DocumentName"
            ]
        ],
        left_on=[
            "__key_c1alias",
            "__txt_docname"
        ],
        right_on=[
            "__key_ReferenceId",
            "__txt_DocumentName"
        ],
        how="inner"
    )

    layer3 = layer3.drop_duplicates(
        subset=["__im_row_id"],
        keep="first"
    )

    if not layer3.empty:

        tmp = layer3[
            [
                "__im_row_id",
                "__fen_row_id"
            ]
        ].copy()

        tmp["DocMatchBoolean"] = 1
        tmp["DocMatchedBy"] = "Layer3_c1alias_ReferenceId_AND_docname_DocumentName"
        tmp["DocMatchLayer"] = 3

        match_frames.append(tmp)

        matched_im_ids.update(
            tmp["__im_row_id"].tolist()
        )

    print(f"Layer 3 matched: {len(layer3):,}")

    # ==================================================
    # Layer 4
    # C_DESCRIPT = LegalEntityName
    # docname = DocumentName
    # ==================================================

    unmatched_im = im[
        ~im["__im_row_id"].isin(matched_im_ids)
    ]

    layer4 = unmatched_im[
        (unmatched_im["__txt_C_DESCRIPT"] != "")
        &
        (unmatched_im["__txt_docname"] != "")
    ].merge(
        fen[
            (fen["__txt_LegalEntityName"] != "")
            &
            (fen["__txt_DocumentName"] != "")
        ][
            [
                "__fen_row_id",
                "__txt_LegalEntityName",
                "__txt_DocumentName"
            ]
        ],
        left_on=[
            "__txt_C_DESCRIPT",
            "__txt_docname"
        ],
        right_on=[
            "__txt_LegalEntityName",
            "__txt_DocumentName"
        ],
        how="inner"
    )

    layer4 = layer4.drop_duplicates(
        subset=["__im_row_id"],
        keep="first"
    )

    if not layer4.empty:

        tmp = layer4[
            [
                "__im_row_id",
                "__fen_row_id"
            ]
        ].copy()

        tmp["DocMatchBoolean"] = 1
        tmp["DocMatchedBy"] = "Layer4_C_DESCRIPT_LegalEntityName_AND_docname_DocumentName"
        tmp["DocMatchLayer"] = 4

        match_frames.append(tmp)

        matched_im_ids.update(
            tmp["__im_row_id"].tolist()
        )

    print(f"Layer 4 matched: {len(layer4):,}")

    # ==================================================
    # Final match map
    # ==================================================

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
                    "DocMatchLayer"
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
                "DocMatchBoolean",
                "DocMatchedBy",
                "DocMatchLayer"
            ]
        )

    return match_df

def build_doc_fen_to_im_result(
    fen,
    im,
    match_df,
    debug_folder=None
):
    """
    Build final Fen -> IM document result.

    Saves middle results before/after merging when debug_folder is provided.
    """

    validate_match_map(
        match_df=match_df,
        left_key="__fen_row_id",
        right_key="__im_row_id",
        match_name="doc_fen_to_im_match_df"
    )

    save_debug_csv(
        match_df,
        debug_folder,
        "debug_01_doc_fen_to_im_match_df.csv"
    )

    # --------------------------------------------------
    # Attach match info to Fen
    # --------------------------------------------------

    before_rows = len(fen)

    result = fen.merge(
        match_df,
        on="__fen_row_id",
        how="left",
        validate="one_to_one"
    )

    validate_row_count(
        before_rows,
        len(result),
        "Fen merge with match_df"
    )

    save_debug_csv(
        result,
        debug_folder,
        "debug_02_fen_after_match_merge.csv"
    )

    # --------------------------------------------------
    # Prefix IM columns
    # --------------------------------------------------

    im_prefixed = im.copy()

    im_prefixed.columns = [
        col
        if col.startswith("__")
        else f"im_{col}"
        for col in im_prefixed.columns
    ]

    save_debug_csv(
        im_prefixed,
        debug_folder,
        "debug_03_im_prefixed_before_merge.csv"
    )

    # --------------------------------------------------
    # Attach matched IM row
    # --------------------------------------------------

    before_rows = len(result)

    result = result.merge(
        im_prefixed,
        on="__im_row_id",
        how="left",
        validate="many_to_one"
    )

    validate_row_count(
        before_rows,
        len(result),
        "Fen result merge with im_prefixed"
    )

    save_debug_csv(
        result,
        debug_folder,
        "debug_04_doc_fen_to_im_after_im_merge.csv"
    )

    # --------------------------------------------------
    # Match defaults
    # --------------------------------------------------

    result["DocMatchBoolean"] = (
        result["DocMatchBoolean"]
        .fillna(0)
        .astype(int)
    )

    result["DocMatchedBy"] = (
        result["DocMatchedBy"]
        .fillna("No Match")
    )

    result["DocMatchLayer"] = (
        result["DocMatchLayer"]
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------
    # Remove helper columns
    # --------------------------------------------------

    drop_cols = [
        "__fen_row_id",
        "__im_row_id",
        "__key_docnum",
        "__key_c1alias",
        "__txt_docname",
        "__txt_C_DESCRIPT",
        "__key_iManage_Doc_Num",
        "__key_LegalEntityId",
        "__key_ReferenceId",
        "__txt_DocumentName",
        "__txt_LegalEntityName"
    ]

    result = result.drop(
        columns=[
            c for c in drop_cols
            if c in result.columns
        ],
        errors="ignore"
    )

    save_debug_csv(
        result,
        debug_folder,
        "debug_05_doc_fen_to_im_final_clean.csv"
    )

    return result.reset_index(drop=True)

def build_doc_im_to_fen_result(
    fen,
    im,
    match_df,
    debug_folder=None
):
    """
    Build final IM -> Fen document result.

    Saves middle results before/after merging when debug_folder is provided.
    """

    validate_match_map(
        match_df=match_df,
        left_key="__im_row_id",
        right_key="__fen_row_id",
        match_name="doc_im_to_fen_match_df"
    )

    save_debug_csv(
        match_df,
        debug_folder,
        "debug_01_doc_im_to_fen_match_df.csv"
    )

    before_rows = len(im)

    result = im.merge(
        match_df,
        on="__im_row_id",
        how="left",
        validate="one_to_one"
    )

    validate_row_count(
        before_rows,
        len(result),
        "IM merge with match_df"
    )

    save_debug_csv(
        result,
        debug_folder,
        "debug_02_im_after_match_merge.csv"
    )

    fen_prefixed = fen.copy()

    fen_prefixed.columns = [
        col
        if col.startswith("__")
        else f"fen_{col}"
        for col in fen_prefixed.columns
    ]

    save_debug_csv(
        fen_prefixed,
        debug_folder,
        "debug_03_fen_prefixed_before_merge.csv"
    )

    before_rows = len(result)

    result = result.merge(
        fen_prefixed,
        on="__fen_row_id",
        how="left",
        validate="many_to_one"
    )

    validate_row_count(
        before_rows,
        len(result),
        "IM result merge with fen_prefixed"
    )

    save_debug_csv(
        result,
        debug_folder,
        "debug_04_doc_im_to_fen_after_fen_merge.csv"
    )

    result["DocMatchBoolean"] = (
        result["DocMatchBoolean"]
        .fillna(0)
        .astype(int)
    )

    result["DocMatchedBy"] = (
        result["DocMatchedBy"]
        .fillna("No Match")
    )

    result["DocMatchLayer"] = (
        result["DocMatchLayer"]
        .fillna(0)
        .astype(int)
    )

    drop_cols = [
        "__im_row_id",
        "__fen_row_id",
        "__key_docnum",
        "__key_c1alias",
        "__txt_docname",
        "__txt_C_DESCRIPT",
        "__key_iManage_Doc_Num",
        "__key_LegalEntityId",
        "__key_ReferenceId",
        "__txt_DocumentName",
        "__txt_LegalEntityName"
    ]

    result = result.drop(
        columns=[
            c for c in drop_cols
            if c in result.columns
        ],
        errors="ignore"
    )

    save_debug_csv(
        result,
        debug_folder,
        "debug_05_doc_im_to_fen_final_clean.csv"
    )

    return result.reset_index(drop=True)


if __name__ == "__main__":

    print("Testing document_match.py")

    fen_test = pd.DataFrame(
        {
            "LegalEntityId": [
                "1001",
                "1002",
                "ABC-REF"
            ],
            "LegalEntityName": [
                "ABC CORP",
                "XYZ CORP",
                "TEST CLIENT"
            ],
            "ReferenceId": [
                "REF001",
                "REF002",
                "REF003"
            ],
            "DocumentName": [
                "KYC FORM",
                "AML FORM",
                "RISK FORM"
            ],
            "iManage_Doc_Num": [
                "101",
                "102",
                "103"
            ]
        }
    )

    im_test = pd.DataFrame(
        {
            "c1alias": [
                "1001",
                "REF002",
                "CLIENTX"
            ],
            "C_DESCRIPT": [
                "ABC CORP",
                "XYZ CORP",
                "TEST CLIENT"
            ],
            "docname": [
                "OTHER",
                "AML FORM",
                "RISK FORM"
            ],
            "docnum": [
                "101",
                "999",
                "888"
            ]
        }
    )

    fen, im = prepare_document_match_data(
        fen_test,
        im_test
    )

    print("\n--- Fen -> IM ---")

    match1 = document_exact_match_fen_to_im(
        fen,
        im
    )

    print(match1)

    print("\n--- IM -> Fen ---")

    match2 = document_exact_match_im_to_fen(
        fen,
        im
    )

    print(match2)

    print("\nDocument Match Unit Test Complete")