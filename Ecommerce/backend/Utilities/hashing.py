"""Password hashing utilities for secure credential storage.

Provides bcrypt-based password hashing with automatic salt generation.
Never stores passwords in plain text - always hash before database storage.

Security Properties:
    - One-way function: Cannot reverse hash to get password
    - Salt: Random salt prevents rainbow table attacks
    - Adaptive: Configurable work factor (cost) for future-proofing
    - Timing-safe: Constant-time comparison prevents timing attacks

Algorithm Choice:
    - bcrypt: Industry standard, well-tested, wide support
    - Argon2: Modern, memory-hard, resistant to GPU attacks (recommended for new projects)
    - PBKDF2: Older standard, still secure but slower than bcrypt

Best Practices:
    - Never log passwords (even hashed)
    - Use HTTPS for password transmission
    - Implement rate limiting on login attempts
    - Require password complexity (length, character types)
    - Support password managers (no autocomplete=off)

Compliance:
    - OWASP: Recommends bcrypt/Argon2 with appropriate work factors
    - PCI DSS: Requires strong cryptography for password storage
    - GDPR: Hashing is a security measure, not anonymization
"""

import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

def hash_password_bcrypt(password: str) -> str:
    """
    Hash a password using bcrypt with automatic salt generation.
    
    Args:
        password: Plain-text password to hash (recommend min 8 chars)
    
    Returns:
        str: bcrypt hash string (60 characters, format: $2b$rounds$salthash)
             Example: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5uf"
    
    Security:
        - Work factor: 12 rounds (2^12 = 4096 iterations)
        - Salt: 128-bit random salt automatically generated
        - Output: Base64-encoded hash with embedded salt and parameters
        - Timing: ~300ms on modern hardware (intentionally slow)
    
    Format Breakdown:
        $2b$          - bcrypt identifier
        12$           - Cost factor (2^12 iterations)
        LQv...        - 22-char salt (128 bits base64-encoded)
        remaining     - 31-char hash (184 bits base64-encoded)
    
    Work Factor (Cost):
        - Default: 12 (recommended as of 2024)
        - Range: 4-31 (higher = more secure but slower)
        - Doubling: Each +1 doubles computation time
        - Future-proofing: Increase as hardware improves
    
    Usage Example:
        ```python
        # During user registration
        plain_password = "MySecureP@ssw0rd"
        password_hash = hash_password_bcrypt(plain_password)
        
        # Store password_hash in database (never store plain_password)
        user = User(email="user@example.com", password_hash=password_hash)
        db.add(user)
        db.commit()
        ```
    
    Performance:
        - Registration: ~300ms (acceptable delay)
        - Login: ~300ms (verify on each attempt)
        - Consider caching: Don't hash same password multiple times
    
    Common Mistakes:
        - Storing plain passwords: Always hash
        - Using MD5/SHA1: Not designed for passwords (too fast)
        - Custom salt: Let bcrypt generate (avoid homebrew crypto)
        - Low work factor: Use at least 12 for modern security
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def check_password_hash(hashed: str, password: str) -> bool:
    """Alias for verify_password_bcrypt with swapped parameter order for compatibility."""
    return verify_password_bcrypt(password, hashed)

def verify_password_bcrypt(password: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash (constant-time comparison).
    
    Args:
        password: Plain-text password from login attempt
        hashed: Stored bcrypt hash from database (60-char string)
    
    Returns:
        bool: True if password matches hash, False otherwise
    
    Security:
        - Constant-time: Execution time independent of match result
        - Timing-safe: Prevents timing attacks to guess passwords
        - Salt extraction: Automatically extracts salt from hash string
        - Work factor: Uses same cost as original hash
    
    How It Works:
        1. Extract salt and parameters from stored hash
        2. Hash provided password with extracted salt and cost
        3. Compare computed hash with stored hash (constant-time)
        4. Return True if identical, False otherwise
    
    Usage Example:
        ```python
        # During login authentication
        user = db.query(User).filter(User.email == login_email).first()
        
        if user and verify_password_bcrypt(login_password, user.password_hash):
            # Password correct - create session
            session = create_session(user.id)
            return {"token": session.token}
        else:
            # Password incorrect or user not found
            # Return same error for both (prevent user enumeration)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        ```
    
    Timing Attack Prevention:
        - Why it matters: Attacker measures response time to guess password
        - Attack: Fast response (wrong user) vs slow response (wrong password)
        - Defense: Always hash even if user doesn't exist
        
        ```python
        # Vulnerable code (timing attack possible)
        user = find_user(email)
        if user and verify_password(password, user.hash):  # Fast if no user
            login_success()
        
        # Secure code (constant time)
        user = find_user(email)
        dummy_hash = "$2b$12$..."  # Dummy hash for non-existent users
        hash_to_check = user.password_hash if user else dummy_hash
        is_valid = verify_password(password, hash_to_check)
        
        if user and is_valid:
            login_success()
        else:
            login_failed()  # Same error message
        ```
    
    Common Authentication Patterns:
        - Rate limiting: Max 5 failed attempts per 15 minutes
        - Account lockout: Temporary lock after 10 failed attempts
        - CAPTCHA: Show after 3 failed attempts
        - Audit logging: Log all login attempts (success and failure)
        - MFA: Require 2FA after password verification
    
    Performance:
        - Speed: ~300ms (same as hashing - intentional)
        - Comparison: Always compares full hash (no early exit)
        - Caching: Don't cache verification results (security risk)
    
    Error Handling:
        - Invalid hash format: Returns False (graceful degradation)
        - Empty password: Returns False
        - None values: Returns False
        - Unicode: UTF-8 encoding handles international characters
    
    Password Reset Flow:
        ```python
        # After user requests password change
        if verify_password_bcrypt(old_password, user.password_hash):
            # Old password correct - allow change
            new_hash = hash_password_bcrypt(new_password)
            user.password_hash = new_hash
            db.commit()
            invalidate_all_sessions(user.id)  # Force re-login
            send_password_changed_email(user.email)
        else:
            raise HTTPException(status_code=400, detail="Current password incorrect")
        ```
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))