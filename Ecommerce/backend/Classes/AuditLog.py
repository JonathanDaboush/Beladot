from typing import Any

class AuditLog:
    """
    Domain model representing an immutable audit trail entry for compliance and security.
    
    This class captures who did what, when, and to which resource, providing a comprehensive
    audit trail for compliance, security investigations, and debugging. Records are immutable
    once created and include contextual information like IP address and user agent.
    
    Key Responsibilities:
        - Record actor information (who performed the action)
        - Capture action and target details (what was done to what)
        - Store contextual metadata (why, how, additional details)
        - Track network information (IP, user agent) for security
        - Provide sanitized output for non-privileged access
    
    Security Considerations:
        - Audit logs are immutable (no updates or deletes)
        - Sensitive data (passwords, tokens) should never be logged
        - PII requires access control (use include_sensitive flag)
        - IP addresses and user agents are compliance-relevant
    
    Compliance Features:
        - Immutable audit trail (GDPR, SOX, HIPAA requirements)
        - Actor attribution (who performed each action)
        - Timestamp for chronological reconstruction
        - Metadata for detailed forensics
    
    Design Notes:
        - This is a write-only model (created but never updated)
        - Sanitization performed at read time (not storage)
        - Repository should prevent updates/deletes
    """
    def __init__(self, id, actor_id, actor_type, actor_email, action, target_type, target_id, item_metadata, ip_address, user_agent, created_at):
        """
        Initialize an AuditLog domain object.
        
        Args:
            id: Unique identifier (None for new logs before persistence)
            actor_id: ID of the user/system who performed the action
            actor_type: Type of actor ('user', 'system', 'api_key')
            actor_email: Email address of the actor (for user type)
            action: Action performed (e.g., 'user.login', 'order.created', 'api_key.revoked')
            target_type: Type of target resource (e.g., 'user', 'order', 'product')
            target_id: ID of the target resource
            item_metadata: Additional context as dictionary (e.g., {'reason': 'fraud'})
            ip_address: IP address of the actor
            user_agent: Browser/client user agent string
            created_at: Timestamp when action occurred
        """
        self.id = id
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.actor_email = actor_email
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.item_metadata = item_metadata
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = created_at
    
    def to_dict(self, include_sensitive: bool = False) -> dict[str, Any]:
        """
        Convert audit log to dictionary with optional sensitive data.
        
        Args:
            include_sensitive: If True, include PII and network data (default False)
            
        Returns:
            dict: Audit log data with selective field inclusion:
                  - Always: id, actor_id, actor_type, action, target_type, 
                           target_id, created_at
                  - Sensitive only: actor_email, ip_address, user_agent, 
                                   full metadata
                  - Public: sanitized metadata (excludes password, token, key, secret)
                  
        Design Notes:
            - Default behavior protects PII (GDPR compliance)
            - Metadata sanitization at key level (prevents secret leakage)
            - Sensitive data requires explicit opt-in (include_sensitive=True)
            - Useful for APIs with different permission levels
        """
        result = {
            "id": self.id,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            result["actor_email"] = self.actor_email
            result["ip_address"] = self.ip_address
            result["user_agent"] = self.user_agent
            result["metadata"] = self.item_metadata
        else:
            if self.item_metadata:
                sanitized = {k: v for k, v in self.item_metadata.items() if k not in ['password', 'token', 'key', 'secret']}
                result["metadata"] = sanitized
        
        return result