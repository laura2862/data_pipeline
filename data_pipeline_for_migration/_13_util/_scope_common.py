from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable, Optional
from datetime import datetime
import pandas as pd

from _01_config.settings import (
    TEMP_FOLDER,
    OUTPUT_FOLDER,
    SCOPE_FOLDER,
    UNSUPPORTED_DOC_TYPES,
)

from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv, save_to_xlsx


TEMP_PATH = Path(TEMP_FOLDER)
OUTPUT_PATH = Path(OUTPUT_FOLDER)
SCOPE_PATH = Path(SCOPE_FOLDER)

SUMMARY_FILE = SCOPE_PATH / "01_scope_summary.csv"

SUMMARY_COLUMNS = [
    "date",
    "start_time",
    "end_time",
    "duration",
    "dataType",
    "dataSource",
    "totalClientCnt",
    "totalDocCount",
]

ACTIVE_STATUSES = {"Active", "Acitve"}
OFFBOARDED_STATUS = "Offboarded"


def ensure_scope_dirs() -> None:
    TEMP_PATH.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    SCOPE_PATH.mkdir(parents=True, exist_ok=True)


def require_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
    source_name: str,
) -> None:
    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{source_name} is missing required columns: {missing}"
        )


def load_csv_required(
    path: Path,
    required_columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Required file does not exist: {path}"
        )

    df = load_csv(path)

    if required_columns:
        require_columns(df, required_columns, str(path))

    return df


def dedupe_column(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:
    require_columns(df, [column], "dedupe input")

    return (
        df[[column]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )


def normalize_text_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip()


def is_one(series: pd.Series) -> pd.Series:
    return (
        normalize_text_series(series)
        .str.lower()
        .isin({"1", "1.0", "true", "y", "yes"})
    )


def is_zero(series: pd.Series) -> pd.Series:
    return (
        normalize_text_series(series)
        .str.lower()
        .isin({"0", "0.0", "false", "n", "no"})
    )


def distinct_count(
    df: pd.DataFrame,
    column: str,
) -> int:
    if column not in df.columns:
        return 0

    return int(df[column].dropna().nunique())


def anti_join_by_column(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:
    require_columns(left_df, [column], "left dataframe")
    require_columns(right_df, [column], "right dataframe")

    right_values = set(
        right_df[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    mask = ~(
        left_df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .isin(right_values)
    )

    return (
        left_df[mask]
        .drop_duplicates()
        .reset_index(drop=True)
    )


def append_scope_summary(
    data_type,
    data_source,
    total_client_cnt,
    total_doc_count=None,
    start_time=None,
    end_time=None,
)-> None:
    """
    Append one summary record into SCOPE_FOLDER/01_scope_summary.csv.

    This uses the existing save_to_csv() utility instead of doing a raw
    append, so the write remains atomic and consistent with the project.
    """
    ensure_scope_dirs()
    if end_time is None:
            end_time = datetime.now()
    
    if start_time is None:
        start_time = end_time
    duration = (
        end_time - start_time
    ).total_seconds()

    new_row = pd.DataFrame(
        [
            {
                "date": start_time.strftime("%Y-%m-%d"),
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": duration,
                "dataType": data_type,
                "dataSource": data_source,
                "totalClientCnt": total_client_cnt,
                "totalDocCount": total_doc_count,
            }
        ],
        columns=SUMMARY_COLUMNS,
    )


    if SUMMARY_FILE.exists():
        existing = load_csv(SUMMARY_FILE)

        for col in SUMMARY_COLUMNS:
            if col not in existing.columns:
                existing[col] = None

        existing = existing[SUMMARY_COLUMNS]
        output = pd.concat(
            [existing, new_row],
            ignore_index=True,
        )
    else:
        output = new_row

    save_to_csv(output, SUMMARY_FILE)







def save_scope_csv_and_xlsx(
    df: pd.DataFrame,
    csv_path: Path,
    xlsx_path: Path,
    sheet_name: str,
) -> None:
    ensure_scope_dirs()
    save_to_csv(df, csv_path)
    save_to_xlsx(df, xlsx_path, sheet_name)


def get_unsupported_doc_type_set() -> set[str]:
    return {
        str(value).strip().upper()
        for value in UNSUPPORTED_DOC_TYPES
    }


def is_supported_doc_type(series: pd.Series) -> pd.Series:
    unsupported = get_unsupported_doc_type_set()

    return ~(
        normalize_text_series(series)
        .str.upper()
        .isin(unsupported)
    )


def is_unsupported_doc_type(series: pd.Series) -> pd.Series:
    unsupported = get_unsupported_doc_type_set()

    return (
        normalize_text_series(series)
        .str.upper()
        .isin(unsupported)
    )


def Is_HIPAA_yes(series: pd.Series) -> pd.Series:
    return (
        normalize_text_series(series)
        .str.upper()
        .eq("Y")
    )


def Is_HIPAA_no(series: pd.Series) -> pd.Series:
    return (
        normalize_text_series(series)
        .str.upper()
        .eq("N")
    )


def run_common_unit_tests() -> None:
    df_left = pd.DataFrame(
        {
            "LegalEntityId": ["1", "2", "3", "3"]
        }
    )

    df_right = pd.DataFrame(
        {
            "LegalEntityId": ["2"]
        }
    )

    result = anti_join_by_column(
        df_left,
        df_right,
        "LegalEntityId",
    )

    assert set(result["LegalEntityId"]) == {"1", "3"}

    s = pd.Series(["1", "true", "Y", "0", "false", "N"])
    assert is_one(s).tolist() == [
        True,
        True,
        True,
        False,
        False,
        False,
    ]

    assert is_zero(s).tolist() == [
        False,
        False,
        False,
        True,
        True,
        True,
    ]

    print("util._scope_common unit tests passed.")


if __name__ == "__main__":
    run_common_unit_tests()