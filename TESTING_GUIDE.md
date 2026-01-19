# Testing Guide - Login & Dashboard

## 🚀 Quick Start

### 1. Start the Server
```bash
python -m uvicorn main:app --reload
```

### 2. Open Your Browser
Go to: `http://127.0.0.1:8000`

## ✅ Manual Testing Steps

### Test 1: Home Page Redirect
1. Visit `http://127.0.0.1:8000/`
2. **Expected:** Automatically redirected to `/login`
3. **Result:** ✅ Should see login page

### Test 2: Login Page
1. Visit `http://127.0.0.1:8000/login`
2. **Expected:** See "Month End Automator" login page
3. **Check:**
   - Left panel: Logo and description
   - Right panel: Login form with Username/Password fields
   - Green "Sign In" button
4. **Result:** ✅ Login page should load

### Test 3: Failed Login
1. On login page, enter:
   - Username: `admin`
   - Password: `wrongpassword`
2. Click "Sign In"
3. **Expected:** Error message: "Invalid username or password"
4. **Result:** ✅ Error message displayed

### Test 4: Successful Login
1. On login page, enter:
   - Username: `amina`
   - Password: `amina0000`
2. Click "Sign In"
3. **Expected:** Redirected to `/dashboard`
4. **Result:** ✅ Dashboard should load

### Test 5: Dashboard Access
1. After login, you should see the dashboard
2. **Check:**
   - Header: "Month End Automator" logo and "Welcome, admin!"
   - Statistics cards: Total Transactions, Total Amount, Reports Generated, Files Processed
   - Upload section: File upload area
   - Recent Reports: List of recent Excel reports
3. **Result:** ✅ Dashboard displays correctly

### Test 6: File Upload from Dashboard
1. On dashboard, click "Choose File"
2. Select `test_transactions.csv`
3. Click "Upload & Process"
4. **Expected:** 
   - File processed
   - Success message shown
   - Excel report generated
   - File appears in Recent Reports
5. **Result:** ✅ File uploaded and processed

### Test 7: Dashboard Protection (No Auth)
1. Open a new incognito/private window
2. Try to visit `http://127.0.0.1:8000/dashboard`
3. **Expected:** Redirected to `/login` or shown error
4. **Result:** ✅ Dashboard protected

### Test 8: Logout
1. On dashboard, click "Logout" button
2. **Expected:** Redirected to `/login`
3. **Result:** ✅ Logged out successfully

### Test 9: API Endpoints (No Auth)
1. Visit `http://127.0.0.1:8000/health`
2. **Expected:** JSON response: `{"status": "healthy", ...}`
3. **Result:** ✅ API accessible without auth

### Test 10: Login Verification
1. Logout
2. Verify login works with:
   - Username: `amina` / Password: `amina0000`
3. **Expected:** Login successful
4. **Result:** ✅ Login works correctly

## 🔑 Test Credentials

- **Amina:** `amina` / `amina0000`

## 📝 Test Checklist

- [ ] Home redirects to login
- [ ] Login page loads correctly
- [ ] Failed login shows error
- [ ] Successful login redirects to dashboard
- [ ] Dashboard displays statistics
- [ ] File upload works from dashboard
- [ ] Dashboard is protected (requires auth)
- [ ] Logout works correctly
- [ ] API endpoints accessible without auth
- [ ] Multiple users can log in

## 🐛 Troubleshooting

### Server Not Starting
- Check if port 8000 is already in use
- Try: `python -m uvicorn main:app --reload --port 8001`

### Routes Not Found (404)
- Make sure server is running with `--reload`
- Check `templates/login.html` and `templates/dashboard.html` exist
- Verify `main.py` has all route definitions

### Login Not Working
- Check browser console for errors
- Verify session cookies are enabled
- Check server logs for errors

### Dashboard Not Loading
- Make sure you're logged in
- Check browser console for errors
- Verify session is maintained

## ✅ Expected Results

After completing all tests, you should see:
- ✅ Login page with beautiful UI
- ✅ Dashboard with statistics and file upload
- ✅ Secure authentication
- ✅ File processing works from dashboard
- ✅ Recent reports tracking
