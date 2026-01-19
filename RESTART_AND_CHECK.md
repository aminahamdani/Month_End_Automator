# Restart and Health Check Commands

Quick commands to restart your Azure App Service and verify it's running.

## Quick Commands

### 1. Restart App Service
```powershell
az webapp restart --name month-end-automator --resource-group month-end-automator-rg
```

### 2. Check App Service Status
```powershell
az webapp show --name month-end-automator --resource-group month-end-automator-rg --query "{State:state, Availability:availabilityState, URL:defaultHostName}" --output table
```

### 3. Get Full App Service Details
```powershell
az webapp show --name month-end-automator --resource-group month-end-automator-rg
```

### 4. Check App URL Health
```powershell
# PowerShell - Test if app is responding
Invoke-WebRequest -Uri "https://month-end-automator.azurewebsites.net" -UseBasicParsing

# Or using curl (if available)
curl -I https://month-end-automator.azurewebsites.net
```

### 5. View Live Logs
```powershell
az webapp log tail --name month-end-automator --resource-group month-end-automator-rg
```

## Using the Script

Run the provided PowerShell script:
```powershell
.\restart_and_check_azure.ps1
```

This will:
- Restart the App Service
- Wait for restart to complete
- Check the app status
- Test if the app is responding at the URL
- Show summary

## Manual Verification Steps

1. **Restart the app:**
   ```powershell
   az webapp restart --name month-end-automator --resource-group month-end-automator-rg
   ```

2. **Wait 10-20 seconds** for the app to fully restart

3. **Check status:**
   ```powershell
   az webapp show --name month-end-automator --resource-group month-end-automator-rg
   ```

4. **Visit in browser:**
   - Open: `https://month-end-automator.azurewebsites.net`
   - Should see login page or redirect to `/login`
   - Login with: `amina` / `amina0000`

5. **Check health endpoint (if available):**
   ```powershell
   Invoke-WebRequest -Uri "https://month-end-automator.azurewebsites.net/health" -UseBasicParsing
   ```

## Troubleshooting

**If app doesn't respond:**
- Wait 30-60 seconds after restart
- Check logs: `az webapp log tail --name month-end-automator --resource-group month-end-automator-rg`
- Verify App Service is running: `az webapp show --name month-end-automator --resource-group month-end-automator-rg --query state`

**Common status codes:**
- `200 OK` - App is running
- `302 Redirect` - App redirecting (normal for login)
- `502 Bad Gateway` - App still starting or error
- `503 Service Unavailable` - App is down or starting

**Check deployment:**
```powershell
az webapp deployment list-publishing-profiles --name month-end-automator --resource-group month-end-automator-rg
```

## Expected Health Check Results

✅ **Healthy:**
- Status Code: 200 or 302
- App URL accessible
- Login page loads

⚠️ **Starting:**
- Status Code: 502 or 503
- Wait 30-60 seconds and retry

❌ **Unhealthy:**
- Status Code: 500
- Check logs for errors
- Verify startup command is correct
