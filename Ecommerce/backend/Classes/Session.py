# Represents a user's browsing session for tracking login state and associating carts with visitors.
# Sessions enable persistent shopping experiences across page loads without requiring login.
class Session:
    def __init__(self, id, session_token, cart_id, user_id, expires_at, created_at, last_activity_at):
        self.id = id  # Unique session identifier
        self.session_token = session_token  # Random token stored in browser cookie to identify returning visitors
        self.cart_id = cart_id  # Links to Cart associated with this session (preserves cart for guests)
        self.user_id = user_id  # Links to User if logged in (null for anonymous/guest sessions)
        self.expires_at = expires_at  # When session becomes invalid (typically 30 days, extended on activity)
        self.created_at = created_at  # When user first visited site
        self.last_activity_at = last_activity_at  # Last page load or action (for detecting abandoned sessions)
