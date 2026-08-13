from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SQL_FOLDER = PROJECT_ROOT / "_20_sql"

TEMP_FOLDER = PROJECT_ROOT / "temp"

OUTPUT_FOLDER = PROJECT_ROOT / "output"


SCOPE_FOLDER = PROJECT_ROOT / "temp/scope"
SCOPE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

TEMP_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)



OUTPUT_IN_SCOPE = (
    PROJECT_ROOT /
    "Output_In_Scope"
)

OUTPUT_IN_SCOPE.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_OUT_SCOPE = (
    PROJECT_ROOT /
    "Output_Out_Scope"
)



OUTPUT_OUT_SCOPE.mkdir(
    parents=True,
    exist_ok=True
)

VALIDATION_FOLDER = PROJECT_ROOT / "validation_output"

VALIDATION_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


VENDOR_FOLDER = (
    PROJECT_ROOT
    / "temp"
    / "e2x_ouput"

)


UNSUPPORTED_DOC_TYPES = [
    "PPTM",
    "NOTES",
    "URL",
    "ZIP"
    # "BMP"

]
