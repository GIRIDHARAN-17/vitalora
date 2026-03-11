from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.core.config import settings


async def send_deterioration_alert(
    doctor_email: str,
    patient_id: str,
    patient_name: str,
    room_no: str,
    news_score: float,
) -> None:
    """
    Send email alert to doctor about patient deterioration.

    Args:
        doctor_email: Doctor's email address
        patient_id: Patient ID
        patient_name: Patient name
        room_no: Room number
        news_score: Predicted NEWS2 score
    """
    if not settings.email_user or not settings.email_pass:
        # Email not configured, skip silently or log
        return

    msg = MIMEMultipart()
    msg["From"] = f"{settings.email_from_name} <{settings.email_user}>"
    msg["To"] = doctor_email
    msg["Subject"] = "ICU Patient Deterioration Alert"

    body = f"""
Patient ID: {patient_id}
Name: {patient_name}
Room: {room_no}

Predicted NEWS2 Score: {news_score:.2f}

Immediate medical attention required.

---
ICU Early Warning System
    """.strip()

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.email_user, settings.email_pass)
            server.send_message(msg)
    except Exception:
        # Log error in production, but don't crash the service
        pass
