from __future__ import annotations

import pandas as pd

from _11_loaders.csv_saver import save_to_xlsx

from _13_util._scope_common import (
    ACTIVE_STATUSES,
    OFFBOARDED_STATUS,
    SCOPE_PATH,
    TEMP_PATH,
    append_scope_summary,
    anti_join_by_column,
    dedupe_column,
    distinct_count,
    ensure_scope_dirs,
    is_one,
    load_csv_required,
    save_scope_csv_and_xlsx,
)


DATA_TYPE = "fen_client"

CLIENT_DETAIL_FILE = TEMP_PATH / "fen_client_detail.csv"
CLIENT_SCOPE_XLSX = SCOPE_PATH / "01_fen_client_scope.xlsx"

CLIENT_DETAIL_COLUMNS = [
    "LegalEntityId",
    "LegalEntityName",
    "LeType",
    "ReferenceId",
    "Alias1",
    "Alias2",
    "Alias3",
    "Alias4",
    "GroupedRoleType",
    "ExhaustedRoleStatus",
    "EntityType",
    "isFromV7",
    "isClientEntity",
    "IsOffboarded",
    "GlobalRisk",
    "Jurisdictions",
]


def write_client_summary(
    df: pd.DataFrame,
    data_source: str,
) -> None:
    append_scope_summary(
        data_type=DATA_TYPE,
        data_source=data_source,
        total_client_cnt=distinct_count(df, "LegalEntityId"),
        total_doc_count=None,
    )


def save_client_scope(
    df: pd.DataFrame,
    csv_name: str,
    sheet_name: str,
) -> pd.DataFrame:
    csv_path = SCOPE_PATH / csv_name

    save_scope_csv_and_xlsx(
        df=df,
        csv_path=csv_path,
        xlsx_path=CLIENT_SCOPE_XLSX,
        sheet_name=sheet_name,
    )

    write_client_summary(df, csv_name)

    return df


def build_offboarded_v7_scope() -> pd.DataFrame:
    """
    Load existing SCOPE_FOLDER/client_offboarded_v7.csv,
    dedupe LegalEntityId, save to Excel sheet, and append summary.
    """
    csv_name = "client_offboarded_v7.csv"
    source_path = SCOPE_PATH / csv_name

    df = load_csv_required(
        source_path,
        required_columns=["LegalEntityId"],
    )

    df = dedupe_column(df, "LegalEntityId")

    save_to_xlsx(
        df,
        CLIENT_SCOPE_XLSX,
        "client_offboarded_v7",
    )

    write_client_summary(df, csv_name)

    return df


def build_offboarded_scope() -> pd.DataFrame:
    """
    From TEMP_FOLDER/fen_client_detail.csv,
    get distinct LegalEntityId where IsOffboarded = 1.
    """
    df_client = load_csv_required(
        CLIENT_DETAIL_FILE,
        required_columns=CLIENT_DETAIL_COLUMNS,
    )

    df_offboarded = df_client[
        is_one(df_client["IsOffboarded"])
    ]

    df = dedupe_column(
        df_offboarded,
        "LegalEntityId",
    )

    return save_client_scope(
        df=df,
        csv_name="client_offboarded.csv",
        sheet_name="client_offboarded",
    )


def build_offboarded_v8_scope(
    df_offboarded: pd.DataFrame,
    df_offboarded_v7: pd.DataFrame,
) -> pd.DataFrame:
    """
    Offboarded_V8 = Offboarded minus Offboarded_V7.
    """
    df = anti_join_by_column(
        left_df=df_offboarded,
        right_df=df_offboarded_v7,
        column="LegalEntityId",
    )

    return save_client_scope(
        df=df,
        csv_name="client_offboarded_v8.csv",
        sheet_name="client_offboarded_v8",
    )


def build_active_entity_scope() -> pd.DataFrame:
    """
    Get distinct LegalEntityId where ExhaustedRoleStatus is Active.

    Note:
    Requirement has typo 'Acitve', so both Active and Acitve are accepted.
    """
    df_client = load_csv_required(
        CLIENT_DETAIL_FILE,
        required_columns=CLIENT_DETAIL_COLUMNS,
    )

    df_active = df_client[
        df_client["ExhaustedRoleStatus"]
        .astype(str)
        .str.strip()
        .isin(ACTIVE_STATUSES)
    ]

    df = dedupe_column(
        df_active,
        "LegalEntityId",
    )

    return save_client_scope(
        df=df,
        csv_name="client_active_entity.csv",
        sheet_name="client_active_entity",
    )


def build_other_status_entity_scope() -> pd.DataFrame:
    """
    Get distinct LegalEntityId where ExhaustedRoleStatus not in
    Active, Acitve, Offboarded.
    """
    df_client = load_csv_required(
        CLIENT_DETAIL_FILE,
        required_columns=CLIENT_DETAIL_COLUMNS,
    )

    excluded_statuses = set(ACTIVE_STATUSES)
    excluded_statuses.add(OFFBOARDED_STATUS)

    df_other = df_client[
        ~df_client["ExhaustedRoleStatus"]
        .astype(str)
        .str.strip()
        .isin(excluded_statuses)
    ]

    df = dedupe_column(
        df_other,
        "LegalEntityId",
    )

    return save_client_scope(
        df=df,
        csv_name="client_other_status_entity.csv",
        sheet_name="client_other_status_entity",
    )


def main() -> None:
    ensure_scope_dirs()

    df_offboarded_v7 = build_offboarded_v7_scope()
    df_offboarded = build_offboarded_scope()
    build_offboarded_v8_scope(
        df_offboarded=df_offboarded,
        df_offboarded_v7=df_offboarded_v7,
    )

    build_active_entity_scope()
    build_other_status_entity_scope()


def run_unit_tests() -> None:
    df_offboarded = pd.DataFrame(
        {
            "LegalEntityId": ["1", "2", "3"]
        }
    )

    df_offboarded_v7 = pd.DataFrame(
        {
            "LegalEntityId": ["1"]
        }
    )

    df_v8 = anti_join_by_column(
        df_offboarded,
        df_offboarded_v7,
        "LegalEntityId",
    )

    assert set(df_v8["LegalEntityId"]) == {"2", "3"}

    statuses = pd.Series(
        ["Active", "Acitve", "Offboarded", "Closed"]
    )

    active_mask = statuses.astype(str).str.strip().isin(
        ACTIVE_STATUSES
    )

    assert active_mask.tolist() == [
        True,
        True,
        False,
        False,
    ]

    print("_11_fen_client_scope unit tests passed.")


if __name__ == "__main__":
    # run_unit_tests()
    main()