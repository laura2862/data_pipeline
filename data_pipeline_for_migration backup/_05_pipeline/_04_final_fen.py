# pipeline/04_final_fen.py
from pathlib import Path
import pandas as pd
from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv
from _01_config.settings import OUTPUT_FOLDER
from _01_config.settings import TEMP_FOLDER
CLIENT_PROPERTY_FOLDER = (
    OUTPUT_FOLDER / "clientPropertiesSummary"
)

CLIENT_PROPERTY_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)



def unique_join(values):
    """
    Join unique non-null values with |.
    Example: Active|Inactive|Pending
    """
    cleaned = [
        str(v).strip()
        for v in values
        if pd.notna(v)
        and str(v).strip() != ""
    ]

    if not cleaned:
        return ""

    return "|".join(
        sorted(
            set(cleaned)
        )
    )


def build_association_summary(fen_association):

    if fen_association.empty:
        return pd.DataFrame()

    summary = (
        fen_association
        .groupby("LegalEntityId", dropna=False)
        .agg(
            AssociationCNT=(
                "LegalEntityId",
                "size"
            ),

            ActiveAssociationCNT=(
                "AssociatedRelationStatus",
                lambda x: (
                    x.astype(str)
                    .str.upper()
                    .eq("ACTIVE")
                    .sum()
                )
            ),

            AssociatedLegalEntityIdList=(
                "AssociatedLegalEntityId",
                unique_join
            ),

            RelationshipList=(
                "Relationship",
                unique_join
            ),

            AssociatedRelationIdList=(
                "AssociatedRelationId",
                unique_join
            ),

            AssociatedRelationStatusList=(
                "AssociatedRelationStatus",
                unique_join
            ),

            RelationshipRoleList=(
                "RelationshipRole",
                unique_join
            )
        )
        .reset_index()
    )

    # Count by Association Status

    status_pivot = (
        fen_association
        .pivot_table(
            index="LegalEntityId",
            columns="AssociatedRelationStatus",
            values="AssociatedLegalEntityId",
            aggfunc="count",
            fill_value=0
        )
        .reset_index()
    )

    status_pivot.columns = [
        "LegalEntityId"
        if c == "LegalEntityId"
        else f"AssociationStatusCNT_{c}"
        for c in status_pivot.columns
    ]

    summary = summary.merge(
        status_pivot,
        on="LegalEntityId",
        how="left"
    )

    return summary

def build_case_summary(fen_case):
    """
    One row per LegalEntityId.
    Keeps case type/status list and counts.
    """

    if fen_case.empty:
        return pd.DataFrame()

    summary = (
        fen_case
        .groupby("LegalEntityId", dropna=False)
        .agg(
            CaseCNT=(
                "LegalEntityId",
                "size"
            ),
            CaseIdList=(
                "CaseId",
                unique_join
            ),
            CaseTypeList=(
                "CaseType",
                unique_join
            ),
            CaseStatusList=(
                "CaseStatus",
                unique_join
            )
        )
        .reset_index()
    )

    # Count by CaseType
    if "CaseType" in fen_case.columns:

        case_type_pivot = (
            fen_case
            .pivot_table(
                index="LegalEntityId",
                columns="CaseType",
                values="CaseId",
                aggfunc="count",
                fill_value=0
            )
            .reset_index()
        )

        case_type_pivot.columns = [
            "LegalEntityId"
            if c == "LegalEntityId"
            else f"CaseTypeCNT_{c}"
            for c in case_type_pivot.columns
        ]

        summary = summary.merge(
            case_type_pivot,
            on="LegalEntityId",
            how="left"
        )

    # Count by CaseStatus
    if "CaseStatus" in fen_case.columns:

        case_status_pivot = (
            fen_case
            .pivot_table(
                index="LegalEntityId",
                columns="CaseStatus",
                values="CaseId",
                aggfunc="count",
                fill_value=0
            )
            .reset_index()
        )

        case_status_pivot.columns = [
            "LegalEntityId"
            if c == "LegalEntityId"
            else f"CaseStatusCNT_{c}"
            for c in case_status_pivot.columns
        ]

        summary = summary.merge(
            case_status_pivot,
            on="LegalEntityId",
            how="left"
        )

    return summary


def build_product_summary(fen_product):
    """
    One row per LegalEntityId.
    Keeps product status, booking entity, trading location lists and counts.
    """

    if fen_product.empty:
        return pd.DataFrame()

    summary = (
        fen_product
        .groupby("LegalEntityId", dropna=False)
        .agg(
            ProductCNT=(
                "LegalEntityId",
                "size"
            ),
            ProductIdList=(
                "ProductId",
                unique_join
            ),
            ProductStatusList=(
                "ProductStatus",
                unique_join
            ),
            ProductBookingEntityList=(
                "ProductBookingEntity",
                unique_join
            ),
            ProductTradingLocationList=(
                "ProductTradingLocation",
                unique_join
            )
        )
        .reset_index()
    )

    # Count by ProductStatus
    if "ProductStatus" in fen_product.columns:

        status_pivot = (
            fen_product
            .pivot_table(
                index="LegalEntityId",
                columns="ProductStatus",
                values="ProductId",
                aggfunc="count",
                fill_value=0
            )
            .reset_index()
        )

        status_pivot.columns = [
            "LegalEntityId"
            if c == "LegalEntityId"
            else f"ProductStatusCNT_{c}"
            for c in status_pivot.columns
        ]

        summary = summary.merge(
            status_pivot,
            on="LegalEntityId",
            how="left"
        )

    # Count by ProductBookingEntity
    if "ProductBookingEntity" in fen_product.columns:

        booking_pivot = (
            fen_product
            .pivot_table(
                index="LegalEntityId",
                columns="ProductBookingEntity",
                values="ProductId",
                aggfunc="count",
                fill_value=0
            )
            .reset_index()
        )

        booking_pivot.columns = [
            "LegalEntityId"
            if c == "LegalEntityId"
            else f"ProductBookingEntityCNT_{c}"
            for c in booking_pivot.columns
        ]

        summary = summary.merge(
            booking_pivot,
            on="LegalEntityId",
            how="left"
        )

    # Count by ProductTradingLocation
    if "ProductTradingLocation" in fen_product.columns:

        trading_pivot = (
            fen_product
            .pivot_table(
                index="LegalEntityId",
                columns="ProductTradingLocation",
                values="ProductId",
                aggfunc="count",
                fill_value=0
            )
            .reset_index()
        )

        trading_pivot.columns = [
            "LegalEntityId"
            if c == "LegalEntityId"
            else f"ProductTradingLocationCNT_{c}"
            for c in trading_pivot.columns
        ]

        summary = summary.merge(
            trading_pivot,
            on="LegalEntityId",
            how="left"
        )

    return summary

def main():

    print("\nLoading files...")

    doc_fen_to_im = load_csv(
        OUTPUT_FOLDER / "doc_fen_to_im.csv"
    )

    client_fen_to_im = load_csv(
        OUTPUT_FOLDER / "client_fen_to_im.csv"
    )

    fen_association = pd.read_csv(
        TEMP_FOLDER / "fen_association.csv"
    )

    fen_product = load_csv(
        TEMP_FOLDER / "fen_product.csv"
    )

    fen_case = load_csv(
        TEMP_FOLDER / "fen_case.csv"
    )



    # ==================================================
    # Client Match
    # ==================================================

    print(
        "\nDuplicate LegalEntityId in client_fen_to_im:",
        client_fen_to_im["LegalEntityId"]
        .duplicated()
        .sum()
    )

    client_fen_to_im = (
        client_fen_to_im[
            [
                "LegalEntityId",
                "ReferenceId",
                "ClientMatchBoolean",
                "ClientMatchedBy",
                "ClientMatchLayer",
                "ClientNameScore",
                "RefClientID"
            ]
        ]
        .sort_values(
            ["LegalEntityId", "ClientMatchLayer"]
        )
        .drop_duplicates(
            subset=["LegalEntityId"],
            keep="first"
        )
        .reset_index(drop=True)
    )

    # ==================================================
    # Association
    # ==================================================

    print(
        "Association rows:",
        len(fen_association)
    )

    print(
        "Association duplicate LegalEntityId:",
        fen_association["LegalEntityId"]
        .duplicated()
        .sum()
    )



    # ==================================================
    # Product
    # ==================================================

    print(
        "Product rows:",
        len(fen_product)
    )

    print(
        "Product duplicate LegalEntityId:",
        fen_product["LegalEntityId"]
        .duplicated()
        .sum()
    )


    # ==================================================
    # Case
    # ==================================================

    print(
        "Case rows:",
        len(fen_case)
    )

    print(
        "Case duplicate LegalEntityId:",
        fen_case["LegalEntityId"]
        .duplicated()
        .sum()
    )



    # ==================================================
    # Merge Client
    # ==================================================

    final_fen_to_im = doc_fen_to_im.merge(
        client_fen_to_im,
        on="LegalEntityId",
        how="left"
    )
    
    final_fen_to_im = (
        final_fen_to_im
        .drop(columns=["ReferenceId_y"])
        .rename(
        columns={ "ReferenceId_x": "ReferenceId"}))




    print(
        "\nRows after client merge:",
        len(final_fen_to_im)
    )

    # ==================================================
    # Build Client Property Summaries
    # ==================================================

    print("\nBuilding client property summaries...")

    association_summary = build_association_summary(
        fen_association
    )

    product_summary = build_product_summary(
        fen_product
    )

    case_summary = build_case_summary(
        fen_case
    )

    print(
        "\nAssociation Summary Rows:",
        len(association_summary)
    )

    print(
        "Product Summary Rows:",
        len(product_summary)
    )

    print(
        "Case Summary Rows:",
        len(case_summary)
    )

    # ==================================================
    # Save Summaries
    # ==================================================

    association_summary.to_csv(
        CLIENT_PROPERTY_FOLDER / "association_summary.csv",
        index=False
    )

    product_summary.to_csv(
        CLIENT_PROPERTY_FOLDER / "product_summary.csv",
        index=False
    )

    case_summary.to_csv(
        CLIENT_PROPERTY_FOLDER / "case_summary.csv",
        index=False
    )

    print(
        "Saved association summary:",
        CLIENT_PROPERTY_FOLDER / "association_summary.csv"
    )

    print(
        "Saved product summary:",
        CLIENT_PROPERTY_FOLDER / "product_summary.csv"
    )

    print(
        "Saved case summary:",
        CLIENT_PROPERTY_FOLDER / "case_summary.csv"
    )

    # ==================================================
    # Merge Association Summary
    # ==================================================

    print(
        "\nRows before association summary merge:",
        len(final_fen_to_im)
    )

    final_fen_to_im = final_fen_to_im.merge(
        association_summary,
        on="LegalEntityId",
        how="left"
    )

    print(
        "Rows after association summary merge:",
        len(final_fen_to_im)
    )

    # ==================================================
    # Merge Product Summary
    # ==================================================

    final_fen_to_im = final_fen_to_im.merge(
        product_summary,
        on="LegalEntityId",
        how="left"
    )

    print(
        "Rows after product summary merge:",
        len(final_fen_to_im)
    )

    # ==================================================
    # Merge Case Summary
    # ==================================================

    final_fen_to_im = final_fen_to_im.merge(
        case_summary,
        on="LegalEntityId",
        how="left"
    )

    print(
        "Rows after case summary merge:",
        len(final_fen_to_im)
    )


    print(
        "\nRows after all summary merges:",
        len(final_fen_to_im)
    )

    print(
        "Original doc_fen_to_im rows:",
        len(doc_fen_to_im)
    )

    # ==================================================
    # Print check after merge
    # ==================================================

    print(
        "\nAssociation Summary Rows:",
        len(association_summary)
    )
    

    print(
        "Product Summary Rows:",
        len(product_summary)
    )

    print(
        "Case Summary Rows:",
        len(case_summary)
        
    )

    # ==================================================
    # Validate LegalEntityId = 1
    # ==================================================

    print("\n==================================================")
    print("LEGAL ENTITY 1 VALIDATION")
    print("==================================================")

    # Association
    print("\nAssociation Summary LE=1")

    assoc_le1 = (
        association_summary[
            association_summary["LegalEntityId"] == 1
        ]
    )

    print(assoc_le1)

    print(
        "Raw Association Rows:",
        len(
            fen_association[
                fen_association["LegalEntityId"] == 1
            ]
        )
    )

    # Product
    print("\nProduct Summary LE=1")

    product_le1 = (
        product_summary[
            product_summary["LegalEntityId"] == 1
        ]
    )

    print(product_le1)

    print(
        "Raw Product Rows:",
        len(
            fen_product[
                fen_product["LegalEntityId"] == 1
            ]
        )
    )

    # Case
    print("\nCase Summary LE=1")

    case_le1 = (
        case_summary[
            case_summary["LegalEntityId"] == 1
        ]
    )

    print(case_le1)

    print(
        "Raw Case Rows:",
        len(
            fen_case[
                fen_case["LegalEntityId"] == 1
            ]
        )
    )

    if not assoc_le1.empty:

        print(
            "\nAssociation Count:",
            assoc_le1.iloc[0]["AssociationCNT"]
        )

    if not product_le1.empty:

        print(
            "\nProduct Count:",
            product_le1.iloc[0]["ProductCNT"]
        )

    if not case_le1.empty:

        print(
            "\nCase Count:",
            case_le1.iloc[0]["CaseCNT"]
        )




    # ==================================================
    # Validation
    # ==================================================

    print("\n==================================================")
    print("FINAL FEN TO IM SUMMARY")
    print("==================================================")

    print("Rows:", len(final_fen_to_im))
    print("Columns:", len(final_fen_to_im.columns))

    if "DocMatchBoolean" in final_fen_to_im.columns:
        print(
            "\nDocument Match Breakdown:"
        )
        print(
            final_fen_to_im["DocMatchedBy"]
            .value_counts(dropna=False)
        )

    if "ClientMatchBoolean" in final_fen_to_im.columns:
        print(
            "\nClient Match Breakdown:"
        )
        print(
            final_fen_to_im["ClientMatchedBy"]
            .value_counts(dropna=False)
        )

    # ==================================================
    # Sample Record
    # ==================================================


    print("\n==================================================")
    print("SAMPLE ROW")
    print("==================================================")

    if not final_fen_to_im.empty:

        sample = (
            final_fen_to_im
            .head(1)
            .to_dict("records")[0]
        )

        print(sample)

    # ==================================================
    # Save
    # ==================================================

    # final_fen_to_im.to_csv(
    #     OUTPUT_FOLDER / "final_fen_to_im.csv",
    #     index=False
    # )
    save_to_csv(final_fen_to_im, OUTPUT_FOLDER / "final_fen_to_im.csv")

    print("\nfinal_fen_to_im.csv saved")




if __name__ == "__main__":
    main()