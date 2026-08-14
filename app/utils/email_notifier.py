import logging
from app.config import settings

logger = logging.getLogger("email_notifier")

class EmailNotifier:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str):
        """Mock/Real SMTP email dispatcher"""
        logger.info(f"--- MOCK EMAIL DISPATCH ---")
        logger.info(f"From: {settings.EMAILS_FROM_EMAIL}")
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body}")
        logger.info(f"---------------------------")
        return True
