import asyncio
import boto3
import emails
from app.core.config import settings
from app.models.lead import Lead

import logging
import os
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from fastapi import BackgroundTasks

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

async def download_file(url: str) -> bytes:
    """Download file from URL (S3 or local)"""
    logger.info(f"Downloading file from URL: {url}")
    if url.startswith('http'):
        # Check if it's an S3 URL
        if '.s3.' in url and 'amazonaws.com' in url:
            try:
                # Extract the bucket and key from the URL
                # URL format: https://bucket-name.s3.region.amazonaws.com/key
                bucket_name = url.split('//')[1].split('.')[0]
                key = url.split('.amazonaws.com/')[1]
                
                logger.info(f"Detected S3 URL. Bucket: {bucket_name}, Key: {key}")
                
                # Create S3 client
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.storage.aws_access_key_id,
                    aws_secret_access_key=settings.storage.aws_secret_access_key,
                    region_name=settings.storage.aws_region
                )
                
                # Get the file from S3
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: s3_client.get_object(Bucket=bucket_name, Key=key)
                )
                
                file_bytes = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: response['Body'].read()
                )
                
                logger.info(f"Successfully downloaded file from S3")
                return file_bytes
                
            except Exception as e:
                logger.error(f"Failed to download from S3: {str(e)}")
                raise
        else:
            # For non-S3 URLs, use regular HTTP client
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"HTTP download failed: {error_text}")
                        raise Exception(f"Failed to download file: {response.status}")
                    return await response.read()
    else:
        # Read local file
        if os.path.exists(url):
            with open(url, 'rb') as f:
                return f.read()
        raise FileNotFoundError(f"File not found: {url}")

def _send_email_sync(msg):
    """Internal function to send email using SMTP synchronously"""
    try:
        with smtplib.SMTP(settings.email.smtp_host, settings.email.smtp_port) as server:
            server.starttls()  # Always use TLS for security
            if settings.email.smtp_user and settings.email.smtp_password:
                server.login(settings.email.smtp_user, settings.email.smtp_password)
            server.send_message(msg)
            logger.info(f"Email sent successfully to {msg['To']}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise

async def _send_email(msg):
    """Async wrapper for sending email"""
    try:
        await asyncio.get_event_loop().run_in_executor(None, _send_email_sync, msg)
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise

async def send_lead_notification(lead, background_tasks: BackgroundTasks = None):
    """Send email notification for new lead with resume attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.email.from_email
        msg['To'] = settings.email.attorney_email
        msg['Subject'] = f"New Lead Notification: {lead.first_name} {lead.last_name}"
        
        body = f"""
        New lead received:
        
        Name: {lead.first_name} {lead.last_name}
        Email: {lead.email}
        Status: {lead.status}
        
        Please find the attached resume for your review.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Download and attach resume
        try:
            logger.info(f"Downloading resume for lead: {lead.email} from {lead.resume_path}")
            resume_content = await download_file(lead.resume_path)
            resume_attachment = MIMEApplication(resume_content, _subtype="pdf")
            resume_attachment.add_header(
                'Content-Disposition', 
                'attachment', 
                filename=f"{lead.first_name}_{lead.last_name}_resume.pdf"
            )
            msg.attach(resume_attachment)
            logger.info(f"Resume attached successfully for lead: {lead.email}")
        except Exception as e:
            logger.error(f"Failed to attach resume for lead {lead.email}: {str(e)}")
            # Still send the email but add a note about the missing attachment
            msg.attach(MIMEText("\nNOTE: Resume could not be attached automatically. Please access it at: " + lead.resume_path, 'plain'))
        
        if background_tasks:
            background_tasks.add_task(_send_email, msg)
            logger.info(f"Email notification queued for lead: {lead.email}")
        else:
            await _send_email(msg)
        
    except Exception as e:
        logger.error(f"Failed to queue email notification for lead {lead.email}: {str(e)}")
        raise