import pandas as pd
import logging
from errors import DataNotFoundError, ProcessingError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_name):
    """
    Reads a CSV file directly into a pandas DataFrame.
    
    Args:
        file_name (str): The path to the CSV file to read.
        
    Returns:
        pd.DataFrame: The loaded data, or None if an error occurs.
    """
    logging.info(f"Loading data from {file_name}")
    try:
        df = pd.read_csv(file_name)
        
        # Validation: Check for required columns
        if 'Amount' not in df.columns:
            raise ProcessingError("Missing required column: 'Amount'")
            
        return df
    except FileNotFoundError:
        logging.error(f"File not found: {file_name}")
        raise DataNotFoundError(f"The file '{file_name}' was not found.")
    except pd.errors.EmptyDataError:
        logging.error(f"File is empty: {file_name}")
        raise ProcessingError("The file is empty.")
    except Exception as e:
        logging.error(f"Unexpected error reading file: {e}")
        raise ProcessingError(f"An error occurred while reading the file: {e}")
