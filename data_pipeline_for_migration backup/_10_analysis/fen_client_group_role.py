"""
Create grouped role columns for fen_client_detail_raw.csv.

Input:
    TEMP_FOLDER/fen_client_detail_raw.csv

Output:
    TEMP_FOLDER/fen_client_detail.csv

For each LegalEntityId, assign one unique GroupedRoleType and one
ExhaustedRoleStatus:

1. If isClientEntity = 1 for the LegalEntityId:
   - GroupedRoleType = "Client/Counterparty"
   - ExhaustedRoleStatus = RoleStatus from that entity's Client/Counterparty role

2. If isClientEntity = 0 and the LegalEntityId has RoleType = "Fund":
   - GroupedRoleType = "Fund"
   - ExhaustedRoleStatus = RoleStatus from that entity's Fund role

3. If isClientEntity = 0 and the LegalEntityId has no Fund role:
   - GroupedRoleType = "Association"
   - ExhaustedRoleStatus = "Active" if any role for the LegalEntityId is Active,
                           otherwise "Inactive"
"""

from pathlib import Path
from typing import Any

import pandas as pd

from _01_config.settings import TEMP_FOLDER

INPUT_FILE = "fen_client_detail_raw.csv"
OUTPUT_FILE = "fen_client_detail.csv"

CLIENT_ROLE = "Client/Counterparty"
FUND_ROLE = "Fund"
ASSOCIATION_ROLE = "Association"
ACTIVE_STATUS = "Active"
INACTIVE_STATUS = "Inactive"

REQUIRED_COLUMNS = [
    "LegalEntityId",
    "RoleType",
    "RoleStatus",
    "isClientEntity",
]


def _is_truthy(value: Any) -> bool:
    """Convert common CSV truthy values to bool."""
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 1
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def _clean_series(series: pd.Series) -> pd.Series:
    """Return a string-cleaned Series with nulls converted to empty strings."""
    return series.fillna("").astype(str).str.strip()


def _has_active_status(group: pd.DataFrame) -> bool:
    """Check whether the LegalEntityId group has at least one Active RoleStatus."""
    return _clean_series(group["RoleStatus"]).str.casefold().eq("active").any()


def _get_role_status(group: pd.DataFrame, role_type: str) -> str:
    """
    Return the RoleStatus that corresponds to the preferred role_type.

    If multiple rows exist for the same role_type, Active is preferred when present.
    Otherwise, the first non-empty status for that role is returned. If no status is
    available, the status falls back to Active if any role in the entity is Active,
    otherwise Inactive.
    """
    role_type_clean = _clean_series(group["RoleType"])
    matched_rows = group[role_type_clean.eq(role_type)]

    if not matched_rows.empty:
        matched_statuses = _clean_series(matched_rows["RoleStatus"])

        if matched_statuses.str.casefold().eq("active").any():
            return ACTIVE_STATUS

        non_empty_statuses = matched_statuses[matched_statuses.ne("")]
        if not non_empty_statuses.empty:
            return non_empty_statuses.iloc[0]

    return ACTIVE_STATUS if _has_active_status(group) else INACTIVE_STATUS


def _derive_grouped_role_for_entity(group: pd.DataFrame) -> pd.Series:
    """Derive GroupedRoleType and ExhaustedRoleStatus for one LegalEntityId."""
    is_client_entity = group["isClientEntity"].map(_is_truthy).any()
    role_types = _clean_series(group["RoleType"])

    if is_client_entity:
        grouped_role_type = CLIENT_ROLE
        exhausted_role_status = _get_role_status(group, CLIENT_ROLE)
    elif role_types.eq(FUND_ROLE).any():
        grouped_role_type = FUND_ROLE
        exhausted_role_status = _get_role_status(group, FUND_ROLE)
    else:
        grouped_role_type = ASSOCIATION_ROLE
        exhausted_role_status = ACTIVE_STATUS if _has_active_status(group) else INACTIVE_STATUS

    return pd.Series(
        {
            "GroupedRoleType": grouped_role_type,
            "ExhaustedRoleStatus": exhausted_role_status,
        }
    )


def add_grouped_role_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add GroupedRoleType and ExhaustedRoleStatus columns to fen client detail data."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    grouped_role_df = (
        df.groupby("LegalEntityId", dropna=False)
        .apply(_derive_grouped_role_for_entity)
        .reset_index()
    )

    return df.merge(grouped_role_df, on="LegalEntityId", how="left")


def fen_client_group_role() -> None:
    temp_folder = Path(TEMP_FOLDER)
    input_path = temp_folder / INPUT_FILE
    output_path = temp_folder / OUTPUT_FILE

    df = pd.read_csv(input_path)
    df = add_grouped_role_columns(df)
    df.to_csv(output_path, index=False)

    print(f"Saved grouped role file to: {output_path}")


if __name__ == "__main__":
    fen_client_group_role()
