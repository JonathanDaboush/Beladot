"""Input sanitization and validation utilities."""
import re
import html
from typing import Any, Optional


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent XSS attacks.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string safe for storage and display
        
    Example:
        >>> sanitize_string("<script>alert('xss')</script>")
        "&lt;script&gt;alert('xss')&lt;/script&gt;"
    """
    if not value:
        return ""
    
    # Trim to max length
    value = value[:max_length]
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # HTML escape to prevent XSS
    value = html.escape(value)
    
    # Strip leading/trailing whitespace
    return value.strip()


def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize SQL identifiers (table/column names) for dynamic queries.
    
    WARNING: Use ONLY in admin scripts, NEVER with user input.
    Always prefer SQLAlchemy ORM over dynamic SQL.
    
    Args:
        identifier: Table or column name to validate
        
    Returns:
        Validated identifier
        
    Raises:
        ValueError: If identifier contains invalid characters
        
    Example:
        >>> sanitize_sql_identifier("users")
        "users"
        >>> sanitize_sql_identifier("users; DROP TABLE")
        ValueError: Invalid SQL identifier
    """
    # Only allow alphanumeric and underscore, must start with letter/underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier}")
    
    # Reject SQL keywords
    sql_keywords = {'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate'}
    if identifier.lower() in sql_keywords:
        raise ValueError(f"SQL keyword not allowed as identifier: {identifier}")
    
    return identifier


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
        
    Note:
        Use Pydantic's EmailStr for more robust validation.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to prevent directory traversal attacks.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename
        
    Example:
        >>> sanitize_filename("../../etc/passwd")
        "passwd"
        >>> sanitize_filename("report<script>.pdf")
        "reportscript.pdf"
    """
    # Remove directory separators
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Allow only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')
    
    # Trim to max length
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if ext:
            name = name[:max_length - len(ext) - 1]
            filename = f"{name}.{ext}"
        else:
            filename = filename[:max_length]
    
    return filename or 'unnamed'


def sanitize_url(url: str) -> Optional[str]:
    """
    Validate and sanitize URL to prevent SSRF attacks.
    
    Args:
        url: URL to validate
        
    Returns:
        Sanitized URL or None if invalid
        
    Note:
        This is basic validation. For production, use URL parsing
        libraries and whitelist allowed domains.
    """
    # Only allow http/https
    if not url.startswith(('http://', 'https://')):
        return None
    
    # Block local/private IP addresses (prevent SSRF)
    blocked_patterns = [
        r'localhost',
        r'127\.0\.0\.1',
        r'0\.0\.0\.0',
        r'10\.\d+\.\d+\.\d+',
        r'172\.(1[6-9]|2[0-9]|3[01])\.\d+\.\d+',
        r'192\.168\.\d+\.\d+',
        r'\[::1\]',
        r'\[::ffff:127\.0\.0\.1\]'
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return None
    
    return url


def sanitize_phone_number(phone: str) -> str:
    """
    Sanitize phone number (remove non-numeric characters).
    
    Args:
        phone: Phone number string
        
    Returns:
        Digits only
    """
    return re.sub(r'[^0-9+]', '', phone)


def check_for_sql_keywords(text: str) -> bool:
    """
    Check if text contains SQL keywords (defense in depth).
    
    Args:
        text: Text to check
        
    Returns:
        True if SQL keywords found (suspicious)
        
    Note:
        This is NOT a substitute for parameterized queries.
        Use only as an additional security layer.
    """
    sql_keywords = [
        'select', 'insert', 'update', 'delete', 'drop', 'create',
        'alter', 'truncate', 'exec', 'execute', 'union', 'declare',
        'script', 'javascript', 'onerror', 'onload'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in sql_keywords)
