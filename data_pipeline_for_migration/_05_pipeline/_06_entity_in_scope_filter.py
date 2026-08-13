from datetime import date
from pathlib import Path

import pandas as pd

from _01_config.settings import (
    TEMP_FOLDER,
    OUTPUT_FOLDER,
    OUTPUT_IN_SCOPE,
    OUTPUT_OUT_SCOPE,
    SCOPE_FOLDER,
)

from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv


# ============================================================
# CONFIGURATION
# ============================================================

OFFBOARDED_FILE = (
    SCOPE_FOLDER /
    "client_offboarded_v7.csv"
)


# Each source file is mapped to:
# 1. The folder containing the file
# 2. A readable folder label for the statistics report
FILES_TO_PROCESS = {
    # --------------------------------------------------------
    # TEMP EXTRACTS
    # --------------------------------------------------------
    "fen_doc.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },
    # "fen_doc_detail.csv": {
    #     "folder": TEMP_FOLDER,
    #     "folder_label": "TEMP_FOLDER",
    # },
    "fen_client_detail.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },
    "fen_client_doc.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },
    "fen_association.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },
    "fen_product.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },
    "fen_address.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },
    "fen_contact.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },
    "fen_comment.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },
    "fen_taxid.csv": {
        "folder": TEMP_FOLDER,
        "folder_label": "TEMP_FOLDER",
    },

    # --------------------------------------------------------
    # MATCH OUTPUTS
    # --------------------------------------------------------
    "doc_fen_to_im.csv": {
        "folder": OUTPUT_FOLDER,
        "folder_label": "OUTPUT_FOLDER",
    },
    "doc_im_to_fen.csv": {
        "folder": OUTPUT_FOLDER,
        "folder_label": "OUTPUT_FOLDER",
    },
    "client_fen_to_im.csv": {
        "folder": OUTPUT_FOLDER,
        "folder_label": "OUTPUT_FOLDER",
    },
    "client_im_to_fen.csv": {
        "folder": OUTPUT_FOLDER,
        "folder_label": "OUTPUT_FOLDER",
    },

    # --------------------------------------------------------
    # FINAL OUTPUTS
    # --------------------------------------------------------
    "final_fen_to_im.csv": {
        "folder": OUTPUT_FOLDER,
        "folder_label": "OUTPUT_FOLDER",
    },
    "final_im_to_fen.csv": {
        "folder": OUTPUT_FOLDER,
        "folder_label": "OUTPUT_FOLDER",
    },
}


# ============================================================
# DISTINCT ENTITY KEY CONFIGURATION
# ============================================================

KEY_COLUMNS_BY_FILE = {
    "fen_doc.csv": [
        "LegalEntityId",
        "DocumentId",
    ],
    # "fen_doc_detail.csv": [
    #     "LegalEntityId",
    #     "DocumentId",
    # ],
    "fen_client_detail.csv": [
        "LegalEntityId",
    ],
    "fen_client_doc.csv": [
        "LegalEntityId",
        "DocumentId",
    ],
    "fen_association.csv": [
        "LegalEntityId",
        "AssociatedRelationId",
    ],
    "fen_product.csv": [
        "LegalEntityId",
        "ProductId",
    ],
    "fen_address.csv": [
        "LegalEntityId",
        "AddressId",
    ],
    "fen_contact.csv": [
        "LegalEntityId",
        "ContactId",
    ],
    "fen_comment.csv": [
        "LegalEntityId",
        "CommentId",
    ],
    "fen_taxid.csv": [
        "LegalEntityId",
        "TaxIdentiferId",
    ],
    "doc_fen_to_im.csv": [
        "LegalEntityId",
        "im_docnum",
    ],
    "doc_im_to_fen.csv": [
        "c1alias",
        "docnum",
    ],
    "client_fen_to_im.csv": [
        "LegalEntityId",
    ],
    "client_im_to_fen.csv": [
        "c1alias",
    ],
    "final_fen_to_im.csv": [
        "LegalEntityId",
        "im_docnum",
    ],
    "final_im_to_fen.csv": [
        "c1alias",
        "docnum",
    ],
}


# ============================================================
# LEGAL ENTITY COLUMN CONFIGURATION
# ============================================================

# This is the column used to:
# 1. Compare rows against client_offboarded_v7.csv
# 2. Calculate legal entity distinct counts
#
# The first available column in the configured list will be used.
LEGAL_ENTITY_COLUMNS_BY_FILE = {
    "fen_doc.csv": [
        "LegalEntityId",
    ],
    # "fen_doc_detail.csv": [
    #     "LegalEntityId",
    # ],
    "fen_client_detail.csv": [
        "LegalEntityId",
    ],
    "fen_client_doc.csv": [
        "LegalEntityId",
    ],
    "fen_association.csv": [
        "LegalEntityId",
    ],
    "fen_product.csv": [
        "LegalEntityId",
    ],
    "fen_address.csv": [
        "LegalEntityId",
    ],
    "fen_contact.csv": [
        "LegalEntityId",
    ],
    "fen_comment.csv": [
        "LegalEntityId",
    ],
    "fen_taxid.csv": [
        "LegalEntityId",
    ],

    # Prefer LegalEntityId when available for FEN-to-IM files.
    # Use im_c1alias as a fallback.
    "doc_fen_to_im.csv": [
        "LegalEntityId",
        "im_c1alias",
    ],
    "client_fen_to_im.csv": [
        "LegalEntityId",
        "im_c1alias",
    ],
    "final_fen_to_im.csv": [
        "LegalEntityId",
        "im_c1alias",
    ],

    # IM-to-FEN files should normally contain c1alias.
    # fen_LegalEntityId is retained as a fallback if the generated
    # output uses that column name instead.
    "doc_im_to_fen.csv": [
        "c1alias",
        "fen_LegalEntityId",
    ],
    "client_im_to_fen.csv": [
        "c1alias",
        "fen_LegalEntityId",
    ],
    "final_im_to_fen.csv": [
        "c1alias",
        "fen_LegalEntityId",
    ],
}


# ============================================================
# STATISTICS OUTPUT COLUMNS
# ============================================================

STATISTICS_COLUMNS = [
    "date",
    "data_source",
    "key_columns",

    "orig_row_count",
    "orig_legal_entity_count",
    "orig_entity_count",

    "in_scope_row_count",
    "in_scope_legal_entity_count",
    "in_scope_entity_count",

    "out_scope_row_count",
    "out_scope_legal_entity_count",
    "out_scope_entity_count",

    "row_count_validation",
    "legal_entity_count_validation",
    "entity_count_validation",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_identifier_series(series):
    """
    Normalize identifier values for reliable comparisons.

    Examples:
        123       -> "123"
        123.0     -> "123"
        " 123 "   -> "123"
        null      -> pandas NA

    The regex removes only trailing decimal zeros. It does not
    alter identifiers containing meaningful decimal values.
    """
    normalized = (
        series
        .astype("string")
        .str.strip()
        .str.replace(
            r"\.0+$",
            "",
            regex=True,
        )
    )

    normalized = normalized.replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "NaN": pd.NA,
            "None": pd.NA,
            "<NA>": pd.NA,
        }
    )

    return normalized


def load_offboarded_ids(scope_file):
    """
    Load client_offboarded_v7.csv.

    The file must contain a LegalEntityId column. Every ID in this
    file is treated as an out-of-scope entity.
    """
    if not scope_file.exists():
        raise FileNotFoundError(
            "Offboarded entity file was not found:\n"
            f"{scope_file}"
        )

    scope_df = load_csv(
        scope_file,
        low_memory=True,
    )

    required_column = "LegalEntityId"

    if required_column not in scope_df.columns:
        raise ValueError(
            f"{required_column} was not found in {scope_file}.\n"
            f"Available columns: {scope_df.columns.tolist()}"
        )

    normalized_ids = normalize_identifier_series(
        scope_df[required_column]
    )

    offboarded_ids = set(
        normalized_ids
        .dropna()
        .tolist()
    )

    return offboarded_ids


def get_legal_entity_column(df, filename):
    """
    Return the legal entity column configured for a file.

    The first configured column that exists in the DataFrame
    will be used.
    """
    candidate_columns = LEGAL_ENTITY_COLUMNS_BY_FILE.get(
        filename,
        [
            "LegalEntityId",
            "im_LegalEntityId",
        ],
    )

    for column in candidate_columns:
        if column in df.columns:
            return column

    raise ValueError(
        f"No legal entity column was found for {filename}.\n"
        f"Expected one of: {candidate_columns}\n"
        f"Available columns: {df.columns.tolist()}"
    )


def validate_key_columns(df, filename):
    """
    Confirm that all configured entity-key columns exist.
    """
    if filename not in KEY_COLUMNS_BY_FILE:
        raise ValueError(
            f"No key-column configuration was found for {filename}."
        )

    key_columns = KEY_COLUMNS_BY_FILE[filename]

    missing_columns = [
        column
        for column in key_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{filename} is missing configured key columns: "
            f"{missing_columns}\n"
            f"Configured key columns: {key_columns}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    return key_columns


def split_by_offboarded_entities(
    df,
    legal_entity_column,
    offboarded_ids,
):
    """
    Split source rows using the offboarded LegalEntityId list.

    OUT OF SCOPE:
        The normalized legal entity value exists in
        client_offboarded_v7.csv.

    IN SCOPE:
        The normalized legal entity value does not exist in
        client_offboarded_v7.csv.

    Rows with a missing legal entity value are placed in the
    in-scope bucket because the missing value cannot match an
    ID from the explicit offboarded list.
    """
    legal_entity_values = normalize_identifier_series(
        df[legal_entity_column]
    )

    out_scope_mask = legal_entity_values.isin(
        offboarded_ids
    )

    out_scope_df = (
        df.loc[out_scope_mask]
        .copy()
    )

    in_scope_df = (
        df.loc[~out_scope_mask]
        .copy()
    )

    return in_scope_df, out_scope_df


def calculate_distinct_count(df, key_columns):
    """
    Calculate the distinct count of the configured key.

    For one key column:
        Counts distinct non-null values.

    For multiple key columns:
        Counts distinct combinations.

    Rows with a missing value in any configured key column are
    excluded from the distinct entity count.
    """
    if df.empty:
        return 0

    missing_columns = [
        column
        for column in key_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Cannot calculate distinct count. "
            f"Missing columns: {missing_columns}"
        )

    key_df = df.loc[:, key_columns].copy()

    for column in key_columns:
        key_df[column] = normalize_identifier_series(
            key_df[column]
        )

    key_df = key_df.dropna(
        subset=key_columns,
        how="any",
    )

    distinct_count = (
        key_df
        .drop_duplicates(
            subset=key_columns
        )
        .shape[0]
    )

    return int(distinct_count)


def calculate_legal_entity_count(
    df,
    legal_entity_column,
):
    """
    Calculate the distinct count of non-null legal entities.
    """
    if df.empty:
        return 0

    if legal_entity_column not in df.columns:
        raise ValueError(
            f"{legal_entity_column} was not found while calculating "
            "the legal entity count."
        )

    legal_entity_values = normalize_identifier_series(
        df[legal_entity_column]
    )

    return int(
        legal_entity_values
        .dropna()
        .nunique()
    )


def validation_result(
    original_count,
    in_scope_count,
    out_scope_count,
):
    """
    Return PASS when the original count equals the sum of the
    in-scope and out-of-scope counts.
    """
    if (
        original_count
        ==
        in_scope_count
        +
        out_scope_count
    ):
        return "PASS"

    return "FAIL"


def build_statistics_row(
    run_date,
    data_source,
    key_columns,
    legal_entity_column,
    original_df,
    in_scope_df,
    out_scope_df,
):
    """
    Calculate all requested statistics for one source file.
    """
    # --------------------------------------------------------
    # Row counts
    # --------------------------------------------------------

    orig_row_count = len(original_df)
    in_scope_row_count = len(in_scope_df)
    out_scope_row_count = len(out_scope_df)

    # --------------------------------------------------------
    # Legal entity distinct counts
    # --------------------------------------------------------

    orig_legal_entity_count = (
        calculate_legal_entity_count(
            original_df,
            legal_entity_column,
        )
    )

    in_scope_legal_entity_count = (
        calculate_legal_entity_count(
            in_scope_df,
            legal_entity_column,
        )
    )

    out_scope_legal_entity_count = (
        calculate_legal_entity_count(
            out_scope_df,
            legal_entity_column,
        )
    )

    # --------------------------------------------------------
    # Configured entity-key distinct counts
    # --------------------------------------------------------

    orig_entity_count = calculate_distinct_count(
        original_df,
        key_columns,
    )

    in_scope_entity_count = calculate_distinct_count(
        in_scope_df,
        key_columns,
    )

    out_scope_entity_count = calculate_distinct_count(
        out_scope_df,
        key_columns,
    )

    # --------------------------------------------------------
    # Build statistics record
    # --------------------------------------------------------

    return {
        "date": run_date,
        "data_source": data_source,
        "key_columns": ", ".join(key_columns),

        "orig_row_count": orig_row_count,
        "orig_legal_entity_count": (
            orig_legal_entity_count
        ),
        "orig_entity_count": orig_entity_count,

        "in_scope_row_count": in_scope_row_count,
        "in_scope_legal_entity_count": (
            in_scope_legal_entity_count
        ),
        "in_scope_entity_count": (
            in_scope_entity_count
        ),

        "out_scope_row_count": out_scope_row_count,
        "out_scope_legal_entity_count": (
            out_scope_legal_entity_count
        ),
        "out_scope_entity_count": (
            out_scope_entity_count
        ),

        "row_count_validation": validation_result(
            orig_row_count,
            in_scope_row_count,
            out_scope_row_count,
        ),

        "legal_entity_count_validation": validation_result(
            orig_legal_entity_count,
            in_scope_legal_entity_count,
            out_scope_legal_entity_count,
        ),

        "entity_count_validation": validation_result(
            orig_entity_count,
            in_scope_entity_count,
            out_scope_entity_count,
        ),
    }


def print_statistics_row(statistics_row):
    """
    Print a concise processing result for one source file.
    """
    print(
        f"Original rows                 : "
        f"{statistics_row['orig_row_count']:,}"
    )
    print(
        f"In-scope rows                 : "
        f"{statistics_row['in_scope_row_count']:,}"
    )
    print(
        f"Out-of-scope rows             : "
        f"{statistics_row['out_scope_row_count']:,}"
    )

    print(
        f"Original legal entities       : "
        f"{statistics_row['orig_legal_entity_count']:,}"
    )
    print(
        f"In-scope legal entities       : "
        f"{statistics_row['in_scope_legal_entity_count']:,}"
    )
    print(
        f"Out-of-scope legal entities   : "
        f"{statistics_row['out_scope_legal_entity_count']:,}"
    )

    print(
        f"Original entity keys          : "
        f"{statistics_row['orig_entity_count']:,}"
    )
    print(
        f"In-scope entity keys          : "
        f"{statistics_row['in_scope_entity_count']:,}"
    )
    print(
        f"Out-of-scope entity keys      : "
        f"{statistics_row['out_scope_entity_count']:,}"
    )

    print(
        f"Row-count validation          : "
        f"{statistics_row['row_count_validation']}"
    )
    print(
        f"Legal-entity validation       : "
        f"{statistics_row['legal_entity_count_validation']}"
    )
    print(
        f"Entity-count validation       : "
        f"{statistics_row['entity_count_validation']}"
    )


# ============================================================
# MAIN PROCESS
# ============================================================

def main():
    print("\n" + "=" * 100)
    print("CLIENT OFFBOARDED ENTITY SCOPE FILTER")
    print("=" * 100)

    # --------------------------------------------------------
    # Ensure output directories exist
    # --------------------------------------------------------

    OUTPUT_IN_SCOPE.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_OUT_SCOPE.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_date = date.today().isoformat()

    # --------------------------------------------------------
    # Load the explicit out-of-scope entity list
    # --------------------------------------------------------

    print(
        f"\nLoading out-of-scope entities from:\n"
        f"{OFFBOARDED_FILE}"
    )

    offboarded_ids = load_offboarded_ids(
        OFFBOARDED_FILE
    )

    print(
        f"\nDistinct out-of-scope LegalEntityId values loaded: "
        f"{len(offboarded_ids):,}"
    )

    statistics_rows = []

    # --------------------------------------------------------
    # Process source files
    # --------------------------------------------------------

    for filename, file_config in FILES_TO_PROCESS.items():
        source_folder = file_config["folder"]
        folder_label = file_config["folder_label"]

        filepath = source_folder / filename

        # Example:
        # TEMP_FOLDER/fen_doc.csv
        data_source = (
            f"{folder_label}/{filename}"
        )

        print("\n" + "-" * 100)
        print(f"Processing file : {filename}")
        print(f"Source          : {filepath}")
        print("-" * 100)

        if not filepath.exists():
            print(
                f"{filename:<40} NOT FOUND"
            )
            continue

        # ----------------------------------------------------
        # Load source file
        # ----------------------------------------------------

        df = load_csv(
            filepath,
            low_memory=True,
        )

        print(
            f"Rows loaded     : {len(df):,}"
        )

        # ----------------------------------------------------
        # Validate file configuration and columns
        # ----------------------------------------------------

        legal_entity_column = get_legal_entity_column(
            df,
            filename,
        )

        key_columns = validate_key_columns(
            df,
            filename,
        )

        print(
            f"Scope column    : {legal_entity_column}"
        )
        print(
            f"Entity keys     : {', '.join(key_columns)}"
        )

        # ----------------------------------------------------
        # Split the source file
        # ----------------------------------------------------

        (
            in_scope_df,
            out_scope_df,
        ) = split_by_offboarded_entities(
            df=df,
            legal_entity_column=legal_entity_column,
            offboarded_ids=offboarded_ids,
        )

        # ----------------------------------------------------
        # Define output files
        # ----------------------------------------------------

        in_scope_file = (
            OUTPUT_IN_SCOPE /
            f"in_scope_{filename}"
        )

        out_scope_file = (
            OUTPUT_OUT_SCOPE /
            f"out_scope_{filename}"
        )

        # ----------------------------------------------------
        # Save in-scope output
        # ----------------------------------------------------

        save_to_csv(
            in_scope_df,
            in_scope_file,
        )

        # ----------------------------------------------------
        # Save out-of-scope output
        # ----------------------------------------------------

        save_to_csv(
            out_scope_df,
            out_scope_file,
        )

        # ----------------------------------------------------
        # Calculate statistics
        # ----------------------------------------------------

        statistics_row = build_statistics_row(
            run_date=run_date,
            data_source=data_source,
            key_columns=key_columns,
            legal_entity_column=legal_entity_column,
            original_df=df,
            in_scope_df=in_scope_df,
            out_scope_df=out_scope_df,
        )

        statistics_rows.append(
            statistics_row
        )

        print_statistics_row(
            statistics_row
        )

        print(
            f"In-scope file saved           : "
            f"{in_scope_file}"
        )
        print(
            f"Out-of-scope file saved       : "
            f"{out_scope_file}"
        )

    # --------------------------------------------------------
    # Create statistics DataFrame
    # --------------------------------------------------------

    statistics_df = pd.DataFrame(
        statistics_rows,
        columns=STATISTICS_COLUMNS,
    )

    # --------------------------------------------------------
    # Save statistics report
    # --------------------------------------------------------

    statistics_file = (
        OUTPUT_IN_SCOPE /
        "entity_scope_statistics.csv"
    )

    save_to_csv(
        statistics_df,
        statistics_file,
    )

    print("\n" + "=" * 100)
    print("ENTITY SCOPE STATISTICS")
    print("=" * 100)

    if statistics_df.empty:
        print(
            "No source files were processed."
        )
    else:
        print(
            statistics_df.to_string(
                index=False
            )
        )

    print(
        f"\nStatistics report saved:\n"
        f"{statistics_file}"
    )

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    if statistics_df.empty:
        failed_validation_count = 0
    else:
        validation_columns = [
            "row_count_validation",
            "legal_entity_count_validation",
            "entity_count_validation",
        ]

        failed_validation_count = int(
            (
                statistics_df[validation_columns]
                !=
                "PASS"
            )
            .any(axis=1)
            .sum()
        )

    print("\n" + "=" * 100)

    if failed_validation_count == 0:
        print(
            "CLIENT OFFBOARDED ENTITY SCOPE FILTER COMPLETE: "
            "ALL VALIDATIONS PASSED"
        )
    else:
        print(
            "CLIENT OFFBOARDED ENTITY SCOPE FILTER COMPLETE: "
            f"{failed_validation_count:,} FILE(S) HAVE "
            "ONE OR MORE FAILED VALIDATIONS"
        )

    print("=" * 100)


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    pd.set_option(
        "display.max_columns",
        None,
    )

    pd.set_option(
        "display.width",
        None,
    )

    pd.set_option(
        "display.max_colwidth",
        None,
    )

    main()