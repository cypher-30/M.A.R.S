"""Deliver an alert. Email first; add SMS or push later behind the same call."""
import smtplib
from email.message import EmailMessage

from app.config import settings


def compose(headline: str, body: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = f"[{settings.app_name}] {headline}"
    message["From"] = settings.smtp_user
    message["To"] = settings.alert_email_to
    message.set_content(body)
    return message


def send_email(headline: str, body: str) -> bool:
    """Returns True on delivery. Never raises into the scheduler — a failed
    alert is logged and retried on the next run."""
    if not settings.smtp_host or not settings.alert_email_to:
        return False
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(compose(headline, body))
        return True
    except Exception:  # noqa: BLE001 — deliberate: alerting must not crash the job
        return False
