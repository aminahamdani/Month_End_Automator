from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # Optional if we had static css files, but keeping provided structure
from processor import load_data
from errors import AppError, DataNotFoundError, ProcessingError
import reporter
import shutil
import os

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    uploaded_filename = "uploaded_transactions.csv"
    report_filename = "Month_End_Report_Generated.xlsx"
    
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

    except AppError as e:
        # For UI, we might want to return the error execution in the template, 
        # but for now sticking to the API error mapping or a simple error page
         return templates.TemplateResponse("index.html", {"request": request, "error": str(e)}) # Simple handling
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/transactions")
def get_transactions():
    """
    Reads the January transactions CSV and returns it as JSON.
    """
    # Ensure we look for the file in the current directory
    file_path = os.path.join(os.getcwd(), 'january_transactions.csv')
    
    try:
        df = load_data(file_path)
        # Convert DataFrame to a list of dictionaries (JSON records)
        return df.to_dict(orient='records')
    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppError as e:
        raise HTTPException(status_code=500, detail=f"Application Error: {str(e)}")
