from _11_loaders.csv_loader import load_csv
from _11_loaders.csv_saver import save_to_csv
from _01_config.settings import TEMP_FOLDER

def build_im_client_doc():

    im_doc = load_csv(TEMP_FOLDER/"im_doc.csv")
    im_doc_detail = load_csv(TEMP_FOLDER/"im_doc_detail.csv")

    result =im_doc.merge(
        im_doc_detail,
        # on="docnum",
        on=["docnum", "version"],
        how="left"
    )



    print(result[result["c1alias"] == 180])

    output_file = (TEMP_FOLDER / "im_client_doc.csv")
    # result.to_csv(output_file,index=False,encoding="utf-8-sig")
    save_to_csv(result,output_file)
    
    
    print("im_client_doc.csv saved")
    
    return result

