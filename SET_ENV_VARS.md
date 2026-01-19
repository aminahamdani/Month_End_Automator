# Set Environment Variables in Azure App Service

This guide shows how to add environment variables (app settings) to your Azure App Service.

## Quick Commands

### 1. Set Multiple Environment Variables (Example)

```powershell
az webapp config appsettings set `
    --resource-group month-end-automator-rg `
    --name month-end-automator `
    --settings DB_URL="your_database_url" SECRET_KEY="your_secret_key" EMAIL_SENDER="noreply@example.com"
```

### 2. Set Individual Environment Variables

```powershell
# Set DB_URL
az webapp config appsettings set `
    --resource-group month-end-automator-rg `
    --name month-end-automator `
    --settings DB_URL="postgresql://user:pass@host:5432/dbname"

# Set SECRET_KEY
az webapp config appsettings set `
    --resource-group month-end-automator-rg `
    --name month-end-automator `
    --settings SECRET_KEY="your-very-secure-secret-key-here"

# Set EMAIL_SENDER
az webapp config appsettings set `
    --resource-group month-end-automator-rg `
    --name month-end-automator `
    --settings EMAIL_SENDER="noreply@yourdomain.com"
```

### 3. Verify Environment Variables Are Set

```powershell
# List all app settings
az webapp config appsettings list `
    --resource-group month-end-automator-rg `
    --name month-end-automator

# Get specific setting
az webapp config appsettings list `
    --resource-group month-end-automator-rg `
    --name month-end-automator `
    --query "[?name=='DB_URL'].value" --output tsv
```

### 4. Delete an Environment Variable

```powershell
az webapp config appsettings delete `
    --resource-group month-end-automator-rg `
    --name month-end-automator `
    --setting-names DB_URL
```

## Using the PowerShell Script

Run the provided script:
```powershell
.\set_azure_env_vars.ps1
```

**Note:** Edit the script first to set your actual values for DB_URL, SECRET_KEY, and EMAIL_SENDER.

## Environment Variables for Month-End Automator

Recommended environment variables you might want to set:

```powershell
# Database connection (if using external database)
DB_URL="postgresql://user:password@host:5432/month_end_automator"

# Secret key for session management (generate a secure random string)
SECRET_KEY="generate-a-secure-random-string-here"

# Email configuration
EMAIL_SENDER="noreply@yourdomain.com"
EMAIL_SMTP_HOST="smtp.gmail.com"
EMAIL_SMTP_PORT="587"
EMAIL_USERNAME="your-email@gmail.com"
EMAIL_PASSWORD="your-app-password"

# Azure Storage (if using Blob Storage for file persistence)
AZURE_STORAGE_ACCOUNT="yourstorageaccount"
AZURE_STORAGE_KEY="yourstoragekey"
AZURE_STORAGE_CONTAINER="uploads"

# Application settings
APP_ENV="production"
LOG_LEVEL="INFO"
```

## Example: Set All Recommended Variables

```powershell
az webapp config appsettings set `
    --resource-group month-end-automator-rg `
    --name month-end-automator `
    --settings `
        DB_URL="your_db_url" `
        SECRET_KEY="your_secret_key" `
        EMAIL_SENDER="noreply@example.com" `
        APP_ENV="production" `
        LOG_LEVEL="INFO"
```

## Security Best Practices

1. **Never commit secrets to code** - Always use environment variables
2. **Use Azure Key Vault** for sensitive values in production
3. **Rotate secrets regularly**
4. **Use different values** for development and production

## Verify in Azure Portal

1. Go to Azure Portal
2. Navigate to your App Service: `month-end-automator`
3. Go to **Configuration** → **Application settings**
4. You'll see all environment variables listed there

## Access Environment Variables in Your App

In your FastAPI app (`main.py`), you can access these with:

```python
import os

db_url = os.getenv("DB_URL", "default_value")
secret_key = os.getenv("SECRET_KEY", "default_secret")
email_sender = os.getenv("EMAIL_SENDER", "noreply@example.com")
```

## Troubleshooting

**If settings don't appear:**
- Wait a few seconds and refresh
- Restart the App Service: `az webapp restart --name month-end-automator --resource-group month-end-automator-rg`

**Check current settings:**
```powershell
az webapp config appsettings list --resource-group month-end-automator-rg --name month-end-automator --output table
```
