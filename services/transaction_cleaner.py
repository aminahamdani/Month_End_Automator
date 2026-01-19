"""
Transaction Cleaner Service

Normalizes and validates transaction data from raw DataFrames.
Provides data cleaning, type inference, validation, and sensitive data masking.
"""
import pandas as pd
import logging
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Critical fields for validation
CRITICAL_FIELDS = {
    'date': ['date', 'transaction_date', 'posted_date', 'transactiondate', 'postdate'],
    'amount': ['amount', 'amt', 'value', 'transaction_amount'],
    'description': ['description', 'desc', 'memo', 'notes', 'details', 'transaction_description']
}

# Sensitive field patterns for masking
SENSITIVE_FIELD_PATTERNS = ['phone', 'account', 'ssn']

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to lowercase with underscores.
    
    Args:
        df: Raw pandas DataFrame
        
    Returns:
        DataFrame with normalized column names
    """
    # Create mapping for normalization
    column_mapping = {}
    for col in df.columns:
        # Convert to lowercase
        normalized = str(col).lower().strip()
        # Replace spaces and special characters with underscores
        normalized = re.sub(r'[^a-z0-9_]+', '_', normalized)
        # Remove multiple consecutive underscores
        normalized = re.sub(r'_+', '_', normalized)
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        
        if normalized and normalized != col:
            column_mapping[col] = normalized
            logging.info(f"Normalizing column '{col}' -> '{normalized}'")
    
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    return df

def infer_column_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Infer and convert column types for dates, amounts, and text.
    
    Args:
        df: DataFrame with normalized column names
        
    Returns:
        DataFrame with inferred types
    """
    df = df.copy()
    
    for col in df.columns:
        col_lower = col.lower()
        
        # Infer date columns
        if any(date_keyword in col_lower for date_keyword in ['date', 'time', 'posted']):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].notna().any():
                    logging.info(f"Inferred date type for column '{col}'")
            except Exception as e:
                logging.warning(f"Could not convert column '{col}' to date: {e}")
        
        # Infer amount/numeric columns
        elif any(amount_keyword in col_lower for amount_keyword in ['amount', 'amt', 'value', 'price', 'cost', 'total']):
            try:
                # Try to convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                if df[col].notna().any():
                    logging.info(f"Inferred numeric type for column '{col}'")
            except Exception as e:
                logging.warning(f"Could not convert column '{col}' to numeric: {e}")
        
        # Ensure text columns are string type
        else:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).replace('nan', '')
                # Log if it's a potential description field
                if any(desc_keyword in col_lower for desc_keyword in ['description', 'desc', 'memo', 'notes', 'details']):
                    logging.info(f"Treated column '{col}' as text")
    
    return df

def flag_missing_critical_fields(df: pd.DataFrame) -> List[Dict]:
    """
    Flag rows with missing critical fields (date, amount, description).
    
    Args:
        df: DataFrame with normalized column names
        
    Returns:
        List of validation issues with row index and field details
    """
    validation_issues = []
    
    # Find critical field columns
    date_col = None
    amount_col = None
    description_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        
        # Find date column
        if not date_col and any(dk in col_lower for dk in CRITICAL_FIELDS['date']):
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_col = col
        
        # Find amount column
        if not amount_col and any(ak in col_lower for ak in CRITICAL_FIELDS['amount']):
            if pd.api.types.is_numeric_dtype(df[col]):
                amount_col = col
        
        # Find description column
        if not description_col and any(dk in col_lower for dk in CRITICAL_FIELDS['description']):
            description_col = col
    
    # Check each row for missing critical fields
    for idx, row in df.iterrows():
        issues = []
        
        if date_col and pd.isna(row.get(date_col)):
            issues.append(f"Missing date in column '{date_col}'")
        
        if amount_col and pd.isna(row.get(amount_col)):
            issues.append(f"Missing amount in column '{amount_col}'")
        
        if description_col:
            desc_value = row.get(description_col, '')
            if pd.isna(desc_value) or str(desc_value).strip() == '':
                issues.append(f"Missing or empty description in column '{description_col}'")
        
        if issues:
            validation_issues.append({
                'row_index': int(idx),
                'issues': issues,
                'has_missing_critical_fields': True
            })
    
    if validation_issues:
        logging.warning(f"Found {len(validation_issues)} rows with missing critical fields")
    else:
        logging.info("No rows with missing critical fields found")
    
    return validation_issues

def mask_sensitive_value(value: str, keep_last: int = 4) -> str:
    """
    Mask a sensitive value, showing only the last N digits/characters.
    
    Args:
        value: The value to mask (will be converted to string)
        keep_last: Number of characters to keep visible (default: 4)
        
    Returns:
        Masked string with all but the last N characters replaced with '*'
    """
    if pd.isna(value) or value is None:
        return value
    
    value_str = str(value).strip()
    
    # If the value is too short, return as is (or minimal masking)
    if len(value_str) <= keep_last:
        # For very short values, mask all but last 1-2 chars
        if len(value_str) <= 1:
            return value_str
        if len(value_str) == 2:
            return '*' + value_str[-1]
        return '*' * (len(value_str) - 1) + value_str[-1]
    
    # Mask all but the last N characters
    masked = '*' * (len(value_str) - keep_last) + value_str[-keep_last:]
    
    return masked

def mask_sensitive_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mask sensitive fields in the DataFrame.
    Applies masking to any column whose name contains 'phone', 'account', or 'ssn'.
    
    Args:
        df: DataFrame with normalized column names
        
    Returns:
        DataFrame with sensitive fields masked
    """
    df = df.copy()
    masked_columns = []
    
    for col in df.columns:
        col_lower = col.lower()
        
        # Check if column name contains any sensitive field pattern
        if any(pattern in col_lower for pattern in SENSITIVE_FIELD_PATTERNS):
            # Mask all values in this column
            df[col] = df[col].apply(mask_sensitive_value)
            masked_columns.append(col)
            logging.info(f"Masked sensitive field: '{col}'")
    
    if masked_columns:
        logging.info(f"Applied masking to {len(masked_columns)} sensitive column(s): {', '.join(masked_columns)}")
    else:
        logging.info("No sensitive fields detected for masking")
    
    return df

def clean_transactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Clean and normalize a DataFrame of raw transactions.
    
    This function:
    1. Normalizes column names (lowercase, underscores)
    2. Infers column types (dates, amounts, text)
    3. Masks sensitive fields (phone, account, ssn)
    4. Flags rows with missing critical fields
    
    Args:
        df: Raw pandas DataFrame of transactions
        
    Returns:
        Tuple of (cleaned DataFrame, list of validation issues)
        Validation issues format:
        [
            {
                'row_index': int,
                'issues': [str, ...],
                'has_missing_critical_fields': bool
            },
            ...
        ]
    """
    if df.empty:
        logging.warning("Empty DataFrame provided to clean_transactions")
        return df, []
    
    logging.info(f"Starting transaction cleaning for {len(df)} rows")
    
    # Step 1: Normalize column names
    df_cleaned = normalize_column_names(df.copy())
    
    # Step 2: Infer column types
    df_cleaned = infer_column_types(df_cleaned)
    
    # Step 3: Mask sensitive fields (phone, account, ssn)
    df_cleaned = mask_sensitive_fields(df_cleaned)
    
    # Step 4: Flag missing critical fields
    validation_issues = flag_missing_critical_fields(df_cleaned)
    
    logging.info(f"Transaction cleaning completed. {len(validation_issues)} validation issues found.")
    
    return df_cleaned, validation_issues
