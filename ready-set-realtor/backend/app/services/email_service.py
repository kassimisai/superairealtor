from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from ..core.config import settings

class EmailTemplate:
    def __init__(self, subject: str, body: str, is_html: bool = True):
        self.subject = subject
        self.body = body
        self.is_html = is_html

class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> dict:
        """
        Initialize email templates.
        """
        return {
            "lead_welcome": EmailTemplate(
                subject="Welcome to {company_name}",
                body="""
                <html>
                <body>
                    <h2>Welcome, {lead_name}!</h2>
                    <p>Thank you for your interest in {company_name}. We're excited to help you with your real estate needs.</p>
                    <p>Here's what you can expect from us:</p>
                    <ul>
                        <li>Personalized property recommendations</li>
                        <li>Market updates and insights</li>
                        <li>Expert guidance throughout your journey</li>
                    </ul>
                    <p>Your dedicated agent, {agent_name}, will be in touch with you shortly.</p>
                    <p>Best regards,<br>{company_name} Team</p>
                </body>
                </html>
                """
            ),
            "viewing_confirmation": EmailTemplate(
                subject="Viewing Confirmation: {property_address}",
                body="""
                <html>
                <body>
                    <h2>Your Viewing is Confirmed!</h2>
                    <p>Dear {lead_name},</p>
                    <p>Your viewing appointment has been scheduled for:</p>
                    <p><strong>Property:</strong> {property_address}<br>
                    <strong>Date:</strong> {viewing_date}<br>
                    <strong>Time:</strong> {viewing_time}</p>
                    <p>Your agent, {agent_name}, will meet you at the property.</p>
                    <p>If you need to reschedule, please contact us at {contact_number}.</p>
                    <p>Best regards,<br>{company_name} Team</p>
                </body>
                </html>
                """
            ),
            "market_update": EmailTemplate(
                subject="Real Estate Market Update: {area_name}",
                body="""
                <html>
                <body>
                    <h2>Market Update: {area_name}</h2>
                    <p>Dear {lead_name},</p>
                    <p>Here's your personalized market update for {area_name}:</p>
                    <ul>
                        <li>Average Price: {avg_price}</li>
                        <li>Price Trend: {price_trend}</li>
                        <li>Days on Market: {days_on_market}</li>
                    </ul>
                    <p>{market_insights}</p>
                    <p>Want to learn more? Contact {agent_name} at {agent_phone}.</p>
                    <p>Best regards,<br>{company_name} Team</p>
                </body>
                </html>
                """
            )
        }

    async def send_email(self, 
                        to_email: str, 
                        template_name: str, 
                        context: dict,
                        cc: Optional[List[str]] = None,
                        bcc: Optional[List[str]] = None) -> bool:
        """
        Send an email using a template.
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = template.subject.format(**context)
            msg['From'] = self.username
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = ", ".join(cc)
            if bcc:
                msg['Bcc'] = ", ".join(bcc)

            # Add body
            body = template.body.format(**context)
            if template.is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.sendmail(self.username, recipients, msg.as_string())

            return True

        except Exception as e:
            # In production, you'd want to log this error
            print(f"Error sending email: {str(e)}")
            return False

    async def send_custom_email(self,
                              to_email: str,
                              subject: str,
                              body: str,
                              is_html: bool = True,
                              cc: Optional[List[str]] = None,
                              bcc: Optional[List[str]] = None) -> bool:
        """
        Send a custom email without using a template.
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = ", ".join(cc)
            if bcc:
                msg['Bcc'] = ", ".join(bcc)

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.sendmail(self.username, recipients, msg.as_string())

            return True

        except Exception as e:
            print(f"Error sending custom email: {str(e)}")
            return False

    def add_template(self, name: str, subject: str, body: str, is_html: bool = True) -> None:
        """
        Add a new email template.
        """
        self.templates[name] = EmailTemplate(subject, body, is_html)

# Create a singleton instance
email_service = EmailService() 