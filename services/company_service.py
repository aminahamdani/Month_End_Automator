"""
Company Service

Manages company data and relationships.
Supports multiple companies with users, files, and reports linked to companies.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for companies
# Format: {company_id: {id, name, created_at}}
_companies: Dict[int, Dict] = {}
_company_id_counter: int = 0

# In-memory storage for users (enhanced with company_id)
# Format: {username: {username, password, company_id}}
_users: Dict[str, Dict] = {}

def create_company(name: str) -> Dict:
    """
    Create a new company.
    
    Args:
        name: Name of the company
        
    Returns:
        Dictionary representing the created company:
        {
            'id': int,
            'name': str,
            'created_at': str (ISO format)
        }
    """
    global _company_id_counter
    
    _company_id_counter += 1
    
    company = {
        'id': _company_id_counter,
        'name': name,
        'created_at': datetime.now().isoformat()
    }
    
    _companies[_company_id_counter] = company
    
    logging.info(f"Company created: {name} (ID: {_company_id_counter})")
    
    return company

def get_company(company_id: int) -> Optional[Dict]:
    """
    Get a company by ID.
    
    Args:
        company_id: ID of the company
        
    Returns:
        Company dictionary or None if not found
    """
    return _companies.get(company_id)

def get_all_companies() -> List[Dict]:
    """
    Get all companies.
    
    Returns:
        List of company dictionaries
    """
    return list(_companies.values())

def get_or_create_default_company() -> Dict:
    """
    Get or create the default company.
    Used for backward compatibility with existing data.
    
    Returns:
        Company dictionary for the default company
    """
    # Check if default company already exists
    for company in _companies.values():
        if company['name'] == 'Default Company':
            return company
    
    # Create default company if it doesn't exist
    return create_company('Default Company')

def create_user(username: str, password: str, company_id: Optional[int] = None) -> Dict:
    """
    Create a user linked to a company.
    
    Args:
        username: Username for the user
        password: Password for the user
        company_id: Optional company ID. If None, assigns to default company.
        
    Returns:
        Dictionary representing the created user:
        {
            'username': str,
            'password': str,
            'company_id': int
        }
    """
    # If no company_id provided, use default company
    if company_id is None:
        default_company = get_or_create_default_company()
        company_id = default_company['id']
    
    # Verify company exists
    if company_id not in _companies:
        raise ValueError(f"Company ID {company_id} does not exist")
    
    user = {
        'username': username,
        'password': password,
        'company_id': company_id
    }
    
    _users[username] = user
    
    logging.info(f"User created: {username} (Company ID: {company_id})")
    
    return user

def get_user(username: str) -> Optional[Dict]:
    """
    Get a user by username.
    
    Args:
        username: Username of the user
        
    Returns:
        User dictionary or None if not found
    """
    return _users.get(username)

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user by username and password.
    
    Args:
        username: Username of the user
        password: Password of the user
        
    Returns:
        User dictionary if authentication succeeds, None otherwise
    """
    user = _users.get(username)
    if user and user['password'] == password:
        return user
    return None

def get_user_company(username: str) -> Optional[Dict]:
    """
    Get the company for a user.
    
    Args:
        username: Username of the user
        
    Returns:
        Company dictionary or None if user not found
    """
    user = _users.get(username)
    if user:
        return _companies.get(user['company_id'])
    return None

def initialize_default_data():
    """
    Initialize default company and migrate existing users.
    This ensures backward compatibility with existing data.
    """
    # Create default company if it doesn't exist
    default_company = get_or_create_default_company()
    
    logging.info(f"Default company initialized: {default_company['name']} (ID: {default_company['id']})")
