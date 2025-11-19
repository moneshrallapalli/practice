"""
Email notification service using Brevo (Sendinblue) API
Simplest and most reliable option
"""
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from typing import Dict, Any
from datetime import datetime
from loguru import logger
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings


class EmailService:
    """Service for sending email notifications using Brevo"""
    
    def __init__(self):
        """Initialize Brevo email service"""
        self.brevo_api_key = settings.BREVO_API_KEY if hasattr(settings, 'BREVO_API_KEY') else None
        self.recipient_email = settings.EMAIL_RECIPIENT
        self.sender_email = "noreply@sentintinel.app"
        self.sender_name = "SentinTinel AI"
        
        # Check if email is configured
        self.enabled = bool(self.brevo_api_key)
        
        if not self.enabled:
            logger.warning("⚠️ Email notifications disabled - BREVO_API_KEY not configured in .env")
        else:
            # Configure Brevo API
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.brevo_api_key
            self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            logger.info(f"📧 Brevo email service initialized - will send to {self.recipient_email}")
    
    async def send_critical_alert(
        self,
        alert_data: Dict[str, Any]
    ) -> bool:
        """
        Send critical alert email using the exact same data structure as the frontend
        
        Args:
            alert_data: The complete alert data dict sent to frontend
            
        Returns:
            bool: True if email sent successfully
        """
        if not self.enabled:
            logger.debug("Email service not enabled, skipping critical alert email")
            return False
        
        try:
            # Extract data from alert (same structure as frontend receives)
            title = alert_data.get('title', 'Critical Alert')
            message = alert_data.get('message', '')
            camera_id = alert_data.get('camera_id', 0)
            timestamp = alert_data.get('timestamp', datetime.now().isoformat())
            severity = alert_data.get('severity', 'CRITICAL')
            
            # Parse timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                time_str = datetime.now().strftime('%B %d, %Y at %I:%M %p')
            
            # Build HTML body - clean and simple, matching the alert tab display
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                    .header {{ background: {'#dc3545' if severity == 'CRITICAL' else '#ffc107' if severity == 'WARNING' else '#17a2b8'}; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                    .header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
                    .content {{ padding: 24px; }}
                    .message {{ font-size: 15px; line-height: 1.7; color: #333; white-space: pre-wrap; margin: 0; }}
                    .meta {{ margin-top: 24px; padding-top: 16px; border-top: 1px solid #e0e0e0; color: #666; font-size: 13px; }}
                    .meta-item {{ margin: 4px 0; }}
                    .footer {{ padding: 16px 24px; background: #f8f9fa; border-radius: 0 0 8px 8px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{title}</h1>
                    </div>
                    <div class="content">
                        <div class="message">{message}</div>
                        <div class="meta">
                            <div class="meta-item">📹 <strong>Camera:</strong> {camera_id}</div>
                            <div class="meta-item">🕐 <strong>Time:</strong> {time_str}</div>
                            <div class="meta-item">⚠️ <strong>Severity:</strong> {severity}</div>
                        </div>
                    </div>
                    <div class="footer">
                        SentinTinel AI Surveillance System
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create email
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": self.recipient_email}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject=f"🚨 {severity}: {title}",
                html_content=html_body
            )
            
            # Send via Brevo
            self.api_instance.send_transac_email(send_smtp_email)
            
            logger.info(f"✅ Critical alert email sent to {self.recipient_email}: {title}")
            return True
            
        except ApiException as e:
            logger.error(f"❌ Failed to send critical alert email: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send critical alert email: {e}")
            return False
    
    async def send_summary_email(
        self,
        alert_data: Dict[str, Any]
    ) -> bool:
        """
        Send 2-minute summary email using the exact same data structure as the frontend
        
        Args:
            alert_data: The complete alert data dict sent to frontend
            
        Returns:
            bool: True if email sent successfully
        """
        if not self.enabled:
            logger.debug("Email service not enabled, skipping summary email")
            return False
        
        try:
            # Extract data from alert (same structure as frontend receives)
            title = alert_data.get('title', 'Activity Summary')
            message = alert_data.get('message', '')
            timestamp = alert_data.get('timestamp', datetime.now().isoformat())
            
            # Parse timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                time_str = datetime.now().strftime('%B %d, %Y at %I:%M %p')
            
            # Build HTML body - clean and simple, matching the alert tab display
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                    .header {{ background: #007bff; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                    .header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
                    .content {{ padding: 24px; }}
                    .message {{ font-size: 15px; line-height: 1.7; color: #333; white-space: pre-wrap; margin: 0; }}
                    .meta {{ margin-top: 24px; padding-top: 16px; border-top: 1px solid #e0e0e0; color: #666; font-size: 13px; }}
                    .meta-item {{ margin: 4px 0; }}
                    .footer {{ padding: 16px 24px; background: #f8f9fa; border-radius: 0 0 8px 8px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{title}</h1>
                    </div>
                    <div class="content">
                        <div class="message">{message}</div>
                        <div class="meta">
                            <div class="meta-item">🕐 <strong>Generated:</strong> {time_str}</div>
                            <div class="meta-item">📊 <strong>Type:</strong> 2-Minute Activity Summary</div>
                        </div>
                    </div>
                    <div class="footer">
                        SentinTinel AI Surveillance System
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create email
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": self.recipient_email}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject=f"📊 {title}",
                html_content=html_body
            )
            
            # Send via Brevo
            self.api_instance.send_transac_email(send_smtp_email)
            
            logger.info(f"✅ Summary email sent to {self.recipient_email}: {title}")
            return True
            
        except ApiException as e:
            logger.error(f"❌ Failed to send summary email: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send summary email: {e}")
            return False


# Global email service instance
email_service = EmailService()

