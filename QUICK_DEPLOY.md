# Quick Azure Deployment Guide

## Fastest Way to Deploy (5 minutes)

### Step 1: Install Azure CLI
Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

### Step 2: Login to Azure
```bash
az login
```

### Step 3: Run Deployment Script (Windows PowerShell)
```powershell
.\deploy_to_azure.ps1 -ResourceGroupName "monthEnd-rg" -AppServiceName "month-end-automator-$(Get-Random)" -Location "eastus"
```

**Or manually:**

### Step 3 (Manual): Create Resources
```bash
# 1. Create resource group
az group create --name monthEnd-rg --location eastus

# 2. Create App Service Plan
az appservice plan create --name monthEnd-plan --resource-group monthEnd-rg --sku B1 --is-linux

# 3. Create Web App (choose a unique name)
az webapp create --resource-group monthEnd-rg --plan monthEnd-plan --name month-end-automator-UNIQUE --runtime "PYTHON|3.9"

# 4. Set startup command
az webapp config set --resource-group monthEnd-rg --name month-end-automator-UNIQUE --startup-file "gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 600"
```

### Step 4: Deploy Code
```bash
# Create ZIP file (exclude unnecessary files)
# Windows PowerShell:
Compress-Archive -Path main.py,processor.py,reporter.py,errors.py,requirements.txt,templates,services -DestinationPath deploy.zip -Force

# Or manually zip these files/folders:
# - main.py
# - processor.py  
# - reporter.py
# - errors.py
# - requirements.txt
# - templates/ (folder)
# - services/ (folder)

# Deploy ZIP
az webapp deployment source config-zip --resource-group monthEnd-rg --name month-end-automator-UNIQUE --src deploy.zip
```

### Step 5: Access Your App
Visit: `https://month-end-automator-UNIQUE.azurewebsites.net`

**Login:**
- Username: `amina`
- Password: `amina0000`

## Check Deployment Status
```bash
az webapp log tail --name month-end-automator-UNIQUE --resource-group monthEnd-rg
```

## Important Notes

⚠️ **File Storage**: Azure App Service has ephemeral storage. Files in `data/uploads` will be lost on restart.

💡 **Solution**: Consider using Azure Blob Storage for persistent file storage (see full deployment guide).

## Full Documentation
See `AZURE_DEPLOYMENT.md` for detailed deployment options, troubleshooting, and advanced configuration.
