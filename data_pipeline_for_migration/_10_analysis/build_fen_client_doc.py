from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv
from _01_config.settings import TEMP_FOLDER
def build_fen_client_doc():

    fen_doc = load_csv(TEMP_FOLDER/"fen_doc.csv")
    fen_doc_detail = load_csv(TEMP_FOLDER/"fen_doc_detail.csv")
    fen_client_detail = load_csv(TEMP_FOLDER/"fen_client_detail.csv")
    fen_association = load_csv(TEMP_FOLDER/"fen_association.csv")
    fen_product = load_csv(TEMP_FOLDER/"fen_product.csv")
    fen_case = load_csv(TEMP_FOLDER/"fen_case.csv")

    result = fen_client_detail.merge(
        fen_doc,
        on="LegalEntityId",
        how="left"
    )

    result = result.merge(
        fen_doc_detail,
        on="DocumentId",
        how="left"
    )

    # result = result.merge(
    #     fen_association,
    #     on="LegalEntityId",
    #     how="left"
    # )

    # result = result.merge(
    #     fen_product,
    #     on="LegalEntityId",
    #     how="left"
    # )

    # result = result.merge(
    #     fen_case,
    #     on="LegalEntityId",
    #     how="left"
    # )
    print(result[result["LegalEntityId"] == 180])

    output_file = (
        TEMP_FOLDER /
        "fen_client_doc.csv"
    )

    # result.to_csv(
    #     output_file,
    #     index=False,
    #     encoding="utf-8-sig"
    # )
    save_to_csv(result,output_file)

    print(
        f"Saved {len(result):,} rows to {output_file}"
    )
    
    return result







if __name__ == "__main__":

    import pandas as pd

    fen_client_detail = load_csv(
       TEMP_FOLDER/ "fen_client_detail.csv"
    )

    result = build_fen_client_doc()

    print("\n" + "=" * 80)
    print("SOURCE ROLES - LE=180")
    print("=" * 80)

    print(
        fen_client_detail.loc[
            fen_client_detail["LegalEntityId"] == 180,
            [
                "RoleType",
                "RoleStatus"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            ["RoleType", "RoleStatus"]
        )
        .to_string(index=False)
    )

    print("\n" + "=" * 80)
    print("MERGED ROLES - LE=180")
    print("=" * 80)

    print(
        result.loc[
            result["LegalEntityId"] == 180,
            [
                "DocumentId",
                "RoleType",
                "RoleStatus"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            ["RoleType", "RoleStatus"]
        )
        .to_string(index=False)
    )

    print(
        f"\nTotal Rows for LE=180: "
        f"{len(result[result['LegalEntityId'] == 180])}"
    )