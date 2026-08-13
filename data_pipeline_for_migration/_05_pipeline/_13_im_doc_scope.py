from __future__ import annotations

import glob
import sqlite3
import sys
import time
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
    Is_HIPAA_no,
    Is_HIPAA_yes,
    is_one,
    is_supported_doc_type,
    is_unsupported_doc_type,
    is_zero,
)


DATA_TYPE = "im_doc"

SOURCE_FILE = OUTPUT_PATH / "final_im_to_fen.csv"
IM_ALL_VERSION_FILE = TEMP_PATH / "im_doc.csv"
IM_DOC_SCOPE_XLSX = SCOPE_PATH / "03_im_doc_scope.xlsx"
SQLITE_DEDUP_DB = SCOPE_PATH / "03_im_doc_scope_dedup.sqlite"

SOURCE_CHUNK_SIZE = 25000
CSV_BATCH_SIZE = 500000

EXPORT_EXCEL = True
MAX_EXCEL_EXPORT_ROWS = 100000

OUTPUT_COLUMNS = [
    "fen_LegalEntityId",
    "fen_ReferenceId",
    "fen_isClientEntity",
    "RefClientID",
    "docnum",
    "version",
    "docloc",
    "docsize",
    "c1alias",
    "t_alias",
    "DocMatchedBy",
    "DocMatchBoolean",
    "fen_ExhaustedRoleStatus",
    "fen_GroupedRoleType",
]

BASE_REQUIRED_COLUMNS = OUTPUT_COLUMNS + [
    "Is_HIPAA",
    "fen_IsOffboarded",
    "fen_ExhaustedRoleStatus",
    "ClientMatchBoolean",
    "version",
]

dataset_mapping = [
    (
        "doc_offboarded_v7",
        "im_doc_offboarded_v7",
    ),
    (
        "doc_offboarded",
        "im_doc_offboarded",
    ),
    (
        "doc_offboarded_v8",
        "im_doc_offboarded_v8",
    ),
    (
        "doc_active_entity",
        "im_doc_active_entity",
    ),
    (
        "doc_other_status",
        "im_doc_other_status_entity",
    ),
    (
        "im_all_version",
        "im_doc_all_version",
    ),
    (
        "orphaned_supported_insecure",
        "im_doc_orphaned_supported_insecure",
    ),
    (
        "unsupported_insecure",
        "im_doc_unsupported_insecure",
    ),
    (
        "doc_secure",
        "im_doc_secure",
    ),
]

def log(message: str) -> None:
    """
    Print progress immediately so long-running jobs show exactly where they are.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {message}", flush=True)


def normalize_series(s: pd.Series) -> pd.Series:
    """
    Normalize values for matching only.

    Original output values are not changed.
    """
    return s.astype("string").fillna("").str.strip()


def get_csv_header(path: Path) -> list:
    """
    Read only the CSV header.
    """
    return list(pd.read_csv(path, nrows=0).columns)


def validate_required_columns(
    path: Path,
    required_columns: list[str],
) -> None:
    """
    Validate required columns without loading the full CSV.
    """
    columns = get_csv_header(path)

    missing = [
        col for col in required_columns
        if col not in columns
    ]

    if missing:
        raise ValueError(
            f"{path} is missing required columns: {missing}"
        )


def validate_source_columns() -> None:
    """
    Validate source columns without loading the full source file.
    """
    validate_required_columns(
        path=SOURCE_FILE,
        required_columns=BASE_REQUIRED_COLUMNS,
    )


def validate_all_version_columns() -> None:
    """
    Validate all version file columns without loading the full file.
    """
    validate_required_columns(
        path=IM_ALL_VERSION_FILE,
        required_columns=["docnum", "version"],
    )


def make_pair_key(
    left: pd.Series,
    right: pd.Series,
) -> pd.Series:
    """
    Build a normalized two-column key for joins without doing a large merge.

    Used for:
      docnum + version
    """
    return (
        normalize_series(left)
        + "\x1f"
        + normalize_series(right)
    )


def load_client_scope_ids(csv_name: str) -> set:
    """
    Load LegalEntityId values from a client scope CSV in chunks.

    This avoids loading scope files fully into memory.
    The resulting set is usually much smaller than the main source file.
    """
    path = SCOPE_PATH / csv_name

    log(f"Loading LegalEntityId values from {path}")

    validate_required_columns(
        path=path,
        required_columns=["LegalEntityId"],
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

        if chunk_no % 10 == 0:
            log(
                f"{csv_name}: loaded chunk {chunk_no:,}, "
                f"unique ids {len(ids):,}"
            )
    log(
        f"{csv_name}: finished loading "
        f"{len(ids):,} unique LegalEntityId values"
    )

    return ids


def load_all_version_keys() -> set:
    """
    Load docnum + version keys from the all version file in chunks.

    This replaces a full DataFrame merge with a memory-light set lookup.
    """
    log(f"Loading all version keys from {IM_ALL_VERSION_FILE}")

    validate_all_version_columns()

    keys: set[str] = set()

    for chunk_no, chunk in enumerate(
        pd.read_csv(
            IM_ALL_VERSION_FILE,
            usecols=["docnum", "version"],
            dtype=str,
            chunksize=SOURCE_CHUNK_SIZE,
            keep_default_na=False,
            low_memory=False,
        ),
        start=1,
    ):
        pair_keys = make_pair_key(
            chunk["docnum"],
            chunk["version"],
        )

        pair_keys = pair_keys[pair_keys.ne("\x1f")]

        keys.update(pair_keys.drop_duplicates().tolist())

        log(
            f"all version file: loaded chunk {chunk_no:,}, "
            f"unique all-version keys so far {len(keys):,}"
        )

    log(
        f"All version key load complete: "
        f"{len(keys):,} unique docnum/version keys"
    )

    return keys


def remove_all_csv_batches(csv_name: str) -> None:
    """
    Remove numeric batch files from prior runs.

    Example input:
      im_doc_secure.csv

    Files removed:
      im_doc_secure_0001.csv
      im_doc_secure_0002.csv
    """
    stem = Path(csv_name).stem
    pattern = str(SCOPE_PATH / f"{stem}_*.csv")

    old_files = glob.glob(pattern)

    if old_files:
        log(f"Removing {len(old_files):,} old CSV batch file(s) for {stem}")

    for file_name in old_files:
        Path(file_name).unlink(missing_ok=True)




def make_row_key(df: pd.DataFrame) -> pd.Series:
    """
    Build a stable dedupe key across OUTPUT_COLUMNS.

    This replaces full-dataset drop_duplicates() without holding all rows
    in memory.
    """
    return (
        df[OUTPUT_COLUMNS]
        .fillna("")
        .astype(str)
        .agg("\x1f".join, axis=1)
    )


class DedupStore:
    """
    SQLite-backed dedupe and distinct counting.

    This avoids keeping these large objects in memory:
      1. all output row keys
      2. all distinct client values
      3. all distinct document values
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
                client_value TEXT NOT NULL,
                PRIMARY KEY (dataset_name, client_value)
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE distinct_docs (
                dataset_name TEXT NOT NULL,
                doc_value TEXT NOT NULL,
                PRIMARY KEY (dataset_name, doc_value)
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

        Exact dedupe is based on OUTPUT_COLUMNS.
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
        client_count_column: str,
        doc_count_column: str,
    ) -> None:
        """
        Store distinct client and document values on disk.
        """
        if df.empty:
            return

        client_values = (
            normalize_series(df[client_count_column])
            .loc[lambda x: x.ne("")]
            .drop_duplicates()
            .tolist()
        )

        doc_values = (
            normalize_series(df[doc_count_column])
            .loc[lambda x: x.ne("")]
            .drop_duplicates()
            .tolist()
        )

        cur = self.conn.cursor()
        cur.execute("BEGIN")

        cur.executemany(
            """
            INSERT OR IGNORE INTO distinct_clients
            (dataset_name, client_value)
            VALUES (?, ?)
            """,
            [(dataset_name, value) for value in client_values],
        )

        cur.executemany(
            """
            INSERT OR IGNORE INTO distinct_docs
            (dataset_name, doc_value)
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
    client_count_column: str = "fen_LegalEntityId"
    doc_count_column: str = "docnum"


class DatasetWriter:

    def __init__(
        self,
        config: DatasetConfig,
    ) -> None:

        self.config = config

        self.csv_stem = (
            Path(config.csv_name).stem
        )

        self.csv_batch_no = 1

        self.csv_batch_row_count = 0

        self.total_rows_written = 0

        remove_all_csv_batches(
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
                self.csv_batch_row_count
                == 0
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
                    f"completed batch "
                    f"{self.csv_batch_no:04d}"
                )

                self.csv_batch_no += 1

                self.csv_batch_row_count = 0

        return len(df)

def iter_im_doc_source_chunks() -> pd.io.parsers.TextFileReader:
    """
    Read source file in chunks and only load required columns.
    """
    usecols = list(dict.fromkeys(BASE_REQUIRED_COLUMNS))

    return pd.read_csv(
        SOURCE_FILE,
        usecols=usecols,
        dtype=str,
        chunksize=SOURCE_CHUNK_SIZE,
        keep_default_na=False,
        low_memory=False,
    )


def filter_doc_matched(
    df: pd.DataFrame,
) -> pd.DataFrame:
    return df[
        is_one(df["DocMatchBoolean"])
    ]


def filter_supported_insecure(
    df: pd.DataFrame,
) -> pd.DataFrame:
    return df[
        is_supported_doc_type(df["t_alias"])
        & Is_HIPAA_no(df["Is_HIPAA"])
    ]


def filter_unsupported_insecure(
    df: pd.DataFrame,
) -> pd.DataFrame:
    return df[
        is_unsupported_doc_type(df["t_alias"])
        & Is_HIPAA_no(df["Is_HIPAA"])
    ]

def build_excel_from_csv_batches() -> None:

    with pd.ExcelWriter(
        IM_DOC_SCOPE_XLSX,
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

                if (
                    current_row
                    >= MAX_EXCEL_EXPORT_ROWS
                ):
                    break

                for chunk in pd.read_csv(
                    file,
                    chunksize=5000,
                    dtype=str,
                    keep_default_na=False,
                ):

                    if (
                        current_row
                        >= MAX_EXCEL_EXPORT_ROWS
                    ):
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

                    current_row += len(
                        chunk
                    )

            log(
                f"{sheet_name}: "
                f"{current_row:,} rows exported"
            )

def process_im_doc_scope() -> None:
    """
    Main batch-processing function for im_doc scope.
    """
    ensure_scope_dirs()

    log("Starting im_doc scope build")
    log(f"Source file: {SOURCE_FILE}")
    log(f"Source chunk size: {SOURCE_CHUNK_SIZE:,}")
    log(f"CSV batch size: {CSV_BATCH_SIZE:,}")
    log(f"Excel output: {IM_DOC_SCOPE_XLSX}")

    validate_source_columns()


    ids_offboarded_v7 = load_client_scope_ids("client_offboarded_v7.csv")
    ids_offboarded_v8 = load_client_scope_ids("client_offboarded_v8.csv")
    all_version_keys = load_all_version_keys()

    active_statuses = {
        str(value).strip()
        for value in ACTIVE_STATUSES
    }

    offboarded_status = str(OFFBOARDED_STATUS).strip()

    excluded_statuses = set(active_statuses)
    excluded_statuses.add(offboarded_status)

    configs = [
        DatasetConfig(
            dataset_name="im_doc_offboarded_v7",
            csv_name="im_doc_offboarded_v7.csv",
            sheet_name="doc_offboarded_v7",
            predicate=lambda df: (
                df["_doc_matched"]
                & df["_supported_insecure"]
                & df["_fen_LegalEntityId_norm"].isin(ids_offboarded_v7)
            ),
            client_count_column="fen_LegalEntityId",
            doc_count_column="docnum",
        ),
        DatasetConfig(
            dataset_name="im_doc_offboarded",
            csv_name="im_doc_offboarded.csv",
            sheet_name="doc_offboarded",
            predicate=lambda df: (
                df["_doc_matched"]
                & df["_supported_insecure"]
                & is_one(df["fen_IsOffboarded"])
            ),
            client_count_column="fen_LegalEntityId",
            doc_count_column="docnum",
        ),
        DatasetConfig(
            dataset_name="im_doc_offboarded_v8",
            csv_name="im_doc_offboarded_v8.csv",
            sheet_name="doc_offboarded_v8",
            predicate=lambda df: (
                df["_doc_matched"]
                & df["_supported_insecure"]
                & df["_fen_LegalEntityId_norm"].isin(ids_offboarded_v8)
            ),
            client_count_column="fen_LegalEntityId",
            doc_count_column="docnum",
        ),
        DatasetConfig(
            dataset_name="im_doc_active_entity",
            csv_name="im_doc_active_entity.csv",
            sheet_name="doc_active_entity",
            predicate=lambda df: (
                df["_doc_matched"]
                & df["_supported_insecure"]
                & df["_fen_ExhaustedRoleStatus_norm"].isin(active_statuses)
            ),
            client_count_column="fen_LegalEntityId",
            doc_count_column="docnum",
        ),
        DatasetConfig(
            dataset_name="im_doc_other_status_entity",
            csv_name="im_doc_other_status_entity.csv",
            sheet_name="doc_other_status",
            predicate=lambda df: (
                df["_doc_matched"]
                & df["_supported_insecure"]
                & ~df["_fen_ExhaustedRoleStatus_norm"].isin(excluded_statuses)
            ),
            client_count_column="fen_LegalEntityId",
            doc_count_column="docnum",
        ),
        DatasetConfig(
            dataset_name="im_doc_all_version",
            csv_name="im_doc_all_version.csv",
            sheet_name="im_all_version",
            predicate=lambda df: df["_doc_version_key"].isin(all_version_keys),
            client_count_column="c1alias",
            doc_count_column="docnum",
        ),
        DatasetConfig(
            dataset_name="im_doc_orphaned_supported_insecure",
            csv_name="im_doc_orphaned_supported_insecure.csv",
            sheet_name="orphaned_supported_insecure",
            predicate=lambda df: (
                df["_supported_insecure"]
                & is_zero(df["ClientMatchBoolean"])
            ),
            client_count_column="c1alias",
            doc_count_column="docnum",
        ),
        DatasetConfig(
            dataset_name="im_doc_unsupported_insecure",
            csv_name="im_doc_unsupported_insecure.csv",
            sheet_name="nsupported_insecure",
            predicate=lambda df: df["_unsupported_insecure"],
            client_count_column="c1alias",
            doc_count_column="docnum",
        ),
        DatasetConfig(
            dataset_name="im_doc_secure",
            csv_name="im_doc_secure.csv",
            sheet_name="doc_secure",
            predicate=lambda df: Is_HIPAA_yes(df["Is_HIPAA"]),
            client_count_column="fen_LegalEntityId",
            doc_count_column="docnum",
        ),
    ]

    dedup = DedupStore(SQLITE_DEDUP_DB)
    writers = {
        cfg.dataset_name: DatasetWriter(
            config=cfg,
        )
        for cfg in configs
    }



    total_source_rows = 0

    try:
        for chunk_no, chunk in enumerate(
            iter_im_doc_source_chunks(),
            start=1,
        ):
            source_rows = len(chunk)
            total_source_rows += source_rows

            log(
                f"Reading source chunk {chunk_no:,}: "
                f"{source_rows:,} rows "
                f"(total source rows read: {total_source_rows:,})"
            )

            if chunk.empty:
                continue

            chunk["_fen_LegalEntityId_norm"] = normalize_series(
                chunk["fen_LegalEntityId"]
            )
            chunk["_fen_ExhaustedRoleStatus_norm"] = normalize_series(
                chunk["fen_ExhaustedRoleStatus"]
            )
            chunk["_doc_version_key"] = make_pair_key(
                chunk["docnum"],
                chunk["version"],
            )

            chunk["_doc_matched"] = is_one(chunk["DocMatchBoolean"])
            chunk["_supported_insecure"] = (
                is_supported_doc_type(chunk["t_alias"])
                & Is_HIPAA_no(chunk["Is_HIPAA"])
            )
            chunk["_unsupported_insecure"] = (
                is_unsupported_doc_type(chunk["t_alias"])
                & Is_HIPAA_no(chunk["Is_HIPAA"])
            )

            for cfg in configs:
                mask = cfg.predicate(chunk)
                df_scope = chunk.loc[mask, OUTPUT_COLUMNS]

                if df_scope.empty:
                   
                    continue

                df_new = dedup.filter_new_rows(
                    dataset_name=cfg.dataset_name,
                    df=df_scope,
                )

                if df_new.empty:
                    
                    continue

                dedup.add_summary_values(
                    dataset_name=cfg.dataset_name,
                    df=df_new,
                    client_count_column=cfg.client_count_column,
                    doc_count_column=cfg.doc_count_column,
                )

                written = writers[cfg.dataset_name].write(df_new)

                log(
                    f"{cfg.dataset_name}: chunk {chunk_no:,}, "
                    f"matching rows {len(df_scope):,}, "
                    f"new rows written {written:,}, "
                    f"total written {writers[cfg.dataset_name].total_rows_written:,}"
                )
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



    finally:
        dedup.close()

        if SQLITE_DEDUP_DB.exists():
            SQLITE_DEDUP_DB.unlink(
                missing_ok=True
            )


def main() -> None:
    """
    Run the production batch job.
    """
    start = time.time()

    try:
        process_im_doc_scope()
    finally:
        elapsed = round(time.time() - start, 2)
        log(f"Completed in {elapsed:,} seconds")


def run_unit_tests() -> None:
    """
    Lightweight unit tests for the core filter behavior.

    These tests do not write files.
    """
    df = pd.DataFrame(
        {
            "DocMatchBoolean": [1, 0, "1"],
            "t_alias": ["PDF", "ZIP", "URL"],
            "Is_HIPAA": ["N", "N", "Y"],
            "ClientMatchBoolean": [0, 1, "0"],
        }
    )

    matched = filter_doc_matched(df)
    assert len(matched) == 2

    supported_insecure = filter_supported_insecure(df)
    assert len(supported_insecure) == 1
    assert supported_insecure.iloc[0]["t_alias"] == "PDF"

    unsupported_insecure = filter_unsupported_insecure(df)
    assert len(unsupported_insecure) == 1
    assert unsupported_insecure.iloc[0]["t_alias"] == "ZIP"

    zero_client_match = df[is_zero(df["ClientMatchBoolean"])]
    assert len(zero_client_match) == 2

    log("_13_im_doc_scope unit tests passed.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_unit_tests()
    else:
        main()