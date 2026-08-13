"""
todo :
- Add validation for step _14 FINAL IN SCOPE IM DOC
- load SCOPE_FOLDER/in_scope_im_doc_final.csv to im_doc_df, keep docnum, version
- load all im_doc_active_entity_x.csv files into im_doc_active_df, keep docnum, version
- load all im_doc_offboarded_v8_entity_x.csv files into im_doc_offboarded_v8_df, keep docnum, version
- mergo im_doc_active_df and im_doc_offboarded_v8_df in to im_doc_active_offboarded_v8 and remove duplicates
- compare im_doc_df with im_doc_active_offboarded_v8 and add columns to mark the gap
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

from _01_config.settings import TEMP_FOLDER,SCOPE_FOLDER 
from _01_config.settings import OUTPUT_FOLDER
from _01_config.settings import VALIDATION_FOLDER
from pandas.errors import EmptyDataError
try:
    from _01_config.settings import OUTPUT_IN_SCOPE
except ImportError:
    OUTPUT_IN_SCOPE = None

try:
    from _01_config.settings import OUTPUT_OUT_SCOPE
except ImportError:
    OUTPUT_OUT_SCOPE = None


# ============================================================
# Output Files
# ============================================================

VALIDATION_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

VALIDATION_LOG_CSV = (
    VALIDATION_FOLDER /
    "validation_log.csv"
)

VALIDATION_LOG_TXT = (
    VALIDATION_FOLDER /
    "validation_log.txt"
)


# ============================================================
# Constants
# ============================================================

CLIENT_COLUMNS = [
    "LegalEntityId",
    "fen_LegalEntityId",
    "c1alias",
]

ENTITY_COLUMNS = [
    "AddressId",
    "CommentId",
    "CaseId",
    "DocumentId",
    "ContactId",
    "AssociatedRelationId",
    "ProductId",
    "TaxIdentifierId",
    "TaxIdentiferId",
    "docnum",
    "im_docnum",
]

VALIDATION_COLUMNS = [
    "date",
    "step_name",
    "file_name",
    "start_time",
    "end_time",
    "duration_seconds",
    "DistinctClientCnt",
    "DistinctEntityCnt",
    "RowCnt",
    "ColumnCnt",
    "ColumnNameList",
    "ExpectedRows",
    "ActualRows",
    "Difference",
    "status",
    "notes",
]

VALIDATION_LOG_ROWS = []


# ============================================================
# General Helpers
# ============================================================

def reset_validation_outputs():
    """
    Reset validation output files and in-memory rows.
    Call once at the start of main.py.
    """

    VALIDATION_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    VALIDATION_LOG_ROWS.clear()

    Path(VALIDATION_LOG_TXT).write_text(
        "",
        encoding="utf-8"
    )

    if VALIDATION_LOG_CSV.exists():
        VALIDATION_LOG_CSV.unlink()


def log_write(
    log_file,
    msg=""
):
    """
    Print message and append it to validation_log.txt.
    """

    print(msg)

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as f:
        f.write(str(msg))
        f.write("\n")


def format_datetime(
    value
):
    if isinstance(value, datetime):
        return value.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return ""


def get_duration_seconds(
    start_time,
    end_time
):
    return round(
        (
            end_time -
            start_time
        ).total_seconds(),
        2
    )


def normalize_key_series(
    series
):
    """
    Normalize key values so 1, 1.0, and '1' compare consistently.
    """

    return (
        series
        .astype(str)
        .str.strip()
        .str.replace(
            ".0",
            "",
            regex=False
        )
    )


def first_existing_path(
    paths
):
    """
    Return the first existing path from a list.
    """

    for path in paths:
        if path is not None:
            path = Path(path)

            if path.exists():
                return path

    return None

def normalize_doc_version_keys(
    df,
    required_columns=("docnum", "version")
):
    """
    Keep and normalize docnum/version for reliable comparison.

    Returns:
        normalized_df, error_message

    The returned dataframe:
    - contains only docnum and version
    - removes rows where either key is blank
    - removes duplicate docnum/version combinations
    """
    if df is None:
        return None, "Dataframe was not loaded."

    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        return (
            None,
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    normalized_df = df[
        list(required_columns)
    ].copy()

    for col in required_columns:
        normalized_df[col] = (
            normalized_df[col]
            .astype("string")
            .str.strip()
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
        )

        normalized_df[col] = (
            normalized_df[col]
            .replace(
                {
                    "": pd.NA,
                    "nan": pd.NA,
                    "None": pd.NA,
                    "<NA>": pd.NA,
                }
            )
        )

    normalized_df = (
        normalized_df
        .dropna(
            subset=list(required_columns)
        )
        .drop_duplicates(
            subset=list(required_columns)
        )
        .reset_index(drop=True)
    )

    return normalized_df, ""


def load_and_combine_csv_files(
    file_paths,
    required_columns=("docnum", "version")
):
    """
    Load multiple CSV files and combine distinct docnum/version keys.

    Returns:
        combined_df,
        loaded_file_names,
        skipped_file_messages
    """
    dataframes = []
    loaded_file_names = []
    skipped_file_messages = []

    for file_path in file_paths:
        file_path = Path(file_path)

        try:
            source_df = pd.read_csv(
                file_path,
                usecols=lambda col: col in required_columns,
                dtype="string",
                low_memory=False
            )

        except EmptyDataError:
            skipped_file_messages.append(
                f"{file_path.name}: empty CSV"
            )
            continue

        except ValueError as exc:
            skipped_file_messages.append(
                f"{file_path.name}: unable to load required columns; {exc}"
            )
            continue

        except Exception as exc:
            skipped_file_messages.append(
                f"{file_path.name}: read error; {exc}"
            )
            continue

        normalized_df, error_message = (
            normalize_doc_version_keys(
                source_df,
                required_columns=required_columns
            )
        )

        if normalized_df is None:
            skipped_file_messages.append(
                f"{file_path.name}: {error_message}"
            )
            continue

        normalized_df["SourceFile"] = file_path.name

        dataframes.append(
            normalized_df
        )

        loaded_file_names.append(
            file_path.name
        )

    if not dataframes:
        return (
            pd.DataFrame(
                columns=[
                    *required_columns,
                    "SourceFile",
                ]
            ),
            loaded_file_names,
            skipped_file_messages,
        )

    combined_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    return (
        combined_df,
        loaded_file_names,
        skipped_file_messages,
    )
# ============================================================
# CSV and Metadata Helpers
# ============================================================

def read_csv_safe(
    path
):
    """
    Read CSV safely.
    Return None if file does not exist.
    """

    path = Path(path)

    if not path.exists():
        return None

    return pd.read_csv(
        path,
        low_memory=False
    )


def get_df_client_count(
    df
):
    """
    Return distinct client count from an in-memory dataframe.
    """

    if df is None:
        return ""

    for col in CLIENT_COLUMNS:
        if col in df.columns:
            return (
                df[col]
                .dropna()
                .astype(str)
                .str.strip()
                .nunique()
            )

    return ""


def get_df_entity_count(
    df
):
    """
    Return distinct entity counts from an in-memory dataframe.
    Multiple entity columns are returned as a readable string.
    """

    if df is None:
        return ""

    counts = []

    for col in ENTITY_COLUMNS:
        if col in df.columns:
            cnt = (
                df[col]
                .dropna()
                .astype(str)
                .str.strip()
                .nunique()
            )

            counts.append(
                f"{col}={cnt}"
            )

    return "; ".join(counts)



def get_csv_metadata(
    path,
    chunksize=200000
):

    path = Path(path)

    if not path.exists():

        return {
            "exists": False,
            "RowCnt": 0,
            "ColumnCnt": 0,
            "ColumnNameList": [],
            "DistinctClientCnt": "",
            "DistinctEntityCnt": "",
            "notes": "File not found"
        }

    try:

        row_count = 0
        column_list = []

        client_values = set()

        entity_values = {}

        for chunk in pd.read_csv(
            path,
            chunksize=chunksize,
            low_memory=False
        ):

            row_count += len(chunk)

            if not column_list:
                column_list = (
                    chunk.columns.tolist()
                )

            for col in CLIENT_COLUMNS:

                if col in chunk.columns:

                    client_values.update(
                        chunk[col]
                        .dropna()
                        .astype(str)
                    )

                    break

            for col in ENTITY_COLUMNS:

                if col in chunk.columns:

                    if (
                        col
                        not in entity_values
                    ):
                        entity_values[col] = set()

                    entity_values[col].update(
                        chunk[col]
                        .dropna()
                        .astype(str)
                    )

        entity_count_text = "; ".join(
            [
                f"{col}={len(values)}"
                for col, values
                in entity_values.items()
            ]
        )

        return {
            "exists": True,
            "RowCnt": row_count,
            "ColumnCnt": len(column_list),
            "ColumnNameList": column_list,
            "DistinctClientCnt": (
                len(client_values)
                if client_values
                else ""
            ),
            "DistinctEntityCnt":
                entity_count_text,
            "notes": ""
        }

    except EmptyDataError:

        return {
            "exists": True,
            "RowCnt": 0,
            "ColumnCnt": 0,
            "ColumnNameList": [],
            "DistinctClientCnt": "",
            "DistinctEntityCnt": "",
            "notes": "Empty CSV"
        }
# ============================================================
# Validation Log Row Helpers
# ============================================================

def add_validation_log_row(
    step_name,
    file_name,
    start_time,
    end_time,
    row_count,
    column_count,
    column_name_list,
    distinct_client_cnt="",
    distinct_entity_cnt="",
    expected_rows="",
    actual_rows="",
    difference="",
    status="",
    notes=""
):
    """
    Add one row to the validation log.

    Important:
    status defaults to blank.
    Only validations with real checks should set PASS or FAIL.
    """

    VALIDATION_LOG_ROWS.append(
        {
            "date":
                datetime.now().strftime(
                    "%Y-%m-%d"
                ),

            "step_name":
                step_name,

            "file_name":
                file_name,

            "start_time":
                format_datetime(
                    start_time
                ),

            "end_time":
                format_datetime(
                    end_time
                ),

            "duration_seconds":
                get_duration_seconds(
                    start_time,
                    end_time
                ),

            "DistinctClientCnt":
                distinct_client_cnt,

            "DistinctEntityCnt":
                distinct_entity_cnt,

            "RowCnt":
                row_count,

            "ColumnCnt":
                column_count,

            "ColumnNameList":
                str(column_name_list),

            "ExpectedRows":
                expected_rows,

            "ActualRows":
                actual_rows,

            "Difference":
                difference,

            "status":
                status,

            "notes":
                notes,
        }
    )


def add_validation_log_row_from_df(
    step_name,
    file_name,
    start_time,
    end_time,
    df,
    expected_rows="",
    actual_rows="",
    difference="",
    status="",
    notes=""
):
    """
    Add one validation log row from an already-loaded dataframe.
    """

    if df is None:
        add_validation_log_row(
            step_name=step_name,
            file_name=file_name,
            start_time=start_time,
            end_time=end_time,
            row_count=0,
            column_count=0,
            column_name_list=[],
            expected_rows=expected_rows,
            actual_rows=actual_rows,
            difference=difference,
            status=status,
            notes=notes,
        )

        return

    add_validation_log_row(
        step_name=step_name,
        file_name=file_name,
        start_time=start_time,
        end_time=end_time,
        row_count=len(df),
        column_count=len(df.columns),
        column_name_list=df.columns.tolist(),
        distinct_client_cnt=get_df_client_count(df),
        distinct_entity_cnt=get_df_entity_count(df),
        expected_rows=expected_rows,
        actual_rows=actual_rows,
        difference=difference,
        status=status,
        notes=notes,
    )


def add_validation_log_row_from_metadata(
    step_name,
    file_name,
    start_time,
    end_time,
    metadata,
    expected_rows="",
    actual_rows="",
    difference="",
    status="",
    notes=""
):
    """
    Add one validation log row from chunked CSV metadata.
    """

    add_validation_log_row(
        step_name=step_name,
        file_name=file_name,
        start_time=start_time,
        end_time=end_time,
        row_count=metadata.get(
            "RowCnt",
            0
        ),
        column_count=metadata.get(
            "ColumnCnt",
            0
        ),
        column_name_list=metadata.get(
            "ColumnNameList",
            []
        ),
        distinct_client_cnt=metadata.get(
            "DistinctClientCnt",
            ""
        ),
        distinct_entity_cnt=metadata.get(
            "DistinctEntityCnt",
            ""
        ),
        expected_rows=expected_rows,
        actual_rows=actual_rows,
        difference=difference,
        status=status,
        notes=notes,
    )


# ============================================================
# Sample Helpers
# ============================================================

def sample_csv_by_key(
    path,
    key_col,
    key_value,
    max_rows=100,
    chunksize=200000
):

    path = Path(path)

    if not path.exists():
        return pd.DataFrame()

    try:

        samples = []

        for chunk in pd.read_csv(
            path,
            chunksize=chunksize,
            low_memory=False
        ):

            if key_col not in chunk.columns:
                return pd.DataFrame()

            match = chunk[
                normalize_key_series(
                    chunk[key_col]
                ).eq(str(key_value))
            ]

            if not match.empty:
                samples.append(match)

            if (
                sum(
                    len(x)
                    for x in samples
                )
                >= max_rows
            ):
                break

        if not samples:
            return pd.DataFrame()

        return (
            pd.concat(
                samples,
                ignore_index=True
            )
            .head(max_rows)
        )

    except EmptyDataError:

        return pd.DataFrame()

def create_default_sample_from_csv(
    path,
    column_list,
    source_file,
    max_rows=100
):
    """
    Create default sample from CSV using chunking.

    Sampling priority:
    LegalEntityId = 1
    fen_LegalEntityId = 1
    c1alias = 1
    docnum = 1
    im_docnum = 1
    """

    key_sequence = [
        "LegalEntityId",
        "fen_LegalEntityId",
        "c1alias",
        "docnum",
        "im_docnum",
    ]

    for key_col in key_sequence:
        if key_col in column_list:
            sample = sample_csv_by_key(
                path=path,
                key_col=key_col,
                key_value=1,
                max_rows=max_rows,
            )

            if not sample.empty:
                sample.insert(
                    0,
                    "SourceFile",
                    source_file
                )

                return sample

    return None


def save_step_samples(
    step_name,
    samples
):
    """
    Save step sample output if sample rows exist.
    """

    if not samples:
        return

    output_file = (
        VALIDATION_FOLDER /
        f"{step_name}_samples.csv"
    )

    pd.concat(
        samples,
        ignore_index=True
    ).to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"Saved: {output_file}"
    )


def print_file_summary(
    file_name,
    metadata,
    log_file
):
    """
    Print metadata summary to console and validation_log.txt.
    """

    log_write(log_file)
    log_write(
        log_file,
        "=" * 80
    )
    log_write(
        log_file,
        f"FILE: {file_name}"
    )
    log_write(
        log_file,
        "=" * 80
    )
    log_write(
        log_file,
        f"Rows: {metadata.get('RowCnt', 0):,}"
    )
    log_write(
        log_file,
        f"Columns: {metadata.get('ColumnCnt', 0):,}"
    )
    log_write(
        log_file,
        "Column List:"
    )

    for col in metadata.get(
        "ColumnNameList",
        []
    ):
        log_write(
            log_file,
            col
        )

    log_write(log_file)


# ============================================================
# STEP 01 - EXTRACT VALIDATION
# ============================================================

def validate_step_01_extract(
    context,
    log_file
):
    """
    Step 01 logs metadata for all CSVs in TEMP_FOLDER.
    No validation rule is applied here, so status remains blank.
    """

    log_write(
        log_file,
        "STEP 01 - EXTRACT VALIDATION"
    )

    step_samples = []

    temp_files = sorted(
        TEMP_FOLDER.glob("*.csv")
    )

    for file_path in temp_files:
        step_start = datetime.now()

        metadata = get_csv_metadata(
            file_path
        )

        if metadata["RowCnt"] == 0:

            log_write(
                log_file,
                f"WARNING: {file_path.name} is empty"
            )

        context[
            f"{file_path.name}_metadata"
        ] = metadata

        print_file_summary(
            file_path.name,
            metadata,
            log_file
        )

        step_end = datetime.now()

        add_validation_log_row_from_metadata(
            step_name="01 Extract",
            file_name=file_path.name,
            start_time=step_start,
            end_time=step_end,
            metadata=metadata,
            status="",
            notes="Metadata only. No PASS or FAIL validation applied."
        )

        sample = create_default_sample_from_csv(
            path=file_path,
            column_list=metadata.get(
                "ColumnNameList",
                []
            ),
            source_file=file_path.name,
        )

        if sample is not None:
            step_samples.append(sample)

    save_step_samples(
        "step01_extract",
        step_samples
    )

    return context


# ============================================================
# STEP 02 - DOCUMENT MATCH VALIDATION
# ============================================================

def validate_step_02_document_match(
    context,
    log_file
):
    """
    Validation:
    - doc_fen_to_im row count should equal fen_client_doc row count.
    - doc_im_to_fen row count should equal im_client_doc row count.
    """

    log_write(
        log_file,
        "STEP 02 - DOCUMENT MATCH VALIDATION"
    )

    step_samples = []

    files_to_validate = [
        {
            "file_name": "doc_fen_to_im.csv",
            "path": OUTPUT_FOLDER / "doc_fen_to_im.csv",
            "expected_metadata_key": "fen_client_doc.csv_metadata",
        },
        {
            "file_name": "doc_im_to_fen.csv",
            "path": OUTPUT_FOLDER / "doc_im_to_fen.csv",
            "expected_metadata_key": "im_client_doc.csv_metadata",
        },
    ]

    for item in files_to_validate:
        step_start = datetime.now()

        metadata = get_csv_metadata(
            item["path"]
        )

        context[
            f"{item['file_name']}_metadata"
        ] = metadata

        expected_metadata = context.get(
            item["expected_metadata_key"],
            {}
        )

        expected_rows = expected_metadata.get(
            "RowCnt",
            ""
        )

        actual_rows = metadata.get(
            "RowCnt",
            0
        )

        if expected_rows == "":
            status = ""
            difference = ""
            notes = "Expected row count was not available."
        else:
            difference = (
                actual_rows -
                expected_rows
            )

            status = (
                "PASS"
                if actual_rows == expected_rows
                else "FAIL"
            )

            notes = "Validated output row count against source input row count."

        add_validation_log_row_from_metadata(
            step_name="02 Match Documents",
            file_name=item["file_name"],
            start_time=step_start,
            end_time=datetime.now(),
            metadata=metadata,
            expected_rows=expected_rows,
            actual_rows=actual_rows,
            difference=difference,
            status=status,
            notes=notes,
        )

        sample = create_default_sample_from_csv(
            path=item["path"],
            column_list=metadata.get(
                "ColumnNameList",
                []
            ),
            source_file=item["file_name"],
        )

        if sample is not None:
            step_samples.append(sample)

    save_step_samples(
        "step02_document_match",
        step_samples
    )

    return context


# ============================================================
# STEP 03 - CLIENT MATCH VALIDATION
# ============================================================

def validate_step_03_client_match(
    context,
    log_file
):
    """
    Validation:
    - client_fen_to_im rows should equal distinct client count in fen_client_doc.
    - client_im_to_fen rows should equal distinct client count in im_client_doc.
    """

    log_write(
        log_file,
        "STEP 03 - CLIENT MATCH VALIDATION"
    )

    step_samples = []

    files_to_validate = [
        {
            "file_name": "client_fen_to_im.csv",
            "path": OUTPUT_FOLDER / "client_fen_to_im.csv",
            "expected_metadata_key": "fen_client_doc.csv_metadata",
        },
        {
            "file_name": "client_im_to_fen.csv",
            "path": OUTPUT_FOLDER / "client_im_to_fen.csv",
            "expected_metadata_key": "im_client_doc.csv_metadata",
        },
    ]

    for item in files_to_validate:
        step_start = datetime.now()

        metadata = get_csv_metadata(
            item["path"]
        )

        context[
            f"{item['file_name']}_metadata"
        ] = metadata

        expected_metadata = context.get(
            item["expected_metadata_key"],
            {}
        )

        expected_rows = expected_metadata.get(
            "DistinctClientCnt",
            ""
        )

        actual_rows = metadata.get(
            "RowCnt",
            0
        )

        if expected_rows == "":
            status = ""
            difference = ""
            notes = "Expected distinct client count was not available."
        else:
            difference = (
                actual_rows -
                expected_rows
            )

            status = (
                "PASS"
                if actual_rows == expected_rows
                else "FAIL"
            )

            notes = "Validated output row count against expected distinct client count."

        add_validation_log_row_from_metadata(
            step_name="03 Match Clients",
            file_name=item["file_name"],
            start_time=step_start,
            end_time=datetime.now(),
            metadata=metadata,
            expected_rows=expected_rows,
            actual_rows=actual_rows,
            difference=difference,
            status=status,
            notes=notes,
        )

        sample = create_default_sample_from_csv(
            path=item["path"],
            column_list=metadata.get(
                "ColumnNameList",
                []
            ),
            source_file=item["file_name"],
        )

        if sample is not None:
            step_samples.append(sample)

    save_step_samples(
        "step03_client_match",
        step_samples
    )

    return context


# ============================================================
# STEP 04 - FINAL FEN VALIDATION
# ============================================================

def validate_step_04_final_fen(
    context,
    log_file
):
    """
    Validation:
    - final_fen_to_im row count should equal doc_fen_to_im row count.
    Uses chunked metadata for large final file.
    """

    step_start = datetime.now()

    log_write(
        log_file,
        "STEP 04 - FINAL FEN VALIDATION"
    )

    step_samples = []

    file_name = "final_fen_to_im.csv"

    file_path = (
        OUTPUT_FOLDER /
        file_name
    )

    metadata = get_csv_metadata(
        file_path
    )

    context[
        f"{file_name}_metadata"
    ] = metadata

    expected_metadata = context.get(
        "doc_fen_to_im.csv_metadata",
        {}
    )

    expected_rows = expected_metadata.get(
        "RowCnt",
        ""
    )

    actual_rows = metadata.get(
        "RowCnt",
        0
    )

    if expected_rows == "":
        status = ""
        difference = ""
        notes = "Expected doc_fen_to_im row count was not available."
    else:
        difference = (
            actual_rows -
            expected_rows
        )

        status = (
            "PASS"
            if actual_rows == expected_rows
            else "FAIL"
        )

        notes = "Validated final FEN row count against doc_fen_to_im."

    sample = create_default_sample_from_csv(
        path=file_path,
        column_list=metadata.get(
            "ColumnNameList",
            []
        ),
        source_file=file_name,
    )

    if sample is not None:
        step_samples.append(sample)

    else:
        log_write(
            log_file,
            "No sample rows found for final_fen_to_im.csv"
        )

    add_validation_log_row_from_metadata(
        step_name="04 Final FEN",
        file_name=file_name,
        start_time=step_start,
        end_time=datetime.now(),
        metadata=metadata,
        expected_rows=expected_rows,
        actual_rows=actual_rows,
        difference=difference,
        status=status,
        notes=notes,
    )

    save_step_samples(
        "step04_final_fen",
        step_samples
    )

    return context


# ============================================================
# STEP 05 - FINAL IM VALIDATION
# ============================================================

def validate_step_05_final_im(
    context,
    log_file
):
    """
    Validation:
    - final_im_to_fen row count should equal doc_im_to_fen row count.
    Uses chunked metadata for large final file.
    """

    step_start = datetime.now()

    log_write(
        log_file,
        "STEP 05 - FINAL IM VALIDATION"
    )

    step_samples = []

    file_name = "final_im_to_fen.csv"

    file_path = (
        OUTPUT_FOLDER /
        file_name
    )

    metadata = get_csv_metadata(
        file_path
    )

    context[
        f"{file_name}_metadata"
    ] = metadata

    expected_metadata = context.get(
        "doc_im_to_fen.csv_metadata",
        {}
    )

    expected_rows = expected_metadata.get(
        "RowCnt",
        ""
    )

    actual_rows = metadata.get(
        "RowCnt",
        0
    )

    if expected_rows == "":
        status = ""
        difference = ""
        notes = "Expected doc_im_to_fen row count was not available."
    else:
        difference = (
            actual_rows -
            expected_rows
        )

        status = (
            "PASS"
            if actual_rows == expected_rows
            else "FAIL"
        )

        notes = "Validated final IM row count against doc_im_to_fen."

    sample = create_default_sample_from_csv(
        path=file_path,
        column_list=metadata.get(
            "ColumnNameList",
            []
        ),
        source_file=file_name,
    )

    if sample is not None:
        step_samples.append(sample)

    else:
        log_write(
            log_file,
            "No sample rows found for final_im_to_fen.csv"
        )

    add_validation_log_row_from_metadata(
        step_name="05 Final IM",
        file_name=file_name,
        start_time=step_start,
        end_time=datetime.now(),
        metadata=metadata,
        expected_rows=expected_rows,
        actual_rows=actual_rows,
        difference=difference,
        status=status,
        notes=notes,
    )

    save_step_samples(
        "step05_final_im",
        step_samples
    )

    return context


# ============================================================
# STEP 06 - ENTITY IN SCOPE FILTER VALIDATION
# ============================================================

def validate_step_06_entity_scope_filter(
    context,
    log_file
):
    """
    Validation:
    - OriginalRows should equal InScopeRows plus OutScopeRows.
    """

    log_write(
        log_file,
        "STEP 06 - ENTITY IN SCOPE FILTER VALIDATION"
    )

    candidate_summary_files = [
        (
            OUTPUT_IN_SCOPE /
            "entity_in_scope_summary.csv"
            if OUTPUT_IN_SCOPE is not None
            else None
        ),
        TEMP_FOLDER /
        "Output_In_Scope" /
        "entity_in_scope_summary.csv",
        OUTPUT_FOLDER /
        "Output_In_Scope" /
        "entity_in_scope_summary.csv",
    ]

    summary_file = first_existing_path(
        candidate_summary_files
    )

    if summary_file is None:
        row_start = datetime.now()
        row_end = datetime.now()

        add_validation_log_row(
            step_name="06 Entity In Scope Filter",
            file_name="entity_in_scope_summary.csv",
            start_time=row_start,
            end_time=row_end,
            row_count=0,
            column_count=0,
            column_name_list=[],
            status="",
            notes="entity_in_scope_summary.csv was not found."
        )

        log_write(
            log_file,
            "entity_in_scope_summary.csv was not found."
        )

        return context

    summary_df = pd.read_csv(
        summary_file,
        low_memory=False
    )

    context[
        "entity_in_scope_summary.csv"
    ] = summary_df

    log_write(
        log_file,
        f"Entity scope summary file: {summary_file}"
    )

    log_write(
        log_file,
        summary_df.to_string(index=False)
    )

    for _, row in summary_df.iterrows():
        row_start = datetime.now()

        file_name = row.get(
            "FileName",
            ""
        )

        original_rows = row.get(
            "OriginalRows",
            ""
        )

        in_scope_rows = row.get(
            "InScopeRows",
            ""
        )

        out_scope_rows = row.get(
            "OutScopeRows",
            ""
        )

        if (
            original_rows != ""
            and in_scope_rows != ""
            and out_scope_rows != ""
        ):
            actual_rows = (
                in_scope_rows +
                out_scope_rows
            )

            difference = (
                actual_rows -
                original_rows
            )

            status = (
                "PASS"
                if difference == 0
                else "FAIL"
            )

            notes = "Validated OriginalRows equals InScopeRows plus OutScopeRows."

        else:
            actual_rows = ""
            difference = ""
            status = ""
            notes = "Required row-count columns were not available."

        row_end = datetime.now()

        add_validation_log_row(
            step_name="06 Entity In Scope Filter",
            file_name=file_name,
            start_time=row_start,
            end_time=row_end,
            row_count=actual_rows,
            column_count=len(summary_df.columns),
            column_name_list=summary_df.columns.tolist(),
            expected_rows=original_rows,
            actual_rows=actual_rows,
            difference=difference,
            status=status,
            notes=notes,
        )

    summary_df.head(100).to_csv(
        VALIDATION_FOLDER /
        "step06_entity_scope_filter_samples.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return context


# ============================================================
# STEP 10 - SCOPING VALIDATION
# ============================================================

def validate_step_10_scoping(
    context,
    log_file
):
    """
    Step 10 logs scoping summary.
    No validation rule is applied here, so status remains blank.
    """

    step_start = datetime.now()

    log_write(
        log_file,
        "STEP 10 - SCOPING VALIDATION"
    )

    scope_summary = (
        TEMP_FOLDER /
        "scope" /
        "01_scope_summary.csv"
    )

    if not scope_summary.exists():
        step_end = datetime.now()

        add_validation_log_row(
            step_name="10 Scoping",
            file_name="01_scope_summary.csv",
            start_time=step_start,
            end_time=step_end,
            row_count=0,
            column_count=0,
            column_name_list=[],
            status="",
            notes="01_scope_summary.csv was not found."
        )

        log_write(
            log_file,
            "01_scope_summary.csv was not found."
        )

        return context

    df = pd.read_csv(
        scope_summary,
        low_memory=False
    )

    context[
        "01_scope_summary.csv"
    ] = df

    total_client_cnt = ""

    if "totalClientCnt" in df.columns:
        total_client_cnt = (
            pd.to_numeric(
                df["totalClientCnt"],
                errors="coerce"
            )
            .dropna()
            .sum()
        )

    total_doc_cnt = ""

    if "totalDocCount" in df.columns:
        total_doc_cnt = (
            pd.to_numeric(
                df["totalDocCount"],
                errors="coerce"
            )
            .dropna()
            .sum()
        )

    step_end = datetime.now()

    add_validation_log_row(
        step_name="10 Scoping",
        file_name="01_scope_summary.csv",
        start_time=step_start,
        end_time=step_end,
        row_count=len(df),
        column_count=len(df.columns),
        column_name_list=df.columns.tolist(),
        distinct_client_cnt=total_client_cnt,
        distinct_entity_cnt=total_doc_cnt,
        status="",
        notes="Scoping summary logged. No PASS or FAIL validation applied."
    )

    df.head(100).to_csv(
        VALIDATION_FOLDER /
        "step10_scoping_samples.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return context

# ============================================================
# STEP 14 - FINAL IN SCOPE IM DOC VALIDATION
# ============================================================

def validate_step_14_final_in_scope_im_doc(
    context,
    log_file
):
    """
    Validation:
    - Load SCOPE_FOLDER/in_scope_im_doc_final.csv.
    - Keep distinct docnum/version keys.
    - Load all im_doc_active_entity_x.csv files.
    - Load all im_doc_offboarded_v8_entity_x.csv files.
    - Combine active and offboarded keys and remove duplicates.
    - Compare both datasets using docnum/version.
    - Save the full comparison and a gap-focused sample.

    PASS:
    - Every final in-scope key exists in active/offboarded.
    - No active/offboarded key is absent from the final in-scope file.

    FAIL:
    - At least one key exists on only one side.
    """
    step_start = datetime.now()

    step_name = "14 Final In Scope IM Doc"
    final_file_name = "in_scope_im_doc_final.csv"

    comparison_file_name = (
        "step14_final_in_scope_im_doc_validation.csv"
    )

    sample_file_name = (
        "step14_final_in_scope_im_doc_samples.csv"
    )

    log_write(
        log_file,
        "STEP 14 - FINAL IN SCOPE IM DOC VALIDATION"
    )

    final_file_path = (
        SCOPE_FOLDER /
        final_file_name
    )

    comparison_file_path = (
        VALIDATION_FOLDER /
        comparison_file_name
    )

    sample_file_path = (
        VALIDATION_FOLDER /
        sample_file_name
    )

    # The wildcard allows entity_1, entity_2, and similar files.
    active_file_paths = sorted(
        SCOPE_FOLDER.glob(
            "im_doc_active_entity_*.csv"
        )
    )

    offboarded_file_paths = sorted(
        SCOPE_FOLDER.glob(
            "im_doc_offboarded_v8_entity_*.csv"
        )
    )

    log_write(
        log_file,
        f"Final in-scope file: {final_file_path}"
    )

    log_write(
        log_file,
        f"Active files found: {len(active_file_paths)}"
    )

    log_write(
        log_file,
        f"Offboarded V8 files found: {len(offboarded_file_paths)}"
    )

    # --------------------------------------------------------
    # Validate required input files
    # --------------------------------------------------------

    missing_inputs = []

    if not final_file_path.exists():
        missing_inputs.append(
            final_file_name
        )

    if not active_file_paths:
        missing_inputs.append(
            "im_doc_active_entity_*.csv"
        )

    if not offboarded_file_paths:
        missing_inputs.append(
            "im_doc_offboarded_v8_entity_*.csv"
        )

    if missing_inputs:
        step_end = datetime.now()

        notes = (
            "Required input files were not found: "
            + ", ".join(missing_inputs)
        )

        log_write(
            log_file,
            notes
        )

        add_validation_log_row(
            step_name=step_name,
            file_name=comparison_file_name,
            start_time=step_start,
            end_time=step_end,
            row_count=0,
            column_count=0,
            column_name_list=[],
            expected_rows="",
            actual_rows="",
            difference="",
            status="FAIL",
            notes=notes,
        )

        return context

    # --------------------------------------------------------
    # Load final in-scope IM document keys
    # --------------------------------------------------------

    try:
        im_doc_source_df = pd.read_csv(
            final_file_path,
            usecols=lambda col: col in [
                "docnum",
                "version",
            ],
            dtype="string",
            low_memory=False
        )

    except EmptyDataError:
        im_doc_source_df = pd.DataFrame(
            columns=[
                "docnum",
                "version",
            ]
        )

    except Exception as exc:
        step_end = datetime.now()

        notes = (
            f"Unable to read {final_file_name}: {exc}"
        )

        log_write(
            log_file,
            notes
        )

        add_validation_log_row(
            step_name=step_name,
            file_name=comparison_file_name,
            start_time=step_start,
            end_time=step_end,
            row_count=0,
            column_count=0,
            column_name_list=[],
            status="FAIL",
            notes=notes,
        )

        return context

    im_doc_df, im_doc_error = (
        normalize_doc_version_keys(
            im_doc_source_df
        )
    )

    if im_doc_df is None:
        step_end = datetime.now()

        notes = (
            f"{final_file_name}: {im_doc_error}"
        )

        log_write(
            log_file,
            notes
        )

        add_validation_log_row(
            step_name=step_name,
            file_name=comparison_file_name,
            start_time=step_start,
            end_time=step_end,
            row_count=0,
            column_count=0,
            column_name_list=[],
            status="FAIL",
            notes=notes,
        )

        return context

    # --------------------------------------------------------
    # Load active files
    # --------------------------------------------------------

    (
        im_doc_active_with_source_df,
        active_loaded_files,
        active_skipped_files,
    ) = load_and_combine_csv_files(
        active_file_paths
    )

    im_doc_active_df = (
        im_doc_active_with_source_df[
            [
                "docnum",
                "version",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Load offboarded V8 files
    # --------------------------------------------------------

    (
        im_doc_offboarded_with_source_df,
        offboarded_loaded_files,
        offboarded_skipped_files,
    ) = load_and_combine_csv_files(
        offboarded_file_paths
    )

    im_doc_offboarded_v8_df = (
        im_doc_offboarded_with_source_df[
            [
                "docnum",
                "version",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    skipped_file_messages = (
        active_skipped_files
        + offboarded_skipped_files
    )

    for message in skipped_file_messages:
        log_write(
            log_file,
            f"WARNING: {message}"
        )

    # --------------------------------------------------------
    # Combine active and offboarded V8
    # --------------------------------------------------------

    im_doc_active_offboarded_v8 = (
        pd.concat(
            [
                im_doc_active_df,
                im_doc_offboarded_v8_df,
            ],
            ignore_index=True
        )
        .drop_duplicates(
            subset=[
                "docnum",
                "version",
            ]
        )
        .reset_index(drop=True)
    )

    # Add source indicators before the final comparison.
    active_keys = im_doc_active_df.copy()
    active_keys["InActive"] = True

    offboarded_keys = (
        im_doc_offboarded_v8_df.copy()
    )
    offboarded_keys["InOffboardedV8"] = True

    combined_source_keys = (
        im_doc_active_offboarded_v8
        .merge(
            active_keys,
            on=[
                "docnum",
                "version",
            ],
            how="left"
        )
        .merge(
            offboarded_keys,
            on=[
                "docnum",
                "version",
            ],
            how="left"
        )
    )

    combined_source_keys[
        "InActive"
    ] = (
        combined_source_keys["InActive"]
        .fillna(False)
        .astype(bool)
    )

    combined_source_keys[
        "InOffboardedV8"
    ] = (
        combined_source_keys["InOffboardedV8"]
        .fillna(False)
        .astype(bool)
    )

    # --------------------------------------------------------
    # Full comparison
    # --------------------------------------------------------

    comparison_df = im_doc_df.merge(
        combined_source_keys,
        on=[
            "docnum",
            "version",
        ],
        how="outer",
        indicator=True
    )

    comparison_df[
        "InFinalInScope"
    ] = comparison_df["_merge"].isin(
        [
            "both",
            "left_only",
        ]
    )

    comparison_df[
        "InActiveOffboardedV8"
    ] = comparison_df["_merge"].isin(
        [
            "both",
            "right_only",
        ]
    )

    comparison_df[
        "GapStatus"
    ] = comparison_df["_merge"].map(
        {
            "both": "MATCH",
            "left_only":
                "MISSING_FROM_ACTIVE_OFFBOARDED_V8",
            "right_only":
                "MISSING_FROM_FINAL_IN_SCOPE",
        }
    )

    comparison_df[
        "HasGap"
    ] = comparison_df[
        "GapStatus"
    ].ne("MATCH")

    comparison_df = comparison_df[
        [
            "docnum",
            "version",
            "InFinalInScope",
            "InActiveOffboardedV8",
            "InActive",
            "InOffboardedV8",
            "GapStatus",
            "HasGap",
        ]
    ].sort_values(
        by=[
            "HasGap",
            "docnum",
            "version",
        ],
        ascending=[
            False,
            True,
            True,
        ],
        na_position="last"
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Calculate summary
    # --------------------------------------------------------

    final_key_count = len(
        im_doc_df
    )

    combined_key_count = len(
        im_doc_active_offboarded_v8
    )

    matched_count = int(
        comparison_df[
            "GapStatus"
        ].eq("MATCH").sum()
    )

    missing_from_active_offboarded_count = int(
        comparison_df[
            "GapStatus"
        ].eq(
            "MISSING_FROM_ACTIVE_OFFBOARDED_V8"
        ).sum()
    )

    missing_from_final_count = int(
        comparison_df[
            "GapStatus"
        ].eq(
            "MISSING_FROM_FINAL_IN_SCOPE"
        ).sum()
    )

    total_gap_count = (
        missing_from_active_offboarded_count
        + missing_from_final_count
    )

    status = (
        "PASS"
        if total_gap_count == 0
        else "FAIL"
    )

    notes_parts = [
        (
            "Compared distinct docnum/version keys from "
            "in_scope_im_doc_final.csv against the combined "
            "active and offboarded V8 files."
        ),
        f"FinalInScopeKeys={final_key_count}",
        (
            "ActiveOffboardedV8Keys="
            f"{combined_key_count}"
        ),
        f"MatchedKeys={matched_count}",
        (
            "MissingFromActiveOffboardedV8="
            f"{missing_from_active_offboarded_count}"
        ),
        (
            "MissingFromFinalInScope="
            f"{missing_from_final_count}"
        ),
        f"ActiveFilesLoaded={len(active_loaded_files)}",
        (
            "OffboardedV8FilesLoaded="
            f"{len(offboarded_loaded_files)}"
        ),
    ]

    if skipped_file_messages:
        notes_parts.append(
            "SkippedFiles="
            f"{len(skipped_file_messages)}"
        )

    notes = "; ".join(
        notes_parts
    )

    # --------------------------------------------------------
    # Save full comparison
    # --------------------------------------------------------

    comparison_df.to_csv(
        comparison_file_path,
        index=False,
        encoding="utf-8-sig"
    )

    # Prefer gap rows for the sample. If there are no gaps,
    # save matched rows to demonstrate the successful check.
    gap_df = comparison_df[
        comparison_df["HasGap"]
    ]

    if not gap_df.empty:
        sample_df = gap_df.head(100)
    else:
        sample_df = comparison_df.head(100)

    sample_df.insert(
        0,
        "SourceFile",
        comparison_file_name
    )

    sample_df.to_csv(
        sample_file_path,
        index=False,
        encoding="utf-8-sig"
    )

    log_write(
        log_file,
        f"Final in-scope distinct keys: {final_key_count:,}"
    )

    log_write(
        log_file,
        (
            "Active/offboarded V8 distinct keys: "
            f"{combined_key_count:,}"
        )
    )

    log_write(
        log_file,
        f"Matched keys: {matched_count:,}"
    )

    log_write(
        log_file,
        (
            "Missing from active/offboarded V8: "
            f"{missing_from_active_offboarded_count:,}"
        )
    )

    log_write(
        log_file,
        (
            "Missing from final in-scope: "
            f"{missing_from_final_count:,}"
        )
    )

    log_write(
        log_file,
        f"Validation status: {status}"
    )

    log_write(
        log_file,
        f"Saved: {comparison_file_path}"
    )

    log_write(
        log_file,
        f"Saved: {sample_file_path}"
    )

    # --------------------------------------------------------
    # Store useful dataframes in context
    # --------------------------------------------------------

    context[
        "step14_im_doc_df"
    ] = im_doc_df

    context[
        "step14_im_doc_active_df"
    ] = im_doc_active_df

    context[
        "step14_im_doc_offboarded_v8_df"
    ] = im_doc_offboarded_v8_df

    context[
        "step14_im_doc_active_offboarded_v8"
    ] = im_doc_active_offboarded_v8

    context[
        "step14_comparison_df"
    ] = comparison_df

    # --------------------------------------------------------
    # Add validation log row
    # --------------------------------------------------------

    add_validation_log_row_from_df(
        step_name=step_name,
        file_name=comparison_file_name,
        start_time=step_start,
        end_time=datetime.now(),
        df=comparison_df,
        expected_rows=final_key_count,
        actual_rows=matched_count,
        difference=total_gap_count,
        status=status,
        notes=notes,
    )

    return context
# ============================================================
# Save Outputs
# ============================================================

def save_validation_logs():
    """
    Save validation_log.csv and append a readable summary to validation_log.txt.
    """

    if not VALIDATION_LOG_ROWS:
        print(
            "No validation log rows generated."
        )
        return

    log_df = pd.DataFrame(
        VALIDATION_LOG_ROWS
    )

    for col in VALIDATION_COLUMNS:
        if col not in log_df.columns:
            log_df[col] = ""

    log_df = log_df[
        VALIDATION_COLUMNS
    ]

    log_df.to_csv(
        VALIDATION_LOG_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    with open(
        VALIDATION_LOG_TXT,
        "a",
        encoding="utf-8"
    ) as f:
        f.write("\n")
        f.write("=" * 100)
        f.write("\n")
        f.write("VALIDATION LOG SUMMARY")
        f.write("\n")
        f.write("=" * 100)
        f.write("\n\n")

        for _, row in log_df.iterrows():
            f.write("=" * 100)
            f.write("\n")

            for col in VALIDATION_COLUMNS:
                f.write(
                    f"{col}: {row[col]}\n"
                )

            f.write("\n")


def save_outputs():
    """
    Public save function called by main.py.
    """

    save_validation_logs()

    print(
        f"\nSaved: {VALIDATION_LOG_CSV}"
    )

    print(
        f"Saved: {VALIDATION_LOG_TXT}"
    )

    print(
        "\nValidation Completed"
    )


# ============================================================
# Standalone Validation Runner
# ============================================================

def main():
    """
    Run validation only.
    This does not run pipeline processing.
    """

    reset_validation_outputs()

    log_file = VALIDATION_LOG_TXT

    context = {}

    print("\nRunning Step 01 Validation")
    context.update(
        validate_step_01_extract(
            context,
            log_file
        )
    )

    print("\nRunning Step 02 Validation")
    context.update(
        validate_step_02_document_match(
            context,
            log_file
        )
    )

    print("\nRunning Step 03 Validation")
    context.update(
        validate_step_03_client_match(
            context,
            log_file
        )
    )

    print("\nRunning Step 04 Validation")
    context.update(
        validate_step_04_final_fen(
            context,
            log_file
        )
    )

    print("\nRunning Step 05 Validation")
    context.update(
        validate_step_05_final_im(
            context,
            log_file
        )
    )

    print("\nRunning Step 06 Validation")
    context.update(
        validate_step_06_entity_scope_filter(
            context,
            log_file
        )
    )

    print("\nRunning Step 10 Validation")
    context.update(
        validate_step_10_scoping(
            context,
            log_file
        )
    )

    save_outputs()

    print(
        f"\nValidation Folder:\n{VALIDATION_FOLDER}"
    )


if __name__ == "__main__":
    main()