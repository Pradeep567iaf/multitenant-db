import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from ..core.config import settings


class EmailService:
    """Service for sending emails."""
    
    @staticmethod
    def send_billing_email(tenant_email: str, tenant_name: str, billing_data: Dict) -> bool:
        """Send billing email to tenant."""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Monthly Billing Statement - {tenant_name}"
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = tenant_email
            
            # Create HTML content
            html_content = EmailService._create_billing_email_html(tenant_name, billing_data)
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email to {tenant_email}: {str(e)}")
            return False
    
    @staticmethod
    def _create_billing_email_html(tenant_name: str, billing_data: Dict) -> str:
        """Create HTML email content for billing statement."""
        breakdown_rows = ""
        for item in billing_data["breakdown"]:
            breakdown_rows += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['feature_code']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['usage_count']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${item['total_cost']:.2f}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background-color: #4CAF50; color: white; padding: 10px; }}
                .total {{ font-size: 18px; font-weight: bold; text-align: right; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Monthly Billing Statement</h1>
                </div>
                <div class="content">
                    <p>Dear {tenant_name},</p>
                    <p>Here is your billing statement for the period from 
                    <strong>{billing_data['billing_period_start'].strftime('%Y-%m-%d')}</strong> 
                    to <strong>{billing_data['billing_period_end'].strftime('%Y-%m-%d')}</strong>.</p>
                    
                    <h3>Billing Breakdown</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Feature</th>
                                <th>Usage Count</th>
                                <th>Total Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            {breakdown_rows}
                        </tbody>
                    </table>
                    
                    <div class="total">
                        Total Amount Due: ${billing_data['total_amount']:.2f}
                    </div>
                    
                    <p>Thank you for your business!</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply.</p>
                    <p>&copy; 2024 Multi-Tenant System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    @staticmethod
    def send_bulk_billing_emails(billing_list: List[Dict]) -> Dict:
        """Send billing emails to multiple tenants."""
        results = {
            "total": len(billing_list),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for billing_data in billing_list:
            success = EmailService.send_billing_email(
                tenant_email=billing_data["tenant_email"],
                tenant_name=billing_data["tenant_name"],
                billing_data=billing_data
            )
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "tenant_email": billing_data["tenant_email"],
                "success": success
            })
        
        return results
