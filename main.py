from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # Optional if we had static css files, but keeping provided structure
from processor import load_data
from errors import AppError, DataNotFoundError, ProcessingError
import reporter
import shutil
import os
import logging
import pandas as pd
from typing import Optional
from datetime import datetime

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    # Generate timestamp-based filenames for better organization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file.filename)[1] or '.csv'
    uploaded_filename = f"uploaded_transactions_{timestamp}{file_ext}"
    report_filename = f"Month_End_Report_{timestamp}.xlsx"
    
    try:
        # Save the uploaded file
        with open(uploaded_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the data
        # Ensure we use absolute path for safety
        file_path = os.path.join(os.getcwd(), uploaded_filename)
        df = load_data(file_path)
        
        # Generate the report
        reporter.create_excel_report(df, report_filename)
        
        # Return success page with download link
        return templates.TemplateResponse("index.html", {
            "request": request,
            "download_link": f"/download/{report_filename}"
        })

    except DataNotFoundError as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"File not found: {str(e)}. Please ensure the file was uploaded correctly."
        })
    except ProcessingError as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Processing error: {str(e)}. Please check your CSV file format and ensure it contains an 'Amount' column."
        })
    except AppError as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Application error: {str(e)}. Please try again or contact support if the issue persists."
        })
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logging.error(f"Unhandled exception in upload_file: {e}", exc_info=True)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": error_message
        })

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
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
