"""
Read from output_in_scope/in_scope_doc_im_to_fen where 
- ClientMatchBoolean=0
- Is_HIPAA='N'
- t_alias not in (   
    "PPTM",
    "NOTES",
    "URL",
    "ZIP"
    )

Checksum compare with the total count of buckets from 

temp/scope/im_doc_active_entity,
temp/scope/im_doc_offboarded_v8_entity,
"""

from _01_config.settings import OUTPUT_IN_SCOPE,SCOPE_FOLDER
from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv


def main():

    print("\nStart filter in-scope iManage document list...")

    im_doc=load_csv( OUTPUT_IN_SCOPE / "in_scope_doc_im_to_fen.csv")


    # Apply filters
    filtered_im_doc = im_doc[
        (im_doc["ClientMatchBoolean"] == 0) & (im_doc["Is_HIPAA"] == "N") & (~im_doc["t_alias"].isin([
            "PPTM",
            "NOTES",
            "URL",
            "ZIP"
        ]))
    ]

    # Keep only required columns
    result_df = filtered_im_doc[
        [
            "docnum",
            "docname",
            "version",
            "docsize",
            "docloc",
            "fen_LegalEntityId",
            "fen_RefClientID",
            "DocMatchedBy",
        ]
    ]

    # save output

    save_to_csv(result_df,

        SCOPE_FOLDER/"in_scope_im_doc_final.csv",
    )

    print(f"Final mapped in-scope iManage documents: {len(result_df)}")


if __name__ == "__main__":
    main()
