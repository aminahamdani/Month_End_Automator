# Azure Deployment Guide for Month-End Automator

This guide will help you deploy the Month-End Automator application to Azure App Service.

## Prerequisites

1. **Azure Account**: You need an active Azure subscription
2. **Azure CLI**: Install [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Git**: For deployment via Git (optional)
4. **Python 3.9+**: Locally installed for testing

## Deployment Options

### Option 1: Deploy via Azure Portal (Recommended for Beginners)

1. **Create Azure App Service:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Click "Create a resource" → Search for "Web App"
   - Click "Create"

2. **Configure the App Service:**
   - **Subscription**: Select your subscription
   - **Resource Group**: Create new or use existing
   - **Name**: `month-end-automator` (must be globally unique)
   - **Publish**: Code
   - **Runtime stack**: Python 3.9 or 3.10
   - **Operating System**: Linux (recommended) or Windows
   - **Region**: Choose closest to your users
   - **App Service Plan**: Create new or use existing (Basic B1 minimum recommended)

3. **Deployment:**
   - Go to "Deployment Center" in your App Service
   - Choose deployment source:
     - **GitHub**: Connect your GitHub repository
     - **Local Git**: Use local Git repository
     - **ZIP Deploy**: Upload a ZIP file of your project

4. **Configure Startup Command:**
   - Go to "Configuration" → "General settings"
   - **Startup Command**:
     ```
     gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 600
     ```

### Option 2: Deploy via Azure CLI

1. **Login to Azure:**
   ```bash
   az login
   ```

2. **Create Resource Group:**
   ```bash
   az group create --name monthEndAutomator-rg --location eastus
   ```

3. **Create App Service Plan:**
   ```bash
   az appservice plan create --name monthEndAutomator-plan --resource-group monthEndAutomator-rg --sku B1 --is-linux
   ```

4. **Create Web App:**
   ```bash
   az webapp create --resource-group monthEndAutomator-rg --plan monthEndAutomator-plan --name month-end-automator --runtime "PYTHON|3.9"
   ```

5. **Configure Startup Command:**
   ```bash
   az webapp config set --resource-group monthEndAutomator-rg --name month-end-automator --startup-file "gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 600"
   ```

6. **Deploy Code (via ZIP):**
   ```bash
   # Create a ZIP file (exclude __pycache__, .git, etc.)
   zip -r deploy.zip . -x "*.git*" "*__pycache__*" "*.pyc" "*.csv" "*.xlsx" "test_*" "*.md"

   # Deploy
   az webapp deployment source config-zip --resource-group monthEndAutomator-rg --name month-end-automator --src deploy.zip
   ```

### Option 3: Deploy via GitHub Actions (CI/CD)

1. **Create GitHub Secrets:**
   - Go to your GitHub repository → Settings → Secrets
   - Add:
     - `AZURE_WEBAPP_NAME`: Your app service name
     - `AZURE_WEBAPP_PUBLISH_PROFILE`: Download from Azure Portal (Get publish profile)
     - `AZURE_RESOURCE_GROUP`: Your resource group name

2. **Create `.github/workflows/deploy.yml`:**
   ```yaml
   name: Deploy to Azure App Service

   on:
     push:
       branches: [ main ]

   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v2
       
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: '3.9'
       
       - name: Install dependencies
         run: |
           pip install -r requirements.txt
       
       - name: Deploy to Azure Web App
         uses: azure/webapps-deploy@v2
         with:
           app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
           publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
   ```

## Configuration

### Environment Variables

Set these in Azure Portal → Configuration → Application settings:

- **PORT**: `8000` (optional, Azure sets this automatically)
- **PYTHONPATH**: `/home/site/wwwroot`
- **WEBSITE_TIME_ZONE**: `UTC` (or your preferred timezone)

### File Storage Considerations

**Important**: Azure App Service has ephemeral storage. Files stored in `data/uploads` will be lost on restart.

**Solutions:**
1. **Use Azure Blob Storage** (Recommended):
   - Create Azure Storage Account
   - Upload files to Blob Storage instead of local filesystem

2. **Use Azure Files**:
   - Mount Azure Files as persistent storage

3. **Use External Database**:
   - Consider migrating in-memory stores to Azure SQL Database or Cosmos DB

## Post-Deployment Steps

1. **Verify Deployment:**
   - Visit `https://your-app-name.azurewebsites.net`
   - Should see login page

2. **Check Logs:**
   - Azure Portal → App Service → Log stream
   - Or: `az webapp log tail --name month-end-automator --resource-group monthEndAutomator-rg`

3. **Monitor:**
   - Azure Portal → App Service → Application Insights (enable if needed)

## Troubleshooting

### Common Issues:

1. **502 Bad Gateway:**
   - Check startup command is correct
   - Verify `gunicorn` is in requirements.txt
   - Check App Service logs

2. **Module Not Found:**
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version matches locally

3. **Files Not Persisting:**
   - Use Azure Blob Storage for file uploads
   - Or configure Azure Files mount

4. **Timeout Errors:**
   - Increase timeout in startup command
   - Consider upgrading App Service Plan

## Security Recommendations

1. **HTTPS**: Enabled by default on Azure App Service
2. **Authentication**: Consider enabling Azure AD authentication
3. **Secrets**: Store credentials in Azure Key Vault
4. **Environment Variables**: Use Application Settings for configuration

## Scaling

- **Vertical Scaling**: Upgrade App Service Plan tier
- **Horizontal Scaling**: Enable auto-scaling in App Service Plan
- **Load Balancing**: Automatically handled by Azure App Service

## Cost Estimates

- **Basic B1 Plan**: ~$13/month
- **Standard S1 Plan**: ~$73/month (recommended for production)
- **Blob Storage**: ~$0.01/GB/month

## Support

For issues:
1. Check Azure Portal → App Service → Logs
2. Review Application Insights
3. Check FastAPI documentation

## Next Steps

After deployment:
1. Set up monitoring and alerts
2. Configure custom domain (optional)
3. Set up backup strategy
4. Implement CI/CD pipeline
5. Consider migrating to Azure Blob Storage for file persistence
