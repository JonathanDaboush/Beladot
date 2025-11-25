from datetime import datetime, timezone, timedelta
import os

class Session:
    def __init__(self, id, session_token, cart_id, user_id, ip_address, user_agent, is_authenticated, expires_at, created_at, last_activity_at):
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
        now = datetime.now(timezone.utc)
        self.last_activity_at = now
        
        session_lifetime_hours = int(os.getenv('SESSION_LIFETIME_HOURS', '24'))
        self.expires_at = now + timedelta(hours=session_lifetime_hours)
        
        if repository:
            repository.update(self)