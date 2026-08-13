from __future__ import annotations

import glob
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd


from _13_util._scope_common import (
    ACTIVE_STATUSES,
    OFFBOARDED_STATUS,
    OUTPUT_PATH,
    SCOPE_PATH,
    TEMP_PATH,
    append_scope_summary,
    ensure_scope_dirs,
    is_one
)


DATA_TYPE = "fen_doc"

SOURCE_FILE = OUTPUT_PATH / "final_fen_to_im.csv"
DOC_SCOPE_XLSX = SCOPE_PATH / "02_fen_doc_scope.xlsx"
SQLITE_DEDUP_DB = SCOPE_PATH / "02_fen_doc_scope_dedup.sqlite"

# Source read size.
SOURCE_CHUNK_SIZE = 25000

# Each output CSV file will contain up to this many rows.
# Example:
#   fen_doc_offboarded_0001.csv
#   fen_doc_offboarded_0002.csv
CSV_BATCH_SIZE = 1000000

# Excel hard row limit per sheet, including header.

EXPORT_EXCEL = True
MAX_EXCEL_EXPORT_ROWS = 100000

OUTPUT_COLUMNS = [
    "LegalEntityId",
    "ReferenceId",
    "isClientEntity",
    "RefClientID",
    "im_docnum",
    "im_version",
    "im_docloc",
    "im_docsize",
    "im_c1alias",
    "im_t_alias",
    "DocMatchedBy",
    "DocMatchBoolean",
    "ExhaustedRoleStatus",
    "GroupedRoleType",
    
]

BASE_REQUIRED_COLUMNS = [
    "LegalEntityId",
    "ExhaustedRoleStatus",
    "DocMatchBoolean",
]

OFFBOARDED_COLUMN_CANDIDATES = [
    "isOffboarded",
    "IsOffboarded",
]




def build_excel_from_csv_batches() -> None:

    dataset_mapping = [
        (
            "doc_offboarded_v7",
            "fen_doc_offboarded_v7",
        ),
        (
            "doc_offboarded",
            "fen_doc_offboarded",
        ),
        (
            "doc_offboarded_v8",
            "fen_doc_offboarded_v8",
        ),
        (
            "doc_active_entity",
            "fen_doc_active_entity",
        ),
        (
            "doc_other_status_entity",
            "fen_doc_other_status_entity",
        ),
    ]

    with pd.ExcelWriter(
        DOC_SCOPE_XLSX,
        engine="xlsxwriter",
    ) as writer:

        for (
            sheet_name,
            csv_prefix,
        ) in dataset_mapping:

            current_row = 0

            files = sorted(
                SCOPE_PATH.glob(
                    f"{csv_prefix}_*.csv"
                )
            )

            for file in files:

                if current_row >= MAX_EXCEL_EXPORT_ROWS:
                    break

                for chunk in pd.read_csv(
                    file,
                    chunksize=5000,
                    dtype=str,
                    keep_default_na=False,
                ):

                    if current_row >= MAX_EXCEL_EXPORT_ROWS:
                        break

                    remaining = (
                        MAX_EXCEL_EXPORT_ROWS
                        - current_row
                    )

                    chunk = chunk.head(
                        remaining
                    )

                    chunk.to_excel(
                        writer,
                        sheet_name=sheet_name,
                        startrow=current_row,
                        header=(current_row == 0),
                        index=False,
                    )

                    current_row += len(chunk)

            log(
                f"{sheet_name}: "
                f"{current_row:,} rows exported"
            )


def log(message: str) -> None:
    """
    Print progress immediately.

    This makes it much easier to know where the script is when it runs
    for a long time or fails.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {message}", flush=True)


def normalize_series(s: pd.Series) -> pd.Series:
    """
    Normalize values used for matching.

    Output values are not changed. This is only for matching/filtering.
    """
    return s.astype("string").fillna("").str.strip()


def get_source_header() -> list:
    """
    Read only the CSV header.

    This avoids loading the full source file just to validate columns.
    """
    return list(pd.read_csv(SOURCE_FILE, nrows=0).columns)


def get_offboarded_column_from_header(columns: list[str]) -> str:
    for col in OFFBOARDED_COLUMN_CANDIDATES:
        if col in columns:
            return col

    raise ValueError(
        f"{SOURCE_FILE} must contain either "
        "'isOffboarded' or 'IsOffboarded'."
    )


def validate_source_columns() -> str:
    """
    Validate the source CSV has every required column.

    Returns the actual offboarded column name found in the source.
    """
    columns = get_source_header()
    offboarded_col = get_offboarded_column_from_header(columns)

    required = list(
        dict.fromkeys(
            OUTPUT_COLUMNS
            + BASE_REQUIRED_COLUMNS
            + [offboarded_col]
        )
    )

    missing = [col for col in required if col not in columns]

    if missing:
        raise ValueError(
            f"{SOURCE_FILE} is missing required columns: {missing}"
        )

    return offboarded_col


def load_client_scope_ids(csv_name: str) -> set:
    """
    Load LegalEntityId values from a client scope CSV.

    This reads the scope file in chunks too, to avoid unnecessary memory use.
    The resulting set is usually much smaller than the main document file.
    """
    path = SCOPE_PATH / csv_name

    log(f"Loading LegalEntityId values from {path}")

    # Validate required column using existing utility.
    # This reads the file, but scope files are usually much smaller than source.
    # If even scope files are huge, replace this with header-only validation.
    header = pd.read_csv(
        path,
        nrows=0,
    )

    if "LegalEntityId" not in header.columns:
        raise ValueError(
            f"{path} missing LegalEntityId"
        )

    ids: set[str] = set()

    for chunk_no, chunk in enumerate(
        pd.read_csv(
            path,
            usecols=["LegalEntityId"],
            dtype=str,
            chunksize=SOURCE_CHUNK_SIZE,
            keep_default_na=False,
            low_memory=False,
        ),
        start=1,
    ):
        values = normalize_series(chunk["LegalEntityId"])
        values = values[values.ne("")]

        ids.update(values.tolist())

        log(
            f"{csv_name}: loaded scope chunk {chunk_no:,}, "
            f"current unique ids {len(ids):,}"
        )

    log(f"{csv_name}: finished loading {len(ids):,} unique LegalEntityId values")

    return ids


def remove_old_csv_batches(csv_name: str) -> None:
    """
    Remove old batch files from previous runs.

    Example:
      fen_doc_offboarded.csv

    Removes:
      fen_doc_offboarded_0001.csv
      fen_doc_offboarded_0002.csv
      ...
    """
    stem = Path(csv_name).stem
    pattern = str(SCOPE_PATH / f"{stem}_*.csv")

    old_files = glob.glob(pattern)

    if old_files:
        log(f"Removing {len(old_files):,} old batch file(s) for {stem}")

    for file_name in old_files:
        Path(file_name).unlink(missing_ok=True)


def make_row_key(df: pd.DataFrame) -> pd.Series:
    """
    Build a stable row key for output-level dedupe.

    This replaces a full-dataset drop_duplicates() call.
    The separator is a non-printable unit separator to reduce accidental clashes.
    """
    return (
        df[OUTPUT_COLUMNS]
        .fillna("")
        .astype(str)
        .agg("\x1f".join, axis=1)
    )



class DedupStore:
    """
    Disk-backed dedupe and distinct counting.

    This avoids holding these in Python memory:
      1. all output row keys
      2. all distinct LegalEntityId values
      3. all distinct im_docnum values
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

        if self.db_path.exists():
            self.db_path.unlink()

        self.conn = sqlite3.connect(self.db_path)

        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self.conn.execute("PRAGMA temp_store = FILE")

        self.conn.execute(
            """
            CREATE TABLE output_row_dedup (
                dataset_name TEXT NOT NULL,
                row_key TEXT NOT NULL,
                PRIMARY KEY (dataset_name, row_key)
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE distinct_clients (
                dataset_name TEXT NOT NULL,
                LegalEntityId TEXT NOT NULL,
                PRIMARY KEY (dataset_name, LegalEntityId)
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE distinct_docs (
                dataset_name TEXT NOT NULL,
                im_docnum TEXT NOT NULL,
                PRIMARY KEY (dataset_name, im_docnum)
            )
            """
        )

        self.conn.commit()

    def filter_new_rows(
        self,
        dataset_name: str,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Return only rows not already written for this dataset.

        Dedupe is exact across OUTPUT_COLUMNS.
        """
        if df.empty:
            return df

        df = df[OUTPUT_COLUMNS].copy()
        df = df.drop_duplicates().reset_index(drop=True)

        row_keys = make_row_key(df)

        keep_positions: list[int] = []

        cur = self.conn.cursor()
        cur.execute("BEGIN")

        for pos, row_key in enumerate(row_keys):
            cur.execute(
                """
                INSERT OR IGNORE INTO output_row_dedup
                (dataset_name, row_key)
                VALUES (?, ?)
                """,
                (dataset_name, row_key),
            )

            if cur.rowcount == 1:
                keep_positions.append(pos)

        self.conn.commit()

        if not keep_positions:
            return df.iloc[0:0].copy()

        return df.iloc[keep_positions].reset_index(drop=True)

    def add_summary_values(
        self,
        dataset_name: str,
        df: pd.DataFrame,
    ) -> None:
        """
        Store distinct LegalEntityId and im_docnum values on disk.
        """
        if df.empty:
            return

        client_values = (
            normalize_series(df["LegalEntityId"])
            .loc[lambda x: x.ne("")]
            .drop_duplicates()
            .tolist()
        )

        doc_values = (
            normalize_series(df["im_docnum"])
            .loc[lambda x: x.ne("")]
            .drop_duplicates()
            .tolist()
        )

        cur = self.conn.cursor()
        cur.execute("BEGIN")

        cur.executemany(
            """
            INSERT OR IGNORE INTO distinct_clients
            (dataset_name, LegalEntityId)
            VALUES (?, ?)
            """,
            [(dataset_name, value) for value in client_values],
        )

        cur.executemany(
            """
            INSERT OR IGNORE INTO distinct_docs
            (dataset_name, im_docnum)
            VALUES (?, ?)
            """,
            [(dataset_name, value) for value in doc_values],
        )

        self.conn.commit()

    def count_distinct_clients(self, dataset_name: str) -> int:
        cur = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM distinct_clients
            WHERE dataset_name = ?
            """,
            (dataset_name,),
        )
        return int(cur.fetchone()[0])

    def count_distinct_docs(self, dataset_name: str) -> int:
        cur = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM distinct_docs
            WHERE dataset_name = ?
            """,
            (dataset_name,),
        )
        return int(cur.fetchone()[0])

    def close(self) -> None:
        self.conn.close()


@dataclass
class DatasetConfig:
    dataset_name: str
    csv_name: str
    sheet_name: str
    predicate: Callable[[pd.DataFrame], pd.Series]


class DatasetWriter:

    def __init__(
        self,
        config: DatasetConfig,
    ) -> None:

        self.config = config

        self.csv_stem = Path(
            config.csv_name
        ).stem

        self.csv_batch_no = 1

        self.csv_batch_row_count = 0

        self.total_rows_written = 0

        remove_old_csv_batches(
            config.csv_name
        )

    def current_csv_path(self) -> Path:

        return (
            SCOPE_PATH
            / f"{self.csv_stem}_{self.csv_batch_no:04d}.csv"
        )

    def write(
        self,
        df: pd.DataFrame,
    ) -> int:

        if df.empty:
            return 0

        df = df[OUTPUT_COLUMNS]

        rows_remaining = len(df)

        start = 0

        while rows_remaining > 0:

            capacity = (
                CSV_BATCH_SIZE
                - self.csv_batch_row_count
            )

            take = min(
                capacity,
                rows_remaining,
            )

            part = df.iloc[
                start:start + take
            ]

            csv_path = (
                self.current_csv_path()
            )

            write_header = (
                self.csv_batch_row_count == 0
            )

            part.to_csv(
                csv_path,
                mode="a",
                index=False,
                header=write_header,
                encoding="utf-8-sig",
            )

            self.csv_batch_row_count += take

            self.total_rows_written += take

            start += take

            rows_remaining -= take

            if (
                self.csv_batch_row_count
                >= CSV_BATCH_SIZE
            ):
                log(
                    f"{self.config.dataset_name}: "
                    f"completed CSV batch "
                    f"{self.csv_batch_no:04d}"
                )

                self.csv_batch_no += 1

                self.csv_batch_row_count = 0

        return len(df)

def iter_doc_source_chunks(
    offboarded_col: str,
) -> pd.io.parsers.TextFileReader:
    """
    Read only required columns as strings.

    dtype=str helps avoid mixed-type inference and keeps identifiers stable.
    chunksize keeps memory bounded.
    """
    usecols = list(
        dict.fromkeys(
            OUTPUT_COLUMNS
            + BASE_REQUIRED_COLUMNS
            + [offboarded_col]
        )
    )

    return pd.read_csv(
        SOURCE_FILE,
        usecols=usecols,
        dtype=str,
        chunksize=SOURCE_CHUNK_SIZE,
        keep_default_na=False,
        low_memory=False,
    )


def process_fen_doc_scope() -> None:
    ensure_scope_dirs()

    log("Starting fen_doc scope build")
    log(f"Source file: {SOURCE_FILE}")
    log(f"Source chunk size: {SOURCE_CHUNK_SIZE:,}")
    log(f"CSV batch size: {CSV_BATCH_SIZE:,}")
    log(f"Excel output: {DOC_SCOPE_XLSX}")

    offboarded_col = validate_source_columns()
    log(f"Using offboarded column: {offboarded_col}")

    ids_offboarded_v7 = load_client_scope_ids("client_offboarded_v7.csv")
    ids_offboarded_v8 = load_client_scope_ids("client_offboarded_v8.csv")

    active_statuses = {str(x).strip() for x in ACTIVE_STATUSES}
    offboarded_status = str(OFFBOARDED_STATUS).strip()

    excluded_statuses = set(active_statuses)
    excluded_statuses.add(offboarded_status)

    configs = [
        DatasetConfig(
            dataset_name="doc_offboarded_v7",
            csv_name="fen_doc_offboarded_v7.csv",
            sheet_name="doc_offboarded_v7",
            predicate=lambda df: df["_LegalEntityId_norm"].isin(ids_offboarded_v7),
        ),
        DatasetConfig(
            dataset_name="doc_offboarded",
            csv_name="fen_doc_offboarded.csv",
            sheet_name="doc_offboarded",
            predicate=lambda df: is_one(df[offboarded_col]),
        ),
        DatasetConfig(
            dataset_name="doc_offboarded_v8",
            csv_name="fen_doc_offboarded_v8.csv",
            sheet_name="doc_offboarded_v8",
            predicate=lambda df: df["_LegalEntityId_norm"].isin(ids_offboarded_v8),
        ),
        DatasetConfig(
            dataset_name="doc_active_entity",
            csv_name="fen_doc_active_entity.csv",
            sheet_name="doc_active_entity",
            predicate=lambda df: df["_ExhaustedRoleStatus_norm"].isin(active_statuses),
        ),
        DatasetConfig(
            dataset_name="doc_other_status_entity",
            csv_name="fen_doc_other_status_entity.csv",
            sheet_name="doc_other_status_entity",
            predicate=lambda df: ~df["_ExhaustedRoleStatus_norm"].isin(excluded_statuses),
        ),
    ]

    dedup = DedupStore(SQLITE_DEDUP_DB)



    writers = {
        cfg.dataset_name: DatasetWriter(cfg)
        for cfg in configs
    }

    total_source_rows = 0
    total_matched_rows = 0

    try:
        for chunk_no, chunk in enumerate(
            iter_doc_source_chunks(offboarded_col),
            start=1,
        ):
            source_rows = len(chunk)
            total_source_rows += source_rows

            log(
                f"Reading source chunk {chunk_no:,}: "
                f"{source_rows:,} rows "
                f"(total source rows read: {total_source_rows:,})"
            )

            matched_mask = is_one(chunk["DocMatchBoolean"])
            chunk = chunk.loc[matched_mask].copy()

            matched_rows = len(chunk)
            total_matched_rows += matched_rows

            log(
                f"Source chunk {chunk_no:,}: "
                f"{matched_rows:,} doc-matched rows "
                f"(total matched rows: {total_matched_rows:,})"
            )

            if chunk.empty:
                continue

            chunk["_LegalEntityId_norm"] = normalize_series(chunk["LegalEntityId"])
            chunk["_ExhaustedRoleStatus_norm"] = normalize_series(chunk["ExhaustedRoleStatus"])

            for cfg in configs:
                mask = cfg.predicate(chunk)
                df_scope = chunk.loc[mask, OUTPUT_COLUMNS]

                if df_scope.empty:
                    log(
                        f"{cfg.dataset_name}: chunk {chunk_no:,}, "
                        "0 matching rows"
                    )
                    continue

                df_new = dedup.filter_new_rows(
                    dataset_name=cfg.dataset_name,
                    df=df_scope,
                )

                if df_new.empty:
                    log(
                        f"{cfg.dataset_name}: chunk {chunk_no:,}, "
                        f"{len(df_scope):,} matching rows, "
                        "0 new rows after dedupe"
                    )
                    continue

                dedup.add_summary_values(
                    dataset_name=cfg.dataset_name,
                    df=df_new,
                )

                written = writers[cfg.dataset_name].write(df_new)

                log(
                    f"{cfg.dataset_name}: chunk {chunk_no:,}, "
                    f"matching rows {len(df_scope):,}, "
                    f"new rows written {written:,}, "
                    f"total written {writers[cfg.dataset_name].total_rows_written:,}"
                )

        log(f"Saving Excel workbook: {DOC_SCOPE_XLSX}")
        if EXPORT_EXCEL:
            build_excel_from_csv_batches()

        log("Appending scope summaries")

        for cfg in configs:
            writer = writers[cfg.dataset_name]

            total_client_cnt = dedup.count_distinct_clients(cfg.dataset_name)
            total_doc_count = dedup.count_distinct_docs(cfg.dataset_name)

            append_scope_summary(
                data_type=DATA_TYPE,
                data_source=f"{Path(cfg.csv_name).stem}_*.csv",
                total_client_cnt=total_client_cnt,
                total_doc_count=total_doc_count,
            )

            log(
                f"{cfg.dataset_name}: completed. "
                f"rows written {writer.total_rows_written:,}, "
                f"distinct clients {total_client_cnt:,}, "
                f"distinct docs {total_doc_count:,}"
            )

        log("fen_doc scope build completed successfully")

    finally:
        dedup.close()

        if SQLITE_DEDUP_DB.exists():
            SQLITE_DEDUP_DB.unlink(
                missing_ok=True
            )


def main() -> None:
    process_fen_doc_scope()


def run_unit_tests() -> None:
    """
    Lightweight unit test for core filtering behavior.

    This does not test file output.
    """
    df = pd.DataFrame(
        {
            "DocMatchBoolean": [1, 0, "1", "N"],
            "ExhaustedRoleStatus": [
                "Active",
                "Offboarded",
                "Acitve",
                "Other",
            ],
            "LegalEntityId": ["A", "B", "C", "D"],
            "isOffboarded": [0, 1, 0, 0],
            "ReferenceId": ["R1", "R2", "R3", "R4"],
            "isClientEntity": ["Y", "Y", "Y", "Y"],
            "RefClientID": ["C1", "C2", "C3", "C4"],
            "im_docnum": ["D1", "D2", "D3", "D4"],
            "im_docloc": ["L1", "L2", "L3", "L4"],
            "im_docsize": ["10", "20", "30", "40"],
            "im_c1alias": ["A1", "A2", "A3", "A4"],
            "im_t_alias": ["T1", "T2", "T3", "T4"],
            "DocMatchedBy": ["M1", "M2", "M3", "M4"],
        }
    )

    matched = df[is_one(df["DocMatchBoolean"])]

    assert len(matched) == 2

    active_statuses = {str(x).strip() for x in ACTIVE_STATUSES}

    active = matched[
        normalize_series(matched["ExhaustedRoleStatus"]).isin(active_statuses)
    ]

    assert len(active) == 2

    log("_12_fen_doc_scope unit tests passed.")


if __name__ == "__main__":
    # run_unit_tests()
    main()