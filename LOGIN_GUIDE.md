# Login & Dashboard Guide

## 🔐 Login Credentials

The application now includes a secure login system. Use these credentials to access:

**Default Users:**
- **Username:** `amina` | **Password:** `amina0000`

## 🚀 Getting Started

1. **Start the Server:**
   ```bash
   python -m uvicorn main:app --reload
   ```

2. **Access the Application:**
   - Open your browser: `http://127.0.0.1:8000`
   - You'll be redirected to the login page

3. **Login:**
   - Enter your username and password
   - Click "Sign In"
   - You'll be redirected to the dashboard

## 📊 Dashboard Features

### Overview Statistics
- **Total Transactions:** Count of all processed transactions
- **Total Amount:** Sum of all transaction amounts
- **Reports Generated:** Number of Excel reports created
- **Files Processed:** Number of transaction files uploaded

### Upload Transactions
- Drag and drop or select CSV/Excel files
- Files are automatically processed
- Reports are generated with timestamp-based naming

### Recent Reports
- View your 5 most recent reports
- Download reports directly from the dashboard
- See when each report was generated

## 🔒 Security Notes

- **MVP Implementation:** Current authentication uses simple username/password matching
- **Production Ready:** For production use, implement:
  - Password hashing (bcrypt, argon2)
  - Database storage for users
  - Session expiration
  - CSRF protection
  - Rate limiting

## 🛣️ Routes

### Protected Routes (Require Login)
- `/dashboard` - Main dashboard
- `/dashboard/upload` - File upload from dashboard

### Public Routes
- `/login` - Login page
- `/logout` - Logout
- `/` - Redirects to login or dashboard based on auth status

### API Routes (No Auth Required)
- `/transactions` - Get transaction data
- `/api/stats/{filename}` - Get statistics
- `/api/export/{filename}` - Export data
- `/api/period-analysis/{filename}` - Period analysis
- `/health` - Health check

## 🎨 Design

The login page is styled similar to the NYC Public Schools login page with:
- **Left Panel:** Branding, logo, and description
- **Right Panel:** Clean login form
- **Modern UI:** Gradient backgrounds, smooth animations
- **Responsive Design:** Works on mobile and desktop
