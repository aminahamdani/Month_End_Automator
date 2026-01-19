"""
Reconciliation Service

Calculates reconciliation summary from transaction data.
Computes total debits, credits (inflows/outflows), and net difference.
"""
import pandas as pd
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_reconciliation_summary(df: pd.DataFrame) -> Dict:
    """
    Calculate reconciliation summary from transaction DataFrame.
    
    Computes:
    - Total debits (negative amounts or outflows)
    - Total credits (positive amounts or inflows)
    - Net difference (credits - debits)
    
    Args:
        df: pandas DataFrame with transaction data
        
    Returns:
        Dictionary with reconciliation summary:
        {
            'total_debits': float,
            'total_credits': float,
            'net_difference': float
        }
    """
    if df.empty:
        logging.warning("Empty DataFrame provided to calculate_reconciliation_summary")
        return {
            'total_debits': 0.0,
            'total_credits': 0.0,
            'net_difference': 0.0
        }
    
    if 'Amount' not in df.columns:
        logging.warning("Amount column not found in DataFrame")
        return {
            'total_debits': 0.0,
            'total_credits': 0.0,
            'net_difference': 0.0
        }
    
    # Convert Amount to numeric if needed
    amounts = pd.to_numeric(df['Amount'], errors='coerce')
    valid_amounts = amounts.dropna()
    
    if len(valid_amounts) == 0:
        logging.warning("No valid amounts found in DataFrame")
        return {
            'total_debits': 0.0,
            'total_credits': 0.0,
            'net_difference': 0.0
        }
    
    # Calculate debits (negative amounts or outflows)
    debits = valid_amounts[valid_amounts < 0]
    total_debits = abs(debits.sum()) if len(debits) > 0 else 0.0
    
    # Calculate credits (positive amounts or inflows)
    credits = valid_amounts[valid_amounts > 0]
    total_credits = credits.sum() if len(credits) > 0 else 0.0
    
    # Calculate net difference (credits - debits)
    # Note: debits are stored as negative, so we add them (subtract absolute value)
    net_difference = total_credits - total_debits
    
    logging.info(f"Reconciliation summary: Credits=${total_credits:,.2f}, Debits=${total_debits:,.2f}, Net=${net_difference:,.2f}")
    
    return {
        'total_debits': float(total_debits),
        'total_credits': float(total_credits),
        'net_difference': float(net_difference)
    }
