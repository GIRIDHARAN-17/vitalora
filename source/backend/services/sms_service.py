"""
SMS notification service using Twilio.

Configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER
in env.env to enable SMS notifications.
"""

from __future__ import annotations

from backend.core.config import settings


async def send_sms(to_phone: str, message: str) -> bool:
    """
    Send SMS via Twilio.

    Args:
        to_phone: Recipient phone number (E.164 format, e.g. +919876543210)
        message: SMS body (max 1600 chars for single SMS)

    Returns:
        True if sent successfully, False otherwise (e.g. Twilio not configured)
    """
    if not all(
        [
            settings.twilio_account_sid,
            settings.twilio_auth_token,
            settings.twilio_from_number,
        ]
    ):
        return False

    try:
        from twilio.rest import Client

        client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
        )
        client.messages.create(
            body=message,
            from_=settings.twilio_from_number,
            to=to_phone,
        )
        return True
    except Exception:
        return False


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number for Twilio (E.164).
    Adds + if missing; assumes Indian numbers if 10 digits.
    """
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        if len(phone) == 10 and phone.isdigit():
            phone = "+91" + phone
        elif len(phone) == 12 and phone.startswith("91"):
            phone = "+" + phone
        else:
            phone = "+" + phone
    return phone
