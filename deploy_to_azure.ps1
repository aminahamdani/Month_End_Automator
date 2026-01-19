# PowerShell script to deploy Month-End Automator to Azure
# Run this script from the project root directory

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$AppServiceName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus"
)

Write-Host "Starting Azure deployment..." -ForegroundColor Green

# Check if Azure CLI is installed
try {
    az --version | Out-Null
} catch {
    Write-Host "Error: Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}

# Login to Azure (if not already logged in)
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if (-not $account) {
    Write-Host "Please log in to Azure..." -ForegroundColor Yellow
    az login
}

# Create resource group
Write-Host "Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create App Service Plan
$planName = "$AppServiceName-plan"
Write-Host "Creating App Service Plan: $planName" -ForegroundColor Yellow
az appservice plan create --name $planName --resource-group $ResourceGroupName --sku B1 --is-linux

# Create Web App
Write-Host "Creating Web App: $AppServiceName" -ForegroundColor Yellow
az webapp create --resource-group $ResourceGroupName --plan $planName --name $AppServiceName --runtime "PYTHON|3.9"

# Configure startup command
Write-Host "Configuring startup command..." -ForegroundColor Yellow
$startupCommand = "gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 600"
az webapp config set --resource-group $ResourceGroupName --name $AppServiceName --startup-file $startupCommand

# Create deployment ZIP (excluding unnecessary files)
Write-Host "Creating deployment package..." -ForegroundColor Yellow
$excludeFiles = @("*__pycache__*", "*.pyc", "*.csv", "*.xlsx", "test_*", "*.md", ".git*", "deploy.zip")
$zipFile = "deploy.zip"

# Remove existing zip if present
if (Test-Path $zipFile) {
    Remove-Item $zipFile
}

# Create zip (manual selection of files for simplicity)
$filesToDeploy = @(
    "main.py",
    "processor.py",
    "reporter.py",
    "errors.py",
    "requirements.txt",
    "templates",
    "services"
)

# Use PowerShell Compress-Archive
Compress-Archive -Path $filesToDeploy -DestinationPath $zipFile -Force

Write-Host "Deploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip --resource-group $ResourceGroupName --name $AppServiceName --src $zipFile

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Your app is available at: https://$AppServiceName.azurewebsites.net" -ForegroundColor Cyan

# Clean up
Write-Host "Cleaning up deployment package..." -ForegroundColor Yellow
Remove-Item $zipFile -ErrorAction SilentlyContinue

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Visit https://$AppServiceName.azurewebsites.net to test your app" -ForegroundColor White
Write-Host "2. Check logs: az webapp log tail --name $AppServiceName --resource-group $ResourceGroupName" -ForegroundColor White
