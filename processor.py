import pandas as pd

def load_data(file_name):
    """
    Reads a CSV file directly into a pandas DataFrame.
    
    Args:
        file_name (str): The path to the CSV file to read.
        
    Returns:
        pd.DataFrame: The loaded data, or None if an error occurs.
    """
    try:
        return pd.read_csv(file_name)
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None
