# Represents a record of important system actions for security, compliance, and debugging.
# Tracks who did what, when, and from where - essential for security audits and troubleshooting.
class AuditLog:
    def __init__(self, id, actor_id, actor_type, actor_email, action, target_type, target_id, metadata, ip_address, user_agent, created_at):
        self.id = id  # Unique audit log entry identifier
        self.actor_id = actor_id  # ID of who performed the action (user, admin, API key)
        self.actor_type = actor_type  # Type of actor: "user", "admin", "system", "api_key"
        self.actor_email = actor_email  # Email of the actor for easy identification in logs
        self.action = action  # What was done (e.g., "user.login", "order.created", "product.updated", "payment.refunded")
        self.target_type = target_type  # Type of resource affected (e.g., "Product", "Order", "User")
        self.target_id = target_id  # ID of the specific resource affected
        self.metadata = metadata  # JSON with additional context (e.g., what fields changed, old vs new values)
        self.ip_address = ip_address  # IP address the action originated from (for security tracking)
        self.user_agent = user_agent  # Browser/app that made the request (helps identify suspicious activity)
        self.created_at = created_at  # When the action occurred
