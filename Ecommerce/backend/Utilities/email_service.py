"""
Email Service for sending transactional emails
Supports: Order confirmations, shipping updates, password resets
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Email configuration from environment variables
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', 'noreply@beladot.com')
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Beladot Marketplace')

executor = ThreadPoolExecutor(max_workers=3)


def send_email_sync(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None):
    """Send email synchronously using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email

        # Add text and HTML parts
        if text_body:
            part1 = MIMEText(text_body, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def send_email_async(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None):
    """Send email asynchronously"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        send_email_sync,
        to_email,
        subject,
        html_body,
        text_body
    )


def generate_order_confirmation_email(order_data: dict) -> tuple[str, str]:
    """Generate order confirmation email content"""
    order_id = order_data.get('id', 'N/A')
    customer_name = order_data.get('customer_name', 'Customer')
    total = order_data.get('total', 0)
    items = order_data.get('items', [])
    order_date = order_data.get('created_at', datetime.now().isoformat())

    subject = f"Order Confirmation - #{order_id[:8]}"
    
    # HTML version
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">
                {item.get('product_name', 'Product')}
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                {item.get('quantity', 1)}
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                ${item.get('price', 0):.2f}
            </td>
        </tr>
        """

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .order-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            .total {{ font-size: 18px; font-weight: bold; text-align: right; padding: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Order Confirmed!</h1>
            </div>
            <div class="content">
                <p>Hi {customer_name},</p>
                <p>Thank you for your order! We've received your order and are preparing it for shipment.</p>
                
                <div class="order-details">
                    <h2>Order #{order_id[:8]}</h2>
                    <p><strong>Order Date:</strong> {order_date[:10]}</p>
                    
                    <table>
                        <thead>
                            <tr style="background: #f0f0f0;">
                                <th style="padding: 10px; text-align: left;">Product</th>
                                <th style="padding: 10px; text-align: center;">Qty</th>
                                <th style="padding: 10px; text-align: right;">Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="total">
                        Total: ${total:.2f}
                    </div>
                </div>
                
                <p>You'll receive another email when your order ships.</p>
                <p>Thank you for shopping with Beladot!</p>
            </div>
            <div class="footer">
                <p>© 2025 Beladot Marketplace. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Text version
    items_text = "\n".join([
        f"  - {item.get('product_name')} x{item.get('quantity')} - ${item.get('price', 0):.2f}"
        for item in items
    ])

    text_body = f"""
Order Confirmation - #{order_id[:8]}

Hi {customer_name},

Thank you for your order! We've received your order and are preparing it for shipment.

Order Details:
{items_text}

Total: ${total:.2f}

You'll receive another email when your order ships.

Thank you for shopping with Beladot!

© 2025 Beladot Marketplace
    """

    return subject, html_body, text_body


def generate_shipping_update_email(shipment_data: dict) -> tuple[str, str]:
    """Generate shipping update email content"""
    order_id = shipment_data.get('order_id', 'N/A')
    tracking_number = shipment_data.get('tracking_number', 'N/A')
    carrier = shipment_data.get('carrier', 'Carrier')
    status = shipment_data.get('status', 'shipped')
    customer_name = shipment_data.get('customer_name', 'Customer')
    estimated_delivery = shipment_data.get('estimated_delivery', 'N/A')

    subject = f"Your order has shipped - #{order_id[:8]}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .tracking-box {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; text-align: center; }}
            .tracking-number {{ font-size: 24px; font-weight: bold; color: #007bff; padding: 10px; background: #e7f3ff; border-radius: 5px; display: inline-block; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📦 Your Order Has Shipped!</h1>
            </div>
            <div class="content">
                <p>Hi {customer_name},</p>
                <p>Great news! Your order #{order_id[:8]} has been shipped and is on its way to you.</p>
                
                <div class="tracking-box">
                    <p><strong>Tracking Number:</strong></p>
                    <div class="tracking-number">{tracking_number}</div>
                    <p style="margin-top: 20px;"><strong>Carrier:</strong> {carrier}</p>
                    <p><strong>Estimated Delivery:</strong> {estimated_delivery}</p>
                    <a href="#" class="button">Track Your Package</a>
                </div>
                
                <p>You can track your package using the tracking number above.</p>
                <p>Thank you for shopping with Beladot!</p>
            </div>
            <div class="footer">
                <p>© 2025 Beladot Marketplace. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
Your Order Has Shipped! - #{order_id[:8]}

Hi {customer_name},

Great news! Your order #{order_id[:8]} has been shipped and is on its way to you.

Tracking Number: {tracking_number}
Carrier: {carrier}
Estimated Delivery: {estimated_delivery}

You can track your package using the tracking number above.

Thank you for shopping with Beladot!

© 2025 Beladot Marketplace
    """

    return subject, html_body, text_body


def generate_password_reset_email(reset_data: dict) -> tuple[str, str]:
    """Generate password reset email content"""
    user_name = reset_data.get('user_name', 'User')
    reset_token = reset_data.get('reset_token', '')
    reset_url = reset_data.get('reset_url', f"http://localhost:3000/reset-password?token={reset_token}")

    subject = "Reset Your Password - Beladot"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .reset-box {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; text-align: center; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                <p>We received a request to reset your password for your Beladot account.</p>
                
                <div class="reset-box">
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                    <p style="margin-top: 20px; font-size: 12px; color: #666;">
                        This link will expire in 1 hour.
                    </p>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
                </div>
                
                <p>For security reasons, this link will expire in 1 hour.</p>
            </div>
            <div class="footer">
                <p>© 2025 Beladot Marketplace. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
Password Reset Request - Beladot

Hi {user_name},

We received a request to reset your password for your Beladot account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

⚠️ Security Notice: If you didn't request this password reset, please ignore this email. Your password will remain unchanged.

© 2025 Beladot Marketplace
    """

    return subject, html_body, text_body


# Convenience functions
async def send_order_confirmation(to_email: str, order_data: dict):
    """Send order confirmation email"""
    subject, html_body, text_body = generate_order_confirmation_email(order_data)
    return await send_email_async(to_email, subject, html_body, text_body)


async def send_shipping_update(to_email: str, shipment_data: dict):
    """Send shipping update email"""
    subject, html_body, text_body = generate_shipping_update_email(shipment_data)
    return await send_email_async(to_email, subject, html_body, text_body)


async def send_password_reset(to_email: str, reset_data: dict):
    """Send password reset email"""
    subject, html_body, text_body = generate_password_reset_email(reset_data)
    return await send_email_async(to_email, subject, html_body, text_body)
