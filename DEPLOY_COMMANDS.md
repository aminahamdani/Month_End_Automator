# Azure Deployment Commands

Run these commands in PowerShell or Command Prompt to deploy your app to Azure.

## Prerequisites

1. Azure CLI installed: https://aka.ms/installazurecliwindows
2. ZIP file: `month_end_automator_deploy.zip` exists in current directory
3. App Service created: `month-end-automator` in resource group `month-end-automator-rg`

## Step-by-Step Deployment

### 1. Login to Azure (if not already logged in)
```powershell
az login
```

### 2. Set your subscription (if needed)
```powershell
# List subscriptions
az account list --output table

# Set to Azure for Students (or your subscription name)
az account set --subscription "Azure for Students"
```

### 3. Verify ZIP file exists
```powershell
dir month_end_automator_deploy.zip
```

### 4. Deploy ZIP file to App Service
```powershell
az webapp deployment source config-zip `
    --resource-group month-end-automator-rg `
    --name month-end-automator `
    --src month_end_automator_deploy.zip
```

### 5. Get App Service URL
```powershell
az webapp show --name month-end-automator --resource-group month-end-automator-rg --query defaultHostName --output tsv
```

### 6. Complete deployment check (single command)
```powershell
az webapp show --name month-end-automator --resource-group month-end-automator-rg
```

## One-Line Deployment

If everything is set up, you can deploy with:
```powershell
az webapp deployment source config-zip --resource-group month-end-automator-rg --name month-end-automator --src month_end_automator_deploy.zip
```

## Verify Deployment

After deployment, visit your app:
- URL: `https://month-end-automator.azurewebsites.net` (or check actual URL with command above)
- Login: `amina` / `amina0000`

## Check Deployment Status

```powershell
# View deployment logs
az webapp log tail --name month-end-automator --resource-group month-end-automator-rg

# Check App Service status
az webapp show --name month-end-automator --resource-group month-end-automator-rg --query "{State:state, URL:defaultHostName}" --output table
```

## Troubleshooting

If deployment fails:
1. Verify ZIP file contains all required files
2. Check App Service exists: `az webapp show --name month-end-automator --resource-group month-end-automator-rg`
3. Check resource group exists: `az group show --name month-end-automator-rg`
4. View logs: `az webapp log tail --name month-end-automator --resource-group month-end-automator-rg`
