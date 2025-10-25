import emails
from app.core.config import settings
from app.models.lead import Lead

async def send_lead_notification(lead: Lead) -> None:
    """
    Send email notifications to both the prospect and the attorney.
    """
    # Configure email message
    message = emails.Message(
        html=None,
        text=None,
        subject=None,
        mail_from=settings.email.from_email,
    )

    # Send prospect confirmation
    message.html = f"""
    <h2>Thank you for your interest!</h2>
    <p>Dear {lead.first_name} {lead.last_name},</p>
    <p>We have received your information and will contact you shortly.</p>
    <p>Best regards,<br>Your Legal Team</p>
    """
    message.subject = "We've Received Your Information"
    message.mail_to = lead.email

    message.send(
        smtp={
            "host": settings.email.smtp_host,
            "port": settings.email.smtp_port,
            "user": settings.email.smtp_user,
            "password": settings.email.smtp_password,
            "tls": True,
        }
    )

    # Send attorney notification
    message.html = f"""
    <h2>New Lead Submitted</h2>
    <p>A new lead has been submitted with the following details:</p>
    <ul>
        <li>Name: {lead.first_name} {lead.last_name}</li>
        <li>Email: {lead.email}</li>
        <li>Resume: {lead.resume_path}</li>
    </ul>
    <p>Please review and reach out to the prospect.</p>
    """
    message.subject = f"New Lead: {lead.first_name} {lead.last_name}"
    message.mail_to = settings.email.attorney_email

    message.send(
        smtp={
            "host": settings.email.smtp_host,
            "port": settings.email.smtp_port,
            "user": settings.email.smtp_user,
            "password": settings.email.smtp_password,
            "tls": True,
        }
    )