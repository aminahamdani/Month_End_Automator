from fastapi import FastAPI
from processor import load_data
import os

app = FastAPI()

@app.get("/transactions")
def get_transactions():
    """
    Reads the January transactions CSV and returns it as JSON.
    """
    # Ensure we look for the file in the current directory
    file_path = os.path.join(os.getcwd(), 'january_transactions.csv')
    
    df = load_data(file_path)
    
    if df is not None:
        # Convert DataFrame to a list of dictionaries (JSON records)
        return df.to_dict(orient='records')
    else:
        return {"error": "Could not load data. Check if 'january_transactions.csv' exists."}
