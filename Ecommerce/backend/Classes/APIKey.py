# Represents an API key for programmatic access to the e-commerce platform.
# Used by third-party integrations, mobile apps, or automated systems to interact with the API securely.
class APIKey:
    def __init__(self, id, user_id, key_hash, name, scopes, is_active, is_revoked, created_at, expires_at, last_used_at):
        self.id = id  # Unique API key record identifier
        self.user_id = user_id  # Links to User who owns this API key
        self.key_hash = key_hash  # Hashed version of the API key for secure storage (never store plain text keys)
        self.name = name  # Friendly name for the key (e.g., "Mobile App", "Shopify Integration")
        self.scopes = scopes  # Permissions array defining what the key can access (e.g., ["read:products", "write:orders"])
        self.is_active = is_active  # Whether the key is currently enabled for use
        self.is_revoked = is_revoked  # Whether the key has been permanently revoked (cannot be reactivated)
        self.created_at = created_at  # When the API key was generated
        self.expires_at = expires_at  # When the key will automatically become invalid (null = no expiration)
        self.last_used_at = last_used_at  # Last time this key was used to make an API call (for monitoring inactive keys)
