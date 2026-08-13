# analysis/e2x_compare_extracts.py

import re
import sys
from pathlib import Path

import pandas as pd
from _01_config.settings import OUTPUT_IN_SCOPE
from _01_config.settings import VENDOR_FOLDER
from _01_config.settings import VALIDATION_FOLDER


# ============================================================
# Normalization Helpers
# ============================================================

def normalize_property_id(value):
    """
    Normalize E2X prefixed property ids.

    Examples:
        LEASSOC12345 -> 12345
        LEADDR999    -> 999
        LETAX123     -> 123
        12345        -> 12345
        12345.0      -> 12345
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    value = re.sub(
        r"\.0$",
        "",
        value
    )

    value = re.sub(
        r"^[A-Z_]+",
        "",
        value
    )

    return value.strip()

def clean_key_series(series):
    """
    Normalize IDs for comparison:
    - convert to string
    - strip spaces
    - remove trailing .0
    - blank/null becomes empty string
    """

    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(
            r"\.0$",
            "",
            regex=True
        )
    )
# ============================================================
# Extract Mapping Configuration
# ============================================================
# BNS files are in TEMP_FOLDER.
# E2X files are in VENDOR_FOLDER.
#
# Client/legal entity:
#     Match on LegalEntityId only.
#
# Property extracts:
#     Match on LegalEntityId + PropertyId.
#
# Association special rule:
#     E2X AlternateId has prefix LEASSOC.
#     Example: LEASSOC12345
#     It is normalized to 12345 before comparison.
# ============================================================

EXTRACT_CONFIG = {
    "client": {
        "bns_file": "in_scope_fen_client_detail.csv",
        "e2x_file": "LeInScope.csv",

        "bns_entity_col": "LegalEntityId",
        "e2x_entity_col": "LegalEntityId",

        "bns_property_col": None,
        "e2x_property_col": None,

        "normalize_bns_property": False,
        "normalize_e2x_property": False,
    },

    "document": {
        "bns_file": "in_scope_fen_doc.csv",
        "e2x_file": "Documents.csv",

        "bns_entity_col": "LegalEntityId",
        "e2x_entity_col": "LegalEntityId",

        "bns_property_col": "DocumentId",
        "e2x_property_col": "DocumentId",

        "normalize_bns_property": False,
        "normalize_e2x_property": False,
    },

    "product": {
        "bns_file": "in_scope_fen_product.csv",
        "e2x_file": "Products.csv",

        "bns_entity_col": "LegalEntityId",
        "e2x_entity_col": "LegalEntityId",

        "bns_property_col": "ProductId",
        "e2x_property_col": "ProductId",

        "normalize_bns_property": False,
        "normalize_e2x_property": False,
    },

    "comment": {
        "bns_file": "in_scope_fen_comment.csv",
        "e2x_file": "Comments.csv",

        "bns_entity_col": "LegalEntityId",
        "e2x_entity_col": "LegalEntityId",

        "bns_property_col": "CommentId",
        "e2x_property_col": "CommentId",

        "normalize_bns_property": False,
        "normalize_e2x_property": False,
    },

    "contact": {
        "bns_file": "in_scope_fen_contact.csv",
        "e2x_file": "Contacts.csv",

        "bns_entity_col": "LegalEntityId",
        "e2x_entity_col": "LegalEntityId",

        "bns_property_col": "ContactId",
        "e2x_property_col": "ContactId",

        "normalize_bns_property": False,
        "normalize_e2x_property": False,
    },

    "association": {
        "bns_file": "in_scope_fen_association.csv",
        "e2x_file": "Associations.csv",

        "bns_entity_col": "LegalEntityId",
        "e2x_entity_col": "LegalEntityId",

        "bns_property_col": "AssociatedRelationId",

        # E2X uses CONCAT('LEASSOC', leas.Id) AS AlternateId
        # Example: LEASSOC12345
        "e2x_property_col": "AlternateId",

        "normalize_bns_property": False,
        "normalize_e2x_property": True,
    },

    "address": {
        "bns_file": "in_scope_fen_address.csv",
        "e2x_file": "Addresses.csv",

        "bns_entity_col": "LegalEntityId",
        "e2x_entity_col": "LegalEntityId",

        "bns_property_col": "AddressId",
        "e2x_property_col": "AddressId",

        "normalize_bns_property": False,
        "normalize_e2x_property": False,
    },

    "taxid": {
        "bns_file": "in_scope_fen_taxid.csv",
        "e2x_file": "TaxIdentifiers.csv",

        "bns_entity_col": "LegalEntityId",
        "e2x_entity_col": "LegalEntityId",

        "bns_property_col": "TaxIdentiferId",
        "e2x_property_col": "TaxIdentiferId",

        "normalize_bns_property": False,
        "normalize_e2x_property": False,
    },
}


# ============================================================
# CSV Helpers
# ============================================================

def read_csv_if_exists(path):
    """
    Read CSV safely.
    Return None if missing.
    """

    path = Path(path)

    if not path.exists():
        return None

    return pd.read_csv(
        path,
        low_memory=False,
        dtype=str
    )


def resolve_column(
    df,
    preferred_col,
    fallback_candidates
):
    """
    Resolve a column name safely.

    First use preferred_col if found.
    Otherwise search fallback candidates case-insensitively.
    """

    if df is None:
        return None

    if preferred_col and preferred_col in df.columns:
        return preferred_col

    lower_to_actual = {
        c.lower(): c
        for c in df.columns
    }

    for candidate in fallback_candidates:

        if candidate and candidate.lower() in lower_to_actual:
            return lower_to_actual[candidate.lower()]

    return None


def prepare_key_df(
    df,
    entity_col,
    property_col,
    source_name,
    normalize_property=False
):
    """
    Build distinct business key dataframe.

    Client:
        LegalEntityId

    Property extracts:
        LegalEntityId + PropertyId
    """

    if df is None:
        return pd.DataFrame()

    if entity_col not in df.columns:
        raise KeyError(
            f"{source_name}: missing entity column: {entity_col}. "
            f"Available columns: {df.columns.tolist()}"
        )

    work = pd.DataFrame()

    work["LegalEntityId"] = clean_key_series(
        df[entity_col]
    )

    if property_col is None:

        work["PropertyId"] = ""
        work["CompareKey"] = work["LegalEntityId"]

    else:

        if property_col not in df.columns:
            raise KeyError(
                f"{source_name}: missing property column: {property_col}. "
                f"Available columns: {df.columns.tolist()}"
            )

        if normalize_property:

            work["PropertyId"] = (
                df[property_col]
                .apply(normalize_property_id)
            )

        else:

            work["PropertyId"] = clean_key_series(
                df[property_col]
            )

        work["CompareKey"] = (
            work["LegalEntityId"]
            + "|"
            + work["PropertyId"]
        )

    # Remove blank LegalEntityId
    work = work[
        work["LegalEntityId"] != ""
    ].copy()

    # For property extracts, remove blank property ids
    if property_col is not None:

        work = work[
            work["PropertyId"] != ""
        ].copy()

    # Keep distinct business keys only
    work = (
        work
        .drop_duplicates(
            subset=[
                "LegalEntityId",
                "PropertyId"
            ]
        )
        .reset_index(drop=True)
    )

    return work

def get_key_count(
    df,
    property_col
):
    """
    Count distinct business keys.
    """

    if property_col is None:

        return (
            df[
                ["LegalEntityId"]
            ]
            .drop_duplicates()
            .shape[0]
        )

    return (
        df[
            [
                "LegalEntityId",
                "PropertyId"
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )


def print_file_debug(
    extract_name,
    source_name,
    path,
    df,
    entity_col
):
    """
    Print file path, row count, columns, first rows, and distinct entity count.
    This helps confirm whether the script is reading the expected file.
    """

    print("\n" + "-" * 100)
    print(f"{extract_name} - {source_name} FILE DEBUG")
    print("-" * 100)

    print("Path:", path)

    if df is None:
        print("File not found")
        return

    print("Raw rows:", len(df))
    print("Columns:", df.columns.tolist())

    if entity_col in df.columns:

        distinct_entity_count = (
            clean_key_series(
                df[entity_col]
            )
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

        print(
            f"Distinct {entity_col}: {distinct_entity_count}"
        )

    else:

        print(
            f"Entity column not found in file: {entity_col}"
        )

    print("\nFirst 10 rows:")
    print(
        df.head(10)
        .to_string(index=False)
    )

def check_sum():
    """
    Validate total counts for each extract based on distinct business keys.

    Client:
        LegalEntityId

    Property extracts:
        LegalEntityId + PropertyId

    Saves:
        VALIDATION_FOLDER / e2x_checksum.csv
    """

    checksum_rows = []

    print("\n" + "=" * 100)
    print("E2X CHECKSUM BY DISTINCT BUSINESS KEYS")
    print("=" * 100)

    for extract_name, config in EXTRACT_CONFIG.items():

        print("\n" + "=" * 100)
        print(f"CHECKSUM: {extract_name}")
        print("=" * 100)

        bns_path = (
            OUTPUT_IN_SCOPE /
            config["bns_file"]
        )

        e2x_path = (
            VENDOR_FOLDER /
            config["e2x_file"]
        )

        bns_df = read_csv_if_exists(
            bns_path
        )

        e2x_df = read_csv_if_exists(
            e2x_path
        )

        print_file_debug(
            extract_name=extract_name,
            source_name="BNS",
            path=bns_path,
            df=bns_df,
            entity_col=config["bns_entity_col"]
        )

        print_file_debug(
            extract_name=extract_name,
            source_name="E2X",
            path=e2x_path,
            df=e2x_df,
            entity_col=config["e2x_entity_col"]
        )

        if bns_df is None or e2x_df is None:

            checksum_rows.append(
                {
                    "ExtractName": extract_name,
                    "BNSFile": str(bns_path),
                    "E2XFile": str(e2x_path),
                    "BNSRawRows": len(bns_df) if bns_df is not None else "",
                    "E2XRawRows": len(e2x_df) if e2x_df is not None else "",
                    "BNSKeyCount": "",
                    "E2XKeyCount": "",
                    "Difference": "",
                    "Status": "MISSING_FILE"
                }
            )

            continue

        bns_keys = prepare_key_df(
            df=bns_df,
            entity_col=config["bns_entity_col"],
            property_col=config["bns_property_col"],
            source_name="BNS",
            normalize_property=config.get(
                "normalize_bns_property",
                False
            )
        )

        e2x_keys = prepare_key_df(
            df=e2x_df,
            entity_col=config["e2x_entity_col"],
            property_col=config["e2x_property_col"],
            source_name="E2X",
            normalize_property=config.get(
                "normalize_e2x_property",
                False
            )
        )

        bns_key_count = get_key_count(
            bns_keys,
            config["bns_property_col"]
        )

        e2x_key_count = get_key_count(
            e2x_keys,
            config["e2x_property_col"]
        )

        difference = (
            bns_key_count
            -
            e2x_key_count
        )

        status = (
            "PASS"
            if difference == 0
            else "FAIL"
        )

        checksum_rows.append(
            {
                "ExtractName": extract_name,
                "BNSFile": str(bns_path),
                "E2XFile": str(e2x_path),
                "BNSRawRows": len(bns_df),
                "E2XRawRows": len(e2x_df),
                "BNSKeyCount": bns_key_count,
                "E2XKeyCount": e2x_key_count,
                "Difference": difference,
                "Status": status
            }
        )

        print("\nDistinct Business Key Result:")
        print("BNSKeyCount:", bns_key_count)
        print("E2XKeyCount:", e2x_key_count)
        print("Difference :", difference)
        print("Status     :", status)

        print("\nE2X Prepared Key Sample:")
        print(
            e2x_keys[
                [
                    "LegalEntityId",
                    "PropertyId",
                    "CompareKey"
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

    checksum_df = pd.DataFrame(
        checksum_rows
    )

    checksum_file = (
        VALIDATION_FOLDER /
        "e2x_checksum.csv"
    )

    checksum_df.to_csv(
        checksum_file,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 100)
    print("E2X CHECKSUM SUMMARY")
    print("=" * 100)

    print(
        checksum_df.to_string(
            index=False
        )
    )

    print(
        f"\nSaved checksum file:\n{checksum_file}"
    )

    return checksum_df

def check_extract(
    extract_name,
    config
):
    """
    Compare one extract by distinct business keys.

    Saves:
        VALIDATION_FOLDER / e2x_<extract_name>.csv
    """

    print("\n" + "=" * 100)
    print(f"DETAIL MAPPING: {extract_name}")
    print("=" * 100)

    bns_path = (
        OUTPUT_IN_SCOPE /
        config["bns_file"]
    )

    e2x_path = (
        VENDOR_FOLDER /
        config["e2x_file"]
    )

    bns_df = read_csv_if_exists(
        bns_path
    )

    e2x_df = read_csv_if_exists(
        e2x_path
    )

    if bns_df is None or e2x_df is None:

        return {
            "ExtractName": extract_name,
            "BNSKeyCount": "",
            "E2XKeyCount": "",
            "Mapped": "",
            "OnlyInBNS": "",
            "OnlyInE2X": "",
            "Status": "MISSING_FILE"
        }

    bns_keys = prepare_key_df(
        df=bns_df,
        entity_col=config["bns_entity_col"],
        property_col=config["bns_property_col"],
        source_name="BNS",
        normalize_property=config.get(
            "normalize_bns_property",
            False
        )
    )

    e2x_keys = prepare_key_df(
        df=e2x_df,
        entity_col=config["e2x_entity_col"],
        property_col=config["e2x_property_col"],
        source_name="E2X",
        normalize_property=config.get(
            "normalize_e2x_property",
            False
        )
    )

    bns_keys = bns_keys.rename(
        columns={
            "LegalEntityId": "BNSLegalEntityId",
            "PropertyId": "BNSPropertyId"
        }
    )

    e2x_keys = e2x_keys.rename(
        columns={
            "LegalEntityId": "E2XLegalEntityId",
            "PropertyId": "E2XPropertyId"
        }
    )

    merged = bns_keys.merge(
        e2x_keys,
        on="CompareKey",
        how="outer",
        indicator=True
    )

    merged["MappedStatus"] = (
        merged["_merge"]
        .map(
            {
                "both": "Mapped",
                "left_only": "Only_In_BNS_Result",
                "right_only": "Only_In_E2X_Result"
            }
        )
    )

    merged["ExtractName"] = extract_name

    merged = merged[
        [
            "ExtractName",
            "CompareKey",
            "BNSLegalEntityId",
            "BNSPropertyId",
            "E2XLegalEntityId",
            "E2XPropertyId",
            "MappedStatus"
        ]
    ]

    detail_file = (
        VALIDATION_FOLDER /
        f"e2x_{extract_name}.csv"
    )

    merged.to_csv(
        detail_file,
        index=False,
        encoding="utf-8-sig"
    )

    mapped = (
        merged[
            merged["MappedStatus"]
            ==
            "Mapped"
        ]
        ["CompareKey"]
        .drop_duplicates()
        .shape[0]
    )

    only_bns = (
        merged[
            merged["MappedStatus"]
            ==
            "Only_In_BNS_Result"
        ]
        ["CompareKey"]
        .drop_duplicates()
        .shape[0]
    )

    only_e2x = (
        merged[
            merged["MappedStatus"]
            ==
            "Only_In_E2X_Result"
        ]
        ["CompareKey"]
        .drop_duplicates()
        .shape[0]
    )

    status = (
        "PASS"
        if only_bns == 0
        and only_e2x == 0
        else "FAIL"
    )

    print("Saved detail file:", detail_file)
    print("Mapped   :", mapped)
    print("Only BNS :", only_bns)
    print("Only E2X :", only_e2x)
    print("Status   :", status)

    return {
        "ExtractName": extract_name,
        "BNSKeyCount": len(bns_keys),
        "E2XKeyCount": len(e2x_keys),
        "Mapped": mapped,
        "OnlyInBNS": only_bns,
        "OnlyInE2X": only_e2x,
        "Status": status
    }

def main():

    print("\n")
    print("=" * 100)
    print("E2X EXTRACT COMPARISON")
    print("=" * 100)

    print("\nBNS Folder:")
    print(OUTPUT_IN_SCOPE)

    print("\nE2X Folder:")
    print(VENDOR_FOLDER)

    print("\nValidation Folder:")
    print(VALIDATION_FOLDER)

    # --------------------------------------------------
    # Step 1: checksum count validation by distinct keys
    # --------------------------------------------------

    checksum_df = check_sum()

    # --------------------------------------------------
    # Step 2: detailed extract mapping files
    # --------------------------------------------------

    extract_results = []

    for extract_name, config in EXTRACT_CONFIG.items():

        try:

            result = check_extract(
                extract_name,
                config
            )

            extract_results.append(
                result
            )

        except Exception as ex:

            print(
                f"{extract_name}: ERROR -> {ex}"
            )

            extract_results.append(
                {
                    "ExtractName":
                        extract_name,

                    "BNSKeyCount":
                        "",

                    "E2XKeyCount":
                        "",

                    "Mapped":
                        "",

                    "OnlyInBNS":
                        "",

                    "OnlyInE2X":
                        "",

                    "Status":
                        "ERROR",

                    "Error":
                        str(ex)
                }
            )

    detail_summary_df = pd.DataFrame(
        extract_results
    )

    detail_summary_file = (
        VALIDATION_FOLDER /
        "e2x_detail_mapping_summary.csv"
    )

    detail_summary_df.to_csv(
        detail_summary_file,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 100)
    print("E2X DETAIL MAPPING SUMMARY")
    print("=" * 100)

    print(
        detail_summary_df.to_string(
            index=False
        )
    )

    print(
        f"\nSaved detail mapping summary:\n{detail_summary_file}"
    )

    print("\n")
    print("=" * 100)
    print("COMPARISON COMPLETE")
    print("=" * 100)

    return checksum_df

if __name__ == "__main__":

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

    main()