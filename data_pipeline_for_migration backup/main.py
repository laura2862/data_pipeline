
"""
TODO : ADD _14
"""
import sys
import traceback
from datetime import datetime

from _01_config.settings import VALIDATION_FOLDER

from _05_pipeline import (
    _01_extract,
    _02_match_documents,
    _03_match_clients_v2,
    _04_final_fen,
    _05_final_im,
    _06_entity_in_scope_filter,
    _07_validation,
    _10_scoping,
    _14_doc_scoping_map,
)


# ==================================================
# Console Helpers
# ==================================================

def print_banner(
    text
):
    print("\n")
    print("=" * 100)
    print(text)
    print("=" * 100)


# ==================================================
# Step Runner
# ==================================================

def run_step(
    step_name,
    execute_step,
    execute_validation,
    step_function,
    validation_function,
    context,
    log_file
):

    print_banner(
        f"STEP: {step_name}"
    )

    # ----------------------------------
    # Skip Entire Step
    # ----------------------------------

    if (
        not execute_step
        and
        not execute_validation
    ):

        print(
            f"SKIPPED: {step_name}"
        )

        return context

    step_start = datetime.now()

    print(
        f"Start Time: {step_start}"
    )

    try:

        # ----------------------------------
        # Run Pipeline
        # ----------------------------------

        if execute_step:

            print(
                f"Running Pipeline Step..."
            )

            step_function()

            print(
                f"COMPLETED: {step_name}"
            )

        else:

            print(
                "Pipeline execution skipped."
            )

        # ----------------------------------
        # Run Validation
        # ----------------------------------

        if execute_validation:

            print(
                "Running validation..."
            )

            validation_result = (
                validation_function(
                    context,
                    log_file
                )
            )

            if validation_result:

                context.update(
                    validation_result
                )

            print(
                "Validation completed."
            )

        else:

            print(
                "Validation skipped."
            )

        step_end = datetime.now()

        print(
            f"Duration: "
            f"{step_end-step_start}"
        )

        return context

    except Exception as e:

        print_banner(
            f"FAILED: {step_name}"
        )

        traceback.print_exc()

        try:

            _07_validation.save_outputs()

        except Exception:

            pass

        sys.exit(1)

# ==================================================
# Main Pipeline
# ==================================================

def main():
    """
    Execute full pipeline and validation.

    Validation outputs are saved once at the end so Step 10
    is included in validation_log.csv and validation_log.txt.
    """

    # ==================================================
    # PIPELINE CONTROL
    # ==================================================

    PIPELINE_CONTROL = {

        "01_EXTRACT":           False,
        "02_MATCH_DOCUMENTS":   False,
        "03_MATCH_CLIENTS":     False,
        "04_FINAL_FEN":         False,
        "05_FINAL_IM":          False,
        "06_ENTITY_SCOPE":      True,
        "10_SCOPING":           True,
        "14_DOC_SCOPING_MAP":   True,

        "VALIDATE_01": False,
        "VALIDATE_02": False,
        "VALIDATE_03": False,
        "VALIDATE_04": False,
        "VALIDATE_05": False,
        "VALIDATE_06": True,
        "VALIDATE_10": True,
        "VALIDATE_14": True,

    }

    pipeline_start = datetime.now()

    print_banner(
        "FENERGO DOCUMENT MIGRATION PIPELINE"
    )

    print(
        f"Pipeline Start Time: {pipeline_start}"
    )

    _07_validation.reset_validation_outputs()

    log_file = _07_validation.VALIDATION_LOG_TXT

    context = {}
    # ==================================================
    # PIPELINE STEP 01 - Extract
    # ==================================================
    context = run_step(
        step_name="01 Extract",

        execute_step=
            PIPELINE_CONTROL[
                "01_EXTRACT"
            ],

        execute_validation=
            PIPELINE_CONTROL[
                "VALIDATE_01"
            ],

        step_function=
            _01_extract.main,

        validation_function=
            _07_validation.validate_step_01_extract,

        context=context,

        log_file=log_file
    )

    # ==================================================
    # PIPELINE STEP 02 - Match Doc
    # ==================================================
    context = run_step(
        step_name="02 Match Documents",

        execute_step=
            PIPELINE_CONTROL[
                "02_MATCH_DOCUMENTS"
            ],

        execute_validation=
            PIPELINE_CONTROL[
                "VALIDATE_02"
            ],

        step_function=
            _02_match_documents.main,

        validation_function=
            _07_validation.validate_step_02_document_match,

        context=context,

        log_file=log_file
    )

    # ==================================================
    # PIPELINE STEP 03 - Match Client
    # ==================================================
    context = run_step(
        step_name="03 Match Clients",

        execute_step=
            PIPELINE_CONTROL[
                "03_MATCH_CLIENTS"
            ],

        execute_validation=
            PIPELINE_CONTROL[
                "VALIDATE_03"
            ],

        step_function=
            _03_match_clients_v2.main,

        validation_function=
            _07_validation.validate_step_03_client_match,

        context=context,

        log_file=log_file
    )

    # ==================================================
    # PIPELINE STEP 04 - Final Fen
    # ==================================================
    context = run_step(
        step_name="04 Final FEN",

        execute_step=
            PIPELINE_CONTROL[
                "04_FINAL_FEN"
            ],

        execute_validation=
            PIPELINE_CONTROL[
                "VALIDATE_04"
            ],

        step_function=
            _04_final_fen.main,

        validation_function=
            _07_validation.validate_step_04_final_fen,

        context=context,

        log_file=log_file
    )

    # ==================================================
    # PIPELINE STEP 05 - Final IM
    # ==================================================
    context = run_step(
        step_name="05 Final IM",

        execute_step=
            PIPELINE_CONTROL[
                "05_FINAL_IM"
            ],

        execute_validation=
            PIPELINE_CONTROL[
                "VALIDATE_05"
            ],

        step_function=
            _05_final_im.main,

        validation_function=
            _07_validation.validate_step_05_final_im,

        context=context,

        log_file=log_file
    )

    # ==================================================
    # PIPELINE STEP 06 Entity In Scope Filter
    # ==================================================
    context = run_step(
        step_name="06 Entity In Scope Filter",

        execute_step=
            PIPELINE_CONTROL[
                "06_ENTITY_SCOPE"
            ],

        execute_validation=
            PIPELINE_CONTROL[
                "VALIDATE_06"
            ],

        step_function=
            _06_entity_in_scope_filter.main,

        validation_function=
            _07_validation.validate_step_06_entity_scope_filter,

        context=context,

        log_file=log_file
    )

    # ==================================================
    # PIPELINE STEP 10 Scoping
    # ==================================================
    step10_start = datetime.now()
    context = run_step(
        step_name="10 Scoping",

        execute_step=
            PIPELINE_CONTROL[
                "10_SCOPING"
            ],

        execute_validation=
            PIPELINE_CONTROL[
                "VALIDATE_10"
            ],

        step_function=
            _10_scoping.main,

        validation_function=
            _07_validation.validate_step_10_scoping,

        context=context,

        log_file=log_file
    )

    step10_end = datetime.now()


    # ==================================================
    # PIPELINE STEP 14 Doc Scoping Map
    # ==================================================

    context = run_step(
        step_name="14 Doc Scoping Map",

        execute_step=
            PIPELINE_CONTROL[
                "14_DOC_SCOPING_MAP"
            ],

        execute_validation=
            PIPELINE_CONTROL[
                "VALIDATE_14"
            ],

        step_function=
            _14_doc_scoping_map.main,

        validation_function=
            _07_validation.validate_step_14_final_in_scope_im_doc,

        context=context,

        log_file=log_file
    )

    _07_validation.save_outputs()

    pipeline_end = datetime.now()

    print_banner(
        "PIPELINE COMPLETED SUCCESSFULLY"
    )

    print(
        f"Pipeline Started  : {pipeline_start}"
    )

    print(
        f"Pipeline Finished : {pipeline_end}"
    )

    print(
        f"Total Duration    : {pipeline_end - pipeline_start}"
    )

    print(
        f"Step 10 Duration  : {step10_end - step10_start}"
    )

    print(
        f"\nValidation Folder:\n{VALIDATION_FOLDER}"
    )


if __name__ == "__main__":
    main()