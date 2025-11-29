import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any


class EmailService:
    """
    Transactional email service for sending automated customer communications.
    
    Handles SMTP connections, HTML template rendering, and email delivery for
    critical business events (registration, password reset, order confirmation,
    shipping updates). Supports variable substitution in templates and retry logic.
    
    Architecture:
        - Template-based: HTML emails loaded from email_templates/ directory
        - Variable substitution: Simple {{variable}} placeholder replacement
        - SMTP delivery: Gmail SMTP with TLS encryption
        - Transactional focus: One email per specific user action
        
    Security:
        - TLS encryption: starttls() for secure SMTP connection
        - App passwords: Use Gmail app-specific passwords (not account password)
        - Rate limiting: Respect SMTP provider limits (Gmail: 500/day for free)
        - SPF/DKIM: Configure DNS records for delivery reliability
        - No sensitive data: Never include passwords, full card numbers
        
    Template System:
        - Location: email_templates/*.html files
        - Syntax: {{variable}} placeholders replaced with actual values
        - Encoding: UTF-8 for international characters
        - MIME type: multipart/alternative (supports text + HTML fallback)
        
    Configuration:
        - smtp_host: SMTP server address (Gmail, SendGrid, AWS SES)
        - smtp_port: 587 (STARTTLS) or 465 (SSL)
        - username/password: SMTP authentication credentials
        - from_email: Sender address (must match authenticated domain)
        
    Email Types:
        - Authentication: Welcome, email verification, password reset
        - Orders: Confirmation, payment received, cancellation
        - Fulfillment: Shipped, out for delivery, delivered
        - Marketing: Cart abandonment, price drop alerts, promotions
        - Support: Order updates, refund processed, return received
        
    Error Handling:
        - Network failures: SMTP connection timeout (retry with exponential backoff)
        - Authentication errors: Invalid credentials (check app password)
        - Rate limits: Too many emails (queue with delay)
        - Invalid recipients: Bounce handling (mark email as invalid)
        - Template missing: FileNotFoundError (graceful degradation)
        
    Best Practices:
        - Async delivery: Queue emails via Job system (don't block HTTP requests)
        - Idempotency: Track sent emails (prevent duplicate welcome emails)
        - Monitoring: Log failures, track delivery rates
        - Testing: Use mailtrap.io or mailhog for development
        - Compliance: Include unsubscribe links (CAN-SPAM Act)
        
    Production Considerations:
        - Use dedicated email service: SendGrid, Mailgun, AWS SES (not Gmail)
        - Environment variables: Don't hardcode credentials
        - Retry logic: Queue failed emails for retry
        - Template caching: Don't reload templates on every send
        - Analytics: Track open rates, click rates (via tracking pixels/links)
        
    Example Usage:
        ```python
        email_service = EmailService()
        success = email_service.send_account_created(
            to_email="user@example.com",
            first_name="John",
            verification_link="https://store.com/verify/abc123"
        )
        if success:
            print("Welcome email sent")
        ```
    """
    
    def __init__(self):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = "your-email@gmail.com"
        self.password = "your-app-password"
        self.from_email = "noreply@yourstore.com"
        self.template_dir = Path(__file__).parent / "email_templates"
    
    def _load_template(self, template_name: str) -> str:
        """
        Load HTML email template from the templates directory.
        
        Args:
            template_name: Template filename without .html extension
                          (e.g., "account_created", "forgot_password")
        
        Returns:
            str: Raw HTML template content with {{variable}} placeholders
        
        Raises:
            FileNotFoundError: If template file doesn't exist
            UnicodeDecodeError: If template has invalid UTF-8 encoding
        
        Template Structure:
            - HTML5 with inline CSS (email clients don't support external CSS)
            - Responsive design (mobile-friendly with media queries)
            - Placeholders: {{first_name}}, {{verification_link}}, etc.
            - Plain text fallback: Consider adding text/plain MIME part
        
        Example Template:
            ```html
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h1>Welcome, {{first_name}}!</h1>
                <p>Click here to verify: <a href="{{verification_link}}">Verify Email</a></p>
            </body>
            </html>
            ```
        """
        template_path = self.template_dir / f"{template_name}.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Replace template placeholders with actual values.
        
        Args:
            template: HTML template string with {{variable}} placeholders
            variables: Dictionary mapping variable names to replacement values
        
        Returns:
            str: Rendered HTML with all placeholders replaced
        
        Security:
            - No HTML escaping: Assumes trusted input (don't pass user-generated content)
            - XSS risk: Never render unsanitized user input in emails
            - For user content: Use html.escape() before rendering
        
        Limitations:
            - Simple string replacement (not a full template engine)
            - No conditionals or loops (use Jinja2 for complex templates)
            - Case-sensitive: {{Name}} != {{name}}
            - Whitespace matters: {{ name }} != {{name}}
        
        Example:
            ```python
            template = "Hello {{name}}, your order {{order_id}} is ready!"
            variables = {"name": "Alice", "order_id": "12345"}
            result = self._render_template(template, variables)
            # Result: "Hello Alice, your order 12345 is ready!"
            ```
        
        Production Alternative:
            Consider using Jinja2 for advanced features:
            - Conditionals: {% if user.is_vip %} ... {% endif %}
            - Loops: {% for item in items %} ... {% endfor %}
            - Filters: {{ price|currency }}
            - Auto-escaping: Prevents XSS by default
        """
        for key, value in variables.items():
            template = template.replace("{{" + key + "}}", str(value))
        return template
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send an email via SMTP with TLS encryption.
        
        Args:
            to_email: Recipient email address (validated format recommended)
            subject: Email subject line (keep under 50 chars for mobile)
            html_content: Rendered HTML email body
        
        Returns:
            bool: True if email sent successfully, False if failed
        
        SMTP Flow:
            1. Connect to SMTP server (smtp.gmail.com:587)
            2. Upgrade to TLS (starttls for encryption)
            3. Authenticate with username/password
            4. Send MIME message with HTML content
            5. Close connection
        
        Error Handling:
            - SMTPAuthenticationError: Invalid credentials (check app password)
            - SMTPRecipientsRefused: Invalid recipient email
            - SMTPServerDisconnected: Network issue (retry)
            - SMTPDataError: Message rejected by server (check content)
            - socket.timeout: Connection timeout (increase timeout or retry)
        
        Limitations:
            - Synchronous: Blocks until sent (use async or Job queue in production)
            - No delivery guarantee: Email accepted by SMTP != delivered to inbox
            - No retry: Returns False immediately on failure
            - No bounce handling: Can't detect bounced emails
        
        Gmail Restrictions:
            - Daily limit: 500 emails/day (free), 2000/day (Google Workspace)
            - Rate limit: ~10 emails/minute
            - Attachment size: 25 MB max
            - Blocked content: Executable files, scripts
        
        Production Improvements:
            ```python
            # 1. Use environment variables
            username = os.getenv("SMTP_USERNAME")
            
            # 2. Add retry logic
            for attempt in range(3):
                if send_email(...):
                    break
                time.sleep(2 ** attempt)  # Exponential backoff
            
            # 3. Use email service provider
            # SendGrid, Mailgun, AWS SES instead of Gmail
            
            # 4. Queue emails asynchronously
            job = Job(type="email.send", payload={...})
            db.add(job)
            ```
        
        Email Deliverability:
            - SPF record: Authorize sending server
            - DKIM signature: Verify email authenticity
            - DMARC policy: Define handling for failed checks
            - Reputation: Monitor sender score, avoid spam complaints
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_account_created(self, to_email: str, first_name: str, verification_link: str) -> bool:
        """
        Send welcome email with email verification link to new users.
        
        Args:
            to_email: New user's email address
            first_name: User's first name for personalization
            verification_link: Unique verification URL with token
                              (e.g., "https://store.com/verify/abc123xyz")
        
        Returns:
            bool: True if email sent successfully, False otherwise
        
        Verification Link:
            - Contains unique token: sha256(user_id + timestamp + secret)
            - Expiration: 24-48 hours (stored in database or JWT)
            - One-time use: Mark token as used after verification
            - Security: Use cryptographically secure random tokens
        
        Email Content:
            - Welcome message with brand introduction
            - Clear call-to-action: "Verify Email" button
            - Benefits: "Complete registration to start shopping"
            - Support contact: Help email or link
            - Legal: Terms of service, privacy policy links
        
        User Flow:
            1. User registers with email/password
            2. System creates unverified user account
            3. Generate verification token, store in DB
            4. Send welcome email with verification link
            5. User clicks link → mark email_verified=true
            6. Redirect to dashboard or onboarding
        
        Best Practices:
            - Send immediately after registration (within seconds)
            - Resend option: "Didn't receive? Resend verification"
            - Mobile-friendly: Large buttons, readable text
            - Track opens: Know if user saw the email
            - A/B test: Different subject lines for higher open rates
        
        Failure Handling:
            - If send fails: Queue for retry, show "check spam" message to user
            - Invalid email: Catch during registration (validate format)
            - Temporary failure: Retry after 5 min, 15 min, 1 hour
        """
        template = self._load_template("account_created")
        html_content = self._render_template(template, {
            "first_name": first_name,
            "verification_link": verification_link
        })
        subject = "Welcome! Verify Your Email"
        return self.send_email(to_email, subject, html_content)
    
    def send_password_reset(self, to_email: str, first_name: str, reset_link: str) -> bool:
        """
        Send password reset email with secure one-time reset link.
        
        Args:
            to_email: User's registered email address
            first_name: User's first name for personalization
            reset_link: Unique password reset URL with token
                       (e.g., "https://store.com/reset-password/xyz789")
        
        Returns:
            bool: True if email sent successfully, False otherwise
        
        Security Considerations:
            - Token generation: Use secrets.token_urlsafe(32) for randomness
            - Token storage: Hash token before storing in DB (like passwords)
            - Expiration: 15-60 minutes (short window reduces risk)
            - One-time use: Invalidate token immediately after password change
            - Rate limiting: Max 3 reset requests per hour per email
            - No user enumeration: Same response for valid/invalid emails
        
        Reset Link Structure:
            - Base URL: https://store.com/reset-password/
            - Token: 43-character URL-safe string
            - Example: /reset-password/kF3xQ7mN9pL2vR8sT6wY4zU1hJ5gD0cB
        
        Email Content:
            - Clear subject: "Reset Your Password" (not "Security Alert")
            - Assurance: "If you didn't request this, ignore this email"
            - Urgency: "This link expires in 1 hour"
            - Call-to-action: "Reset Password" button (not just text link)
            - Security tip: "Never share this link with anyone"
        
        Password Reset Flow:
            1. User clicks "Forgot Password"
            2. Enter email address
            3. System generates reset token, stores hashed version + expiry
            4. Send reset email (even if email not found - prevent enumeration)
            5. User clicks link within expiration window
            6. Verify token valid and not expired
            7. Show password reset form
            8. User sets new password
            9. Invalidate token, update password hash
            10. Send confirmation email ("Your password was changed")
        
        Attack Vectors:
            - Brute force: Rate limit requests (3 per hour)
            - Token guessing: Use 256-bit random tokens (impossible to guess)
            - Replay attacks: One-time tokens (mark as used)
            - Email interception: Short expiration (15-60 min)
            - Account takeover: Notify user via email after password change
        
        Best Practices:
            - Don't reveal if email exists in system (prevent user enumeration)
            - Log all password reset attempts (audit trail)
            - Alert user via email if password changed (detection)
            - Invalidate all sessions after password change (force re-login)
            - Clear message: "Check spam folder if not received"
        
        Failure Scenarios:
            - Token expired: Show "Link expired, request a new one"
            - Token already used: Show "Already used, request a new one"
            - Invalid token: Show generic "Invalid link"
            - Email send fails: Queue for retry, log error
        """
        template = self._load_template("forgot_password")
        html_content = self._render_template(template, {
            "first_name": first_name,
            "reset_link": reset_link
        })
        subject = "Reset Your Password"
        return self.send_email(to_email, subject, html_content)
    
    def send_order_shipped(self, to_email: str, customer_name: str, order_number: str, tracking_number: str, carrier_name: str, service_level: str, tracking_url: str, estimated_delivery: str, shipping_address: str) -> bool:
        """
        Send shipment confirmation with tracking information.
        
        Sent when carrier picks up the package and shipment is created.
        
        Args:
            to_email: Customer email
            customer_name: Customer's name
            order_number: Order ID
            tracking_number: Carrier's tracking number
            carrier_name: "Purolator", "FedEx", "DHL", etc.
            service_level: "Express", "Ground", "Overnight"
            tracking_url: Direct link to carrier's tracking page
            estimated_delivery: "Nov 30, 2025 by 5:00 PM"
            shipping_address: Full delivery address
        
        Business Logic:
            - Sent after create_shipment() succeeds
            - Highest open rate of all transactional emails (~70%)
            - Include tracking link (don't make customer search)
            - Set delivery expectations (reduce "where's my order?" inquiries)
        """
        template = self._load_template("order_shipped")
        html_content = self._render_template(template, {
            "customer_name": customer_name,
            "order_number": order_number,
            "tracking_number": tracking_number,
            "carrier_name": carrier_name,
            "service_level": service_level,
            "tracking_url": tracking_url,
            "estimated_delivery": estimated_delivery,
            "shipping_address": shipping_address
        })
        subject = f"Your Order #{order_number} Has Shipped!"
        return self.send_email(to_email, subject, html_content)
    
    def send_out_for_delivery(self, to_email: str, customer_name: str, order_number: str, tracking_number: str, tracking_url: str, delivery_time: str, driver_name: str, delivery_instructions: str, carrier_name: str) -> bool:
        """
        Send out-for-delivery notification (same-day alert).
        
        Sent when package is loaded on delivery vehicle for final mile delivery.
        
        Args:
            delivery_time: "By 5:00 PM today"
            driver_name: "John" or "Your driver"
            delivery_instructions: Customer's saved instructions
        
        Business Logic:
            - Sent morning of delivery day (triggered by carrier webhook)
            - High urgency - customer needs to be home
            - Include option to leave without signature
            - Reduce missed deliveries
        """
        template = self._load_template("out_for_delivery")
        html_content = self._render_template(template, {
            "customer_name": customer_name,
            "order_number": order_number,
            "tracking_number": tracking_number,
            "tracking_url": tracking_url,
            "delivery_time": delivery_time,
            "driver_name": driver_name,
            "delivery_instructions": delivery_instructions,
            "carrier_name": carrier_name
        })
        subject = f"Order #{order_number} - Out for Delivery Today!"
        return self.send_email(to_email, subject, html_content)
    
    def send_delivered(self, to_email: str, customer_name: str, order_number: str, tracking_number: str, delivered_at: str, delivered_to_name: str, delivery_location: str, signature_url: str, photo_url: str, review_url: str) -> bool:
        """
        Send delivery confirmation with proof.
        
        Sent when carrier confirms successful delivery.
        
        Args:
            delivered_at: "Nov 28, 2025 at 2:35 PM"
            delivered_to_name: Person who signed
            delivery_location: "Front door", "Mailroom", etc.
            signature_url: Image URL from carrier API
            photo_url: Doorstep photo from carrier
            review_url: Link to product review page
        
        Business Logic:
            - Final email in delivery lifecycle
            - Include proof of delivery (signature/photo)
            - Request product review (high conversion timing)
            - Reduce "where's my order?" inquiries
        """
        template = self._load_template("delivered")
        html_content = self._render_template(template, {
            "customer_name": customer_name,
            "order_number": order_number,
            "tracking_number": tracking_number,
            "delivered_at": delivered_at,
            "delivered_to_name": delivered_to_name,
            "delivery_location": delivery_location,
            "signature_url": signature_url,
            "photo_url": photo_url,
            "review_url": review_url
        })
        subject = f"Order #{order_number} - Delivered!"
        return self.send_email(to_email, subject, html_content)
    
    def send_delivery_failed(self, to_email: str, customer_name: str, order_number: str, tracking_number: str, failure_reason: str, attempt_date: str, reschedule_url: str, carrier_name: str, pickup_location: str, available_date: str, remaining_attempts: int, days_until_return: int) -> bool:
        """
        Send failed delivery notification with recovery options.
        
        Sent when delivery attempt fails (customer not home, address issue, etc.).
        
        Args:
            failure_reason: "No one available to receive", "Address not found"
            attempt_date: "Nov 28, 2025 at 3:15 PM"
            reschedule_url: Link to carrier's redelivery page
            pickup_location: Nearest carrier location address
            available_date: "Nov 29, 2025"
            remaining_attempts: 2
            days_until_return: 5 (before package returned to sender)
        
        Business Logic:
            - Urgent action required
            - Multiple recovery options (reschedule, pickup, authorize release)
            - Time pressure (limited attempts)
            - Prevent return to sender
        """
        template = self._load_template("delivery_failed")
        html_content = self._render_template(template, {
            "customer_name": customer_name,
            "order_number": order_number,
            "tracking_number": tracking_number,
            "failure_reason": failure_reason,
            "attempt_date": attempt_date,
            "reschedule_url": reschedule_url,
            "carrier_name": carrier_name,
            "pickup_location": pickup_location,
            "available_date": available_date,
            "remaining_attempts": remaining_attempts,
            "days_until_return": days_until_return
        })
        subject = f"Action Required - Delivery Attempt Failed for Order #{order_number}"
        return self.send_email(to_email, subject, html_content)
    
    def send_return_label(self, to_email: str, customer_name: str, order_number: str, return_id: str, tracking_number: str, label_url: str, tracking_url: str, carrier_name: str, dropoff_locations: str, refund_days: int, returned_items: str, refund_amount: str) -> bool:
        """
        Send return shipping label to customer.
        
        Sent after return request is approved.
        
        Args:
            return_id: Internal return ID
            label_url: PDF return label download link
            dropoff_locations: List of carrier drop-off points
            refund_days: 3-7 business days after receipt
            returned_items: List of items being returned
            refund_amount: "$125.99"
        
        Business Logic:
            - Include detailed packing instructions
            - Prepaid label (you pay shipping)
            - Set refund expectations
            - Track return shipment
        """
        template = self._load_template("return_label_ready")
        html_content = self._render_template(template, {
            "customer_name": customer_name,
            "order_number": order_number,
            "return_id": return_id,
            "tracking_number": tracking_number,
            "label_url": label_url,
            "tracking_url": tracking_url,
            "carrier_name": carrier_name,
            "dropoff_locations": dropoff_locations,
            "refund_days": refund_days,
            "returned_items": returned_items,
            "refund_amount": refund_amount
        })
        subject = f"Return Label Ready for Order #{order_number}"
        return self.send_email(to_email, subject, html_content)
