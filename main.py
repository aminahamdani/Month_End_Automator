from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # Optional if we had static css files, but keeping provided structure
from starlette.middleware.sessions import SessionMiddleware
from processor import load_data
from errors import AppError, DataNotFoundError, ProcessingError
from services.company_service import (
    initialize_default_data, authenticate_user as company_authenticate_user,
    get_user as get_company_user, get_user_company, create_user as create_company_user
)
from services.audit_log import log_action, get_user_activity
import reporter
import shutil
import os
import logging
import pandas as pd
from typing import Optional
from datetime import datetime
from pathlib import Path
import secrets

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize company service and migrate existing users to default company
initialize_default_data()

# Migrate existing hardcoded users to the company service
_existing_users = {
    "amina": "amina0000"
}
for username, password in _existing_users.items():
    try:
        create_company_user(username, password)  # Will default to default company
    except:
        pass  # User might already exist

def get_current_user(request: Request):
    """Check if user is authenticated"""
    return request.session.get("username")

def require_auth(request: Request):
    """Dependency to require authentication"""
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return username

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Redirect to login or dashboard based on auth status"""
    username = get_current_user(request)
    if username:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """Display login page"""
    username = get_current_user(request)
    if username:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login"""
    user = company_authenticate_user(username, password)
    if user:
        request.session["username"] = username
        request.session["company_id"] = user.get("company_id")
        log_action(username, "user_login", {"username": username})
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })

@app.get("/logout")
async def logout(request: Request):
    """Handle logout"""
    username = get_current_user(request)
    if username:
        log_action(username, "user_logout", {"username": username})
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Display dashboard - requires authentication"""
    username = require_auth(request)
    
    # Get user info
    user = get_company_user(username)
    company = get_user_company(username) if user else None
    
    # Get recent activity
    recent_activity = get_user_activity(username, limit=10)
    
    # Get recent files and calculate statistics from uploaded transaction files
    recent_files = []
    total_transactions = 0
    total_amount = 0.0
    uploaded_files_count = 0
    
    try:
        uploads_dir = Path("data/uploads")
        if uploads_dir.exists():
            # Get all uploaded transaction files (CSV/Excel files that were uploaded)
            uploaded_files = [f for f in os.listdir(uploads_dir) if f.startswith('uploaded_transactions_') and f.endswith(('.csv', '.xlsx', '.xls'))]
            uploaded_files_count = len(uploaded_files)
            
            # Calculate total transactions and amount from all uploaded files
            for uploaded_file in uploaded_files:
                try:
                    file_path = uploads_dir / uploaded_file
                    df = load_data(str(file_path))
                    
                    # Count transactions (rows)
                    total_transactions += len(df)
                    
                    # Sum all amounts
                    if 'Amount' in df.columns:
                        amounts = pd.to_numeric(df['Amount'], errors='coerce')
                        valid_amounts = amounts.dropna()
                        total_amount += float(valid_amounts.sum())
                except Exception as e:
                    logging.error(f"Error processing {uploaded_file} for stats: {e}")
                    pass
            
            # Get recent report files for display
            files = [f for f in os.listdir(uploads_dir) if f.endswith(('.xlsx', '.xls')) and f.startswith('Month_End_Report_')]
            files_with_paths = [(uploads_dir / f, f) for f in files]
            files_with_paths.sort(key=lambda x: os.path.getmtime(x[0]), reverse=True)
            for file_path, filename in files_with_paths[:5]:
                recent_files.append({
                    "name": filename,
                    "date": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                })
    except Exception as e:
        logging.error(f"Error getting recent files and stats: {e}")
        pass
    
    # Get stats (simplified - in production, use database)
    stats = {
        "total_transactions": total_transactions,
        "total_amount": total_amount,
        "reports_generated": len(recent_files),
        "files_processed": uploaded_files_count,
        "last_file_processed_at": recent_files[0]["date"] if recent_files else None,
        "last_report_generated_at": recent_files[0]["date"] if recent_files else None
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": username,
        "stats": stats,
        "recent_files": recent_files,
        "recent_activity": recent_activity,
        "validation_issues": []  # Would come from database in production
    })

@app.post("/api/upload")
async def api_upload(request: Request, file: UploadFile = File(...)):
    """API endpoint for file upload - requires authentication"""
    username = require_auth(request)
    
    # Generate timestamp-based filenames for better organization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file.filename)[1] or '.csv'
    uploaded_filename = f"uploaded_transactions_{timestamp}{file_ext}"
    report_filename = f"Month_End_Report_{timestamp}.xlsx"
    
    try:
        # Ensure uploads directory exists
        uploads_dir = Path("data/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the uploaded file
        upload_path = uploads_dir / uploaded_filename
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the data
        df = load_data(str(upload_path))
        
        # Generate the report
        report_path = uploads_dir / report_filename
        reporter.create_excel_report(df, str(report_path))
        
        # Log the action
        log_action(username, "file_upload", {
            "filename": uploaded_filename,
            "report_filename": report_filename,
            "rows_processed": len(df)
        })
        
        return JSONResponse(content={
            "status": "success",
            "filename": report_filename,
            "uploaded_at": datetime.now().isoformat(),
            "rows_processed": len(df)
        })

    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=f"Processing error: {str(e)}")
    except AppError as e:
        raise HTTPException(status_code=500, detail=f"Application error: {str(e)}")
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logging.error(f"Unhandled exception in api_upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_message)

@app.get("/download/{filename}")
async def download_file(request: Request, filename: str):
    """Download a file - requires authentication"""
    username = require_auth(request)
    
    # Check in uploads directory first, then current directory
    uploads_dir = Path("data/uploads")
    file_path = uploads_dir / filename
    if not file_path.exists():
        file_path = Path(filename)
    
    if file_path.exists():
        log_action(username, "file_download", {"filename": filename})
        return FileResponse(str(file_path), filename=filename)
    raise HTTPException(status_code=404, detail="File not found")


@app.post("/api/export/{filename}")
async def export_file(filename: str, format: str = "json"):
    """
    Export transaction data to different formats: json, csv, xlsx
    """
    file_path = os.path.join(os.getcwd(), filename)
    
    try:
        df = load_data(file_path)
        
        if format.lower() == "json":
            json_data = df.to_dict(orient='records')
            return JSONResponse(content={"data": json_data, "count": len(json_data)})
        
        elif format.lower() == "csv":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"export_{timestamp}.csv"
            export_path = os.path.join(os.getcwd(), export_filename)
            df.to_csv(export_path, index=False)
            return FileResponse(export_path, filename=export_filename, media_type='text/csv')
        
        elif format.lower() == "xlsx":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"export_{timestamp}.xlsx"
            export_path = os.path.join(os.getcwd(), export_filename)
            df.to_excel(export_path, index=False)
            return FileResponse(export_path, filename=export_filename, 
                              media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Supported: json, csv, xlsx")
            
    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppError as e:
        raise HTTPException(status_code=500, detail=f"Application Error: {str(e)}")

@app.get("/transactions")
def get_transactions(
    filename: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Reads transaction data and returns it as JSON with optional filtering.
    
    Query parameters:
    - filename: Optional filename (defaults to 'january_transactions.csv')
    - min_amount: Minimum amount filter
    - max_amount: Maximum amount filter  
    - search: Search term to filter by (searches in all string columns)
    """
    # Default to january_transactions.csv if no filename provided
    if not filename:
        filename = 'january_transactions.csv'
    
    file_path = os.path.join(os.getcwd(), filename)
    
    try:
        df = load_data(file_path)
        
        # Apply filters if provided
        if min_amount is not None:
            df = df[df['Amount'] >= min_amount]
        
        if max_amount is not None:
            df = df[df['Amount'] <= max_amount]
        
        if search:
            # Search in all string columns
            search_mask = pd.Series([False] * len(df))
            for col in df.columns:
                if df[col].dtype == 'object':  # String columns
                    search_mask |= df[col].astype(str).str.contains(search, case=False, na=False)
            df = df[search_mask]
        
        # Apply date filters if provided
        date_cols = ['Date', 'date', 'Transaction Date', 'transaction_date', 'Posted Date']
        date_col = None
        for col in date_cols:
            if col in df.columns and pd.api.types.is_datetime64_any_dtype(df[col]):
                date_col = col
                break
        
        if date_col:
            if start_date:
                try:
                    start = pd.to_datetime(start_date)
                    df = df[df[date_col] >= start]
                except:
                    pass
            
            if end_date:
                try:
                    end = pd.to_datetime(end_date)
                    df = df[df[date_col] <= end]
                except:
                    pass
        
        # Convert DataFrame to a list of dictionaries (JSON records)
        return {
            "data": df.to_dict(orient='records'),
            "count": len(df),
            "filters_applied": {
                "min_amount": min_amount,
                "max_amount": max_amount,
                "search": search,
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppError as e:
        raise HTTPException(status_code=500, detail=f"Application Error: {str(e)}")


@app.post("/preview")
async def preview_file(file: UploadFile = File(...), rows: int = 10):
    """
    Preview the first N rows of an uploaded file without saving it permanently.
    Useful for validating file format before processing.
    """
    temp_filename = f"temp_preview_{file.filename}"
    
    try:
        # Save temporarily
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Load and preview
        file_path = os.path.join(os.getcwd(), temp_filename)
        df = load_data(file_path)
        
        # Get preview (first N rows)
        preview_df = df.head(min(rows, len(df)))
        
        return {
            "total_rows": len(df),
            "preview_rows": len(preview_df),
            "columns": df.columns.tolist(),
            "data": preview_df.to_dict(orient='records')
        }
    except (DataNotFoundError, ProcessingError, AppError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error previewing file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error previewing file: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except:
                pass


@app.get("/api/stats/{filename}")
def get_file_statistics(filename: str):
    """
    Get statistics for a specific file without generating a full report.
    Returns summary statistics as JSON.
    """
    file_path = os.path.join(os.getcwd(), filename)
    
    try:
        df = load_data(file_path)
        stats = reporter.calculate_summary_statistics(df)
        
        return {
            "filename": filename,
            "statistics": stats,
            "columns": df.columns.tolist(),
            "row_count": len(df)
        }
    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppError as e:
        raise HTTPException(status_code=500, detail=f"Application Error: {str(e)}")


@app.get("/api/files")
def list_available_files():
    """
    List all available transaction files in the current directory.
    """
    try:
        csv_files = [f for f in os.listdir(os.getcwd()) if f.endswith(('.csv', '.xlsx', '.xls'))]
        return {
            "files": csv_files,
            "count": len(csv_files)
        }
    except Exception as e:
        logging.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@app.get("/api/period-analysis/{filename}")
def get_period_analysis(filename: str, period: str = "month"):
    """
    Analyze transactions by time period (day, week, month, year).
    
    Args:
        filename: The transaction file to analyze
        period: Analysis period - 'day', 'week', 'month', or 'year'
    """
    file_path = os.path.join(os.getcwd(), filename)
    
    try:
        df = load_data(file_path)
        
        # Find date column
        date_cols = ['Date', 'date', 'Transaction Date', 'transaction_date', 'Posted Date']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                try:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    break
                except:
                    pass
        
        if not date_col or 'Amount' not in df.columns:
            raise HTTPException(status_code=400, detail="Date column not found or Amount column missing")
        
        # Group by period
        if period == "day":
            df['Period'] = df[date_col].dt.date
        elif period == "week":
            df['Period'] = df[date_col].dt.to_period('W').astype(str)
        elif period == "month":
            df['Period'] = df[date_col].dt.to_period('M').astype(str)
        elif period == "year":
            df['Period'] = df[date_col].dt.to_period('Y').astype(str)
        else:
            raise HTTPException(status_code=400, detail="Invalid period. Use: day, week, month, or year")
        
        period_analysis = df.groupby('Period')['Amount'].agg([
            ('Total', 'sum'),
            ('Count', 'count'),
            ('Average', 'mean'),
            ('Min', 'min'),
            ('Max', 'max')
        ]).reset_index()
        
        return {
            "filename": filename,
            "period": period,
            "analysis": period_analysis.to_dict(orient='records')
        }
        
    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppError as e:
        raise HTTPException(status_code=500, detail=f"Application Error: {str(e)}")


@app.get("/health")
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {
        "status": "healthy",
        "service": "Month-End Close Automator",
        "version": "2.0.0"
    }
