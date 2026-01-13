import pandas as pd
from processor import load_data

def main():
    # Set display options for better visibility in terminal
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    # Use the modular load_data function
    df = load_data('january_transactions.csv')
    
    if df is not None:
        print("January Transactions:")
        print("-" * 50)
        print(df)
        print("-" * 50)

if __name__ == "__main__":
    main()
