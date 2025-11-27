from datetime import datetime, timezone, timedelta
import os

class Session:
    """
    Domain model representing a user session with activity tracking and expiration.
    
    This class manages web sessions, tracking authentication state, cart association,
    and user activity. It supports configurable session lifetime with automatic
    expiration and renewal on activity.
    
    Key Responsibilities:
        - Store session token for cookie-based auth
        - Track authentication state (guest vs authenticated)
        - Link sessions to carts (shopping cart persistence)
        - Record network information (IP, user agent) for security
        - Manage session expiration and renewal
        - Track last activity for idle timeout
    
    Session Types:
        - Guest session: is_authenticated=False, user_id=None
        - Authenticated session: is_authenticated=True, user_id set
    
    Security Features:
        - Session tokens should be cryptographically random
        - IP address and user agent tracked for anomaly detection
        - Configurable expiration via SESSION_LIFETIME_HOURS env var
        - Activity-based renewal (sliding expiration)
    
    Design Notes:
        - Each session linked to one cart (cart follows user)
        - Guest sessions can be upgraded to authenticated on login
        - This is a domain object; persistence handled by SessionRepository
    """
    def __init__(self, id, session_token, cart_id, user_id, ip_address, user_agent, is_authenticated, expires_at, created_at, last_activity_at):
        """
        Initialize a Session domain object.
        
        Args:
            id: Unique identifier (None for new sessions before persistence)
            session_token: Cryptographically random session identifier (for cookies)
            cart_id: Foreign key to associated shopping cart
            user_id: Foreign key to user (None for guest sessions)
            ip_address: Client IP address
            user_agent: Client browser/app user agent string
            is_authenticated: Whether session is authenticated (vs guest)
            expires_at: Session expiration timestamp
            created_at: Session creation timestamp
            last_activity_at: Last request timestamp using this session
        """
        self.id = id
        self.session_token = session_token
        self.cart_id = cart_id
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.is_authenticated = is_authenticated
        self.expires_at = expires_at
        self.created_at = created_at
        self.last_activity_at = last_activity_at
    
    def touch(self, repository=None) -> None:
        """
        Update session activity timestamp and extend expiration (sliding window).
        
        Args:
            repository: Repository for persisting changes (optional)
            
        Side Effects:
            - Sets last_activity_at to current time
            - Extends expires_at by SESSION_LIFETIME_HOURS from now
            - Persists session via repository
            
        Design Notes:
            - Implements sliding expiration (activity extends session)
            - Should be called on each authenticated request
            - Session lifetime configurable via environment variable (default 24 hours)
        """
        now = datetime.now(timezone.utc)
        self.last_activity_at = now
        
        session_lifetime_hours = int(os.getenv('SESSION_LIFETIME_HOURS', '24'))
        self.expires_at = now + timedelta(hours=session_lifetime_hours)
        
        if repository:
            repository.update(self)