import requests
import pandas as pd
from openpyxl.styles import Font

def generate_report():
    """
    Fetches transaction data from the local FastAPI server and saves it to an Excel file
    with formatted headers.
    """
    url = "http://127.0.0.1:8000/transactions"
    output_file = "January_Closing_Report.xlsx"

    try:
        print(f"Fetching data from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle potential error response from the server logic
        if isinstance(data, dict) and "error" in data:
            print(f"Server Error: {data['error']}")
            return

        print("Data received. Converting to DataFrame...")
        df = pd.DataFrame(data)

        print(f"Saving to {output_file}...")
        create_excel_report(df, output_file)

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Is main.py running?")
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def create_excel_report(df, output_file):
    """
    Generates a styled Excel report from a DataFrame.
    """
    # Use a context manager to handle the usage of the ExcelWriter
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='January_Transactions')
        
        # Access the workbook and sheet for formatting
        workbook = writer.book
        worksheet = writer.sheets['January_Transactions']
        
        # Apply bold formatting to the header row (Row 1)
        header_font = Font(bold=True)
        for cell in worksheet[1]:
            cell.font = header_font

        # Apply currency format to 'Amount' column
        # Find the 'Amount' column index (1-based)
        amount_col_idx = None
        for idx, col_name in enumerate(df.columns, 1):
            if col_name == 'Amount':
                amount_col_idx = idx
                break
        
        if amount_col_idx:
            for row in range(2, worksheet.max_row + 1):
                cell = worksheet.cell(row=row, column=amount_col_idx)
                cell.number_format = '$#,##0.00'

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    print(f"Success! Report saved as {output_file}")

if __name__ == "__main__":
    generate_report()
