from fastapi import FastAPI, HTTPException
from processor import load_data
from errors import AppError, DataNotFoundError, ProcessingError
import os

app = FastAPI()

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
