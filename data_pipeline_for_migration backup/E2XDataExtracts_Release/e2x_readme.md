# Step 1 : DB Settings
Change E2X-Solution-1.2\Scripts\DeployConfig.ps1

    DatabaseName = 'FenergoData'
IST>>
    ServerInstance = 'wvdbsu00612.uatbns.bns,5150'
    UseWindowsAuthentication = $true
    SqlUsername = 'fen_read_ist'
    SqlPassword = 'k1ng$treet2026'


# Step 2 : Generate Deploy-ScotiaBank-E2XObjects.sql 
- go to E2X-Solution-1.2\
- Run .\Scripts\Build-ScotiaBank-E2XObject.ps1, Deploy-ScotiaBank-E2XObjects.sql will be generated in .\Output\


# Step 3: Create E2X schema,tables,views (DDL)
Run Output\Deploy-ScotiaBank-E2XObjects.sql in SSMS ,  Staging Tables will be created and ready to extarct values

# Step 4: Create extract and insert value into staging tables (DML)
Run Execution\PopulateStagingTables.sql in SSMS

# Step 5: Create Batch
- Go to E2XDataExtracts_Release\

## Step 5.1: Create Batch by LegalEntitiesInScope.txt
- Prepare \Output\LegalEntitiesInScope.txt"
- run.\FenXDataMigration.E2XDataExtracts.exe createbatch `
	-f "C:\Users\s7909996\OneDrive - The Bank of Nova Scotia\Documents\Workspace\Doc Analysis\E2X-Solution-1.2\Output\LegalEntitiesInScope.txt"
## Step 5.2: Create Batch by view 
- run .\FenXDataMigration.E2XDataExtracts.exe createbatch `
	-vn "e2x.vwLegalEntitiesInScope" `
	-cn "LegalEntityId"

# Step 6: Generate CSV Files
- go to E2XDataExtracts_Release\
- run
	.\FenXDataMigration.E2XDataExtracts.exe extract `
	-b 1 `
	-f "C:\Users\s7909996\OneDrive - The Bank of Nova Scotia\Documents\Workspace\Doc Analysis\temp\e2x_output" `
	-m Documents
	
