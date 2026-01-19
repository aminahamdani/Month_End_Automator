# Force Oryx to rebuild by triggering a deployment
# This script ensures Oryx installs dependencies from requirements.txt

param(
    [string]$ResourceGroupName = "month-end-automator-rg",
    [string]$AppServiceName = "month-end-automator"
)

Write-Host "Forcing Oryx build for $AppServiceName..." -ForegroundColor Green

# Ensure SCM_DO_BUILD_DURING_DEPLOYMENT is set
Write-Host "Setting SCM_DO_BUILD_DURING_DEPLOYMENT=true..." -ForegroundColor Yellow
az webapp config appsettings set `
    --resource-group $ResourceGroupName `
    --name $AppServiceName `
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Restart the app to trigger build
Write-Host "Restarting app to trigger Oryx build..." -ForegroundColor Yellow
az webapp restart --resource-group $ResourceGroupName --name $AppServiceName

Write-Host "`nBuild triggered! Check logs in Azure Portal -> Log stream" -ForegroundColor Green
Write-Host "Or run: az webapp log tail --name $AppServiceName --resource-group $ResourceGroupName" -ForegroundColor Cyan
