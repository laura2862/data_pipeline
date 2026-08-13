# FenE to FenX Migration Data Pipeline and Vendor Extracts Reconciliation Framework

## Overview

This project supports the migration of client, document, and related entity data from the Fenergo (FenE) platform to FenX.

The pipeline performs the following functions:

1. Extract migration data from the FenE database
2. Match FenE and iManage documents
3. Match FenE and iManage clients
4. Build final FenE-to-FenX migration datasets
5. Filter data to migration-approved entities
6. Validate each processing stage
7. Compare BNS migration outputs against E2X vendor extracts

The objective is to provide complete traceability from source system extraction through final reconciliation with vendor deliverables.

## Quick setup

Use Python **3.11, 3.12, or 3.13**. From the project root, run:

macOS/Linux:

```bash
bash setup_env.sh
source .venv/bin/activate
python main.py
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_env.ps1
.\.venv\Scripts\Activate.ps1
python main.py
```

The setup script creates an isolated `.venv`, installs every required Python
package from `requirements.txt`, and verifies that the imports succeed.

To use the database extraction step, users must also install **Microsoft ODBC
Driver 17 or later for SQL Server**, have network access to the BNS databases,
and be authenticated for Windows trusted connection. Users who only run the
matching/scoping steps do not need database connectivity.


# STEP 01 - Extract

## Module

```text
pipeline/_01_extract.py
```

## Purpose

Extract migration data from the FenE and IM SQL database and save to CSV.


## Outputs Location:

```text
temp/
```

Files:

```text
fen_client_detail_raw.csv
fen_client_detail.csv  -  grouped RoleType and Status upon fen_client_detail_raw, and used for mapping
fen_doc.csv
fen_doc_detail.csv
fen_product.csv
fen_comment.csv
fen_contact.csv
fen_association.csv
fen_address.csv
fen_taxid.csv
im_doc.csv
im_doc_detail.csv
```

# STEP 02 - Match Documents

## Module

```text
pipeline/_02_match_documents.py
```

## Purpose

Perform document-level matching between FenE and iManage by 4 ordered layers:
```text
    Layer 1:
        iManage_Doc_Num = docnum

    Layer 2:
        LegalEntityId = c1alias
        AND DocumentName = docname

    Layer 3:
        ReferenceId = c1alias
        AND DocumentName = docname

    Layer 4:
        LegalEntityName = C_DESCRIPT
        AND DocumentName = docname

    Earlier layers win.


```

Creates candidate document mappings for migration.


## Inputs

```text
temp/fen_client_doc.csv
temp/im_client_doc.csv
```

## Output

```text
output/doc_fen_to_im.csv
output/doc_im_to_doc.csv
```


# STEP 03 - Match Clients

## Module

```text
pipeline/_03_match_clients.py
```

## Purpose

Perform client-level matching using fuzzy matching techniques.
Only client-level migration keys are retained.

```text
  Fen client match to IM client.

    Layers:
        1. LegalEntityId = c1alias
        2. ReferenceId = c1alias
        3. LegalEntityName fuzzy C_DESCRIPT
        4. Alias1 fuzzy C_DESCRIPT
        5. Alias2 fuzzy C_DESCRIPT
        6. Alias3 fuzzy C_DESCRIPT
        7. Alias4 fuzzy C_DESCRIPT
```


## Inputs

```text
temp/fen_client_doc.csv
temp/im_client_doc.csv
```

## Output

```text
output/client_fen_to_im.csv
output/client_im_to_doc.csv
```

## Note
RefClientID is LegalEntityId or iManage ClientId as matched reference client Id


---

# STEP 04 - Final FenE Mapped Dataset

## Module

```text
pipeline/_04_final_fen.py
```

## Purpose

Build the final FenE mapped dataset.


## Inputs

```text
output/doc_fen_to_im.csv
output/client_fen_to_im.csv
output/fen_association.csv
output/fen_product.csv
output/fen_case.csv

```

## Processing Summary

Multiple datasets are merged onto:

```text
LegalEntityId
```

One-to-many relationships are aggregated before merging to avoid row explosion.

Examples:

```text
Product Counts
Association Counts
Case Counts
```

## Output

```text
output/final_fen_to_im.csv
```

---

# STEP 05 - Final iManage Mapped Dataset

## Module

```text
pipeline/_05_final_im.py
```

## Purpose

Build reverse mapping for iManage mapped dataset:


## Inputs

```text
output/doc_im_to_fen.csv
output/client_im_to_fen.csv

```

## Processing Summary

Multiple datasets are merged onto:

```text
c1alias - iManage client ID
```
## Output

```text
output/final_im_to_fen.csv
```


---

# STEP 06 - Entity In Scope Filter

## Module

```text
pipeline/_06_entity_in_scope_filter.py
```

## Purpose

Get In-Scope entities by filtering out the v7 offboarded entities based on temp/scope/client_offboarded_v7.csv

## Inputs

```text
output/final_fen_to_im.csv
temp/scope/client_offboarded_v7.csv
```

## Processing Logic

Keep only records where:

```text
LegalEntityId
does not exist in
temp/scope/client_offboarded_v7.csv
```

## Outputs

```text
output_in_scope/
output_out_scope/
```

Examples:

```text
in_scope_fen_client_detail.csv
in_scope_fen_doc.csv
in_scope_fen_product.csv
in_scope_fen_comment.csv
in_scope_fen_contact.csv
in_scope_fen_association.csv
in_scope_fen_address.csv
in_scope_fen_taxid.csv

out_scope_fen_client_detail.csv
out_scope_fen_doc.csv
out_scope_fen_product.csv
out_scope_fen_comment.csv
out_scope_fen_contact.csv
out_scope_fen_association.csv
out_scope_fen_address.csv
out_scope_fen_taxid.csv
```


---

# STEP 10 -13 - Scoping

## Module

```text
pipeline/_10_scoping.py
```

## Purpose

Split client and mapped iManage documents into defined buckets including active entity, offboarded_v8_entity, orphan_im_doc, ...

## Outputs

```text
temp/scope/
```
---
# STEP 14 - Doc Scoping Map
## Module

```text
pipeline/_14_doc_scoping_map.py
```

## Purpose

Get in-scope iManage documents with mapped FID from final_im_to_fen.csv by filter out
- ClientMatchBoolean=0
- Is_HIPAA='N'
- t_alias not in (   
    "PPTM",
    "NOTES",
    "URL",
    "ZIP"
    )

Validate the result with in-scope buckets from 
temp/scope/im_doc_active_entity,
temp/scope/im_doc_offboarded_v8_entity

## Outputs

```text
temp/scope/in_scope_im_doc_final.csv
```
---


# STEP 15 - e2x_compare_extract
## Module

```text
analysis/e2x_compare_extract.py
```
## Purpose
compare the extract results by E2X tool from temp/e2x_output with the results generated by this tool in output_in_scope/

## Outputs

```text
validation_output/e2x_detail_mapping_summary.csv
```
---

