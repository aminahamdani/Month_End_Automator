import pandas as pd
import logging
import os
from errors import DataNotFoundError, ProcessingError
from datetime import datetime

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_name):
    """
    Reads a CSV or Excel file into a pandas DataFrame.
    Supports both .csv and .xlsx/.xls files.
    
    Args:
        file_name (str): The path to the file to read.
        
    Returns:
        pd.DataFrame: The loaded data.
        
    Raises:
        DataNotFoundError: If the file is not found.
        ProcessingError: If there are issues processing the file.
    """
    logging.info(f"Loading data from {file_name}")
    
    # Check if file exists
    if not os.path.exists(file_name):
        logging.error(f"File not found: {file_name}")
        raise DataNotFoundError(f"The file '{file_name}' was not found.")
    
    # Check file size (basic validation)
    file_size = os.path.getsize(file_name)
    if file_size == 0:
        logging.error(f"File is empty: {file_name}")
        raise ProcessingError("The file is empty.")
    
    # Determine file type and read accordingly
    file_ext = os.path.splitext(file_name)[1].lower()
    
    try:
        if file_ext == '.csv':
            df = pd.read_csv(file_name)
        elif file_ext in ['.xlsx', '.xls']:
            # Read the first sheet of Excel file
            df = pd.read_excel(file_name, sheet_name=0)
        else:
            raise ProcessingError(f"Unsupported file format: {file_ext}. Supported formats: .csv, .xlsx, .xls")
        
        # Validate DataFrame is not empty
        if df.empty:
            raise ProcessingError("The file contains no data rows.")
        
        # Normalize column names (strip whitespace, handle case sensitivity)
        df.columns = df.columns.str.strip()
        
        # Validation: Check for required columns (case-insensitive)
        amount_columns = [col for col in df.columns if col.lower() == 'amount']
        if not amount_columns:
            available_cols = ', '.join(df.columns.tolist())
            raise ProcessingError(f"Missing required column: 'Amount'. Available columns: {available_cols}")
        
        # If multiple amount columns found, use the first one
        if len(amount_columns) > 1:
            logging.warning(f"Multiple 'Amount' columns found, using: {amount_columns[0]}")
        
        # Rename to standard 'Amount' if needed
        if amount_columns[0] != 'Amount':
            df = df.rename(columns={amount_columns[0]: 'Amount'})
        
        # Validate Amount column contains numeric data
        if not pd.api.types.is_numeric_dtype(df['Amount']):
            # Try to convert to numeric, coercing errors
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            if df['Amount'].isna().all():
                raise ProcessingError("The 'Amount' column contains no valid numeric data.")
        
        # Remove rows with null Amount values
        initial_rows = len(df)
        df = df.dropna(subset=['Amount'])
        if len(df) < initial_rows:
            removed = initial_rows - len(df)
            logging.warning(f"Removed {removed} row(s) with missing Amount values")
        
        # Try to parse date columns if they exist
        date_cols = ['Date', 'date', 'Transaction Date', 'transaction_date', 'Posted Date']
        for col in date_cols:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logging.info(f"Parsed date column: {col}")
                except:
                    pass
        
        logging.info(f"Successfully loaded {len(df)} rows from {file_name}")
        return df
        
    except FileNotFoundError:
        logging.error(f"File not found: {file_name}")
        raise DataNotFoundError(f"The file '{file_name}' was not found.")
    except pd.errors.EmptyDataError:
        logging.error(f"File is empty: {file_name}")
        raise ProcessingError("The file is empty.")
    except ProcessingError:
        # Re-raise our custom errors
        raise
    except Exception as e:
        logging.error(f"Unexpected error reading file: {e}")
        raise ProcessingError(f"An error occurred while reading the file: {str(e)}")
