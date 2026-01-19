# Month-End Close Automator

## Description
A professional web application built to automate the month-end close process for accounting teams. This application streamlines transaction processing, generates comprehensive Excel reports, and provides a secure, user-friendly dashboard for managing financial data.

**Live Application**: [https://month-end-automator-a7gpcmeucqacgzch.canadacentral-01.azurewebsites.net](https://month-end-automator-a7gpcmeucqacgzch.canadacentral-01.azurewebsites.net)

## Features

### 🔐 Authentication & Security
- Secure login system with session management
- User authentication via company service
- Protected routes requiring authentication
- Audit logging for all user actions

### 📊 Dashboard
- Real-time statistics and metrics
- File upload with drag-and-drop support
- Recent reports and activity tracking
- Data quality validation

### 📈 Reporting
- Automated Excel report generation
- Professional styling with currency formatting
- Transaction reconciliation summaries
- Multiple export formats (JSON, CSV, XLSX)

### 🚀 Deployment
- Deployed on Azure App Service
- GitHub Actions CI/CD pipeline
- Automatic deployments on push to main
- Health check monitoring

## Architecture

This project follows a modular architecture for maintainability and scalability:

### Core Files
*   **`main.py`**: FastAPI web server with authentication, routes, and API endpoints
*   **`processor.py`**: Data processing and validation logic
*   **`reporter.py`**: Excel report generation with professional styling
*   **`errors.py`**: Centralized error handling and custom exceptions

### Services
*   **`services/company_service.py`**: User and company management
*   **`services/audit_log.py`**: Activity logging and audit trails
*   **`services/reconciliation.py`**: Financial reconciliation calculations
*   **`services/transaction_cleaner.py`**: Data cleaning and validation

### Templates
*   **`templates/login.html`**: Secure login page
*   **`templates/dashboard.html`**: Main dashboard interface
*   **`templates/index.html`**: Legacy upload interface

## Installation

### Prerequisites
- Python 3.10+
- pip package manager

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/aminahamdani/Month_End_Automator.git
   cd Month_End_Automator
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Usage

### Local Development

1. **Run the server:**
   ```bash
   python -m uvicorn main:app --reload
   ```

2. **Access the application:**
   - Open your browser to: `http://127.0.0.1:8000`
   - You'll be redirected to the login page

3. **Login:**
   - Username: `amina`
   - Password: `amina0000`

4. **Use the dashboard:**
   - Upload transaction files (CSV or Excel)
   - View statistics and recent reports
   - Download generated reports

### REST API Endpoints

#### Public Endpoints
- `GET /health` - Health check endpoint
- `GET /login` - Login page
- `POST /login` - Authenticate user

#### Protected Endpoints (Require Authentication)
- `GET /dashboard` - Main dashboard
- `POST /api/upload` - Upload transaction file
- `GET /download/{filename}` - Download report
- `GET /transactions` - Get transaction data with filtering
- `POST /api/export/{filename}` - Export data in various formats
- `GET /api/stats/{filename}` - Get file statistics
- `GET /api/period-analysis/{filename}` - Period-based analysis

## Deployment

### Azure App Service
The application is deployed on Azure App Service with:
- **Runtime**: Python 3.10
- **Platform**: Linux
- **CI/CD**: GitHub Actions
- **Health Check**: Configured at `/health`

See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy
See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for the fastest deployment method.

## Documentation

- [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) - Complete Azure deployment guide
- [LOGIN_GUIDE.md](LOGIN_GUIDE.md) - Login and dashboard usage
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing instructions
- [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - Quick deployment guide

## Dependencies

Key dependencies (see `requirements.txt` for complete list):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `gunicorn` - Production WSGI server
- `pandas` - Data processing
- `openpyxl` - Excel file generation
- `jinja2` - Template engine
- `requests` - HTTP library

## Project Structure

```
Month_End_Automator/
├── main.py                 # FastAPI application
├── processor.py            # Data processing
├── reporter.py             # Report generation
├── errors.py               # Error handling
├── requirements.txt        # Dependencies
├── services/               # Service modules
│   ├── company_service.py
│   ├── audit_log.py
│   ├── reconciliation.py
│   └── transaction_cleaner.py
├── templates/              # HTML templates
│   ├── login.html
│   ├── dashboard.html
│   └── index.html
├── .github/workflows/      # CI/CD workflows
└── docs/                   # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues or questions, please open an issue on GitHub.
