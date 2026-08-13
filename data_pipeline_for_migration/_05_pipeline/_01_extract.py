# pipeline/01_extract.py

from _03_extract.run_fenergo_extract import main as run_fenergo
from _03_extract.run_imanage_extract import main as run_imanage
from _10_analysis.build_fen_client_doc import  build_fen_client_doc
from _10_analysis.build_im_client_doc import build_im_client_doc
from _10_analysis.fen_client_group_role import fen_client_group_role 


def main():

    print("Running Fenergo extract...")
    run_fenergo()
    fen_client_group_role()
    build_fen_client_doc()

    print("Running iManage extract...")
    run_imanage()
    build_im_client_doc()



    print("Extract complete.")


if __name__ == "__main__":
    main()