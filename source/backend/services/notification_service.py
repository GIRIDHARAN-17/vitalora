"""
Unified notification service: sends alerts via email and SMS.
"""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.services.email_service import send_deterioration_alert
from backend.services.sms_service import normalize_phone, send_sms


def _deterioration_sms_message(
    patient_name: str, patient_id: str, room_no: str, news_score: float
) -> str:
    return (
        f"ICU Alert: Patient {patient_name} (ID:{patient_id}, Room:{room_no}) "
        f"deterioration - NEWS2 score {news_score:.1f}. Immediate attention required."
    )


async def send_deterioration_notification(
    db: AsyncIOMotorDatabase,
    doctor_email: str,
    doctor_phone: str | None,
    patient_phone: str | None,
    patient_id: str,
    patient_name: str,
    room_no: str,
    news_score: float,
) -> None:
    """
    Send deterioration alert to doctor via email and SMS (if phone provided).
    Also sends SMS to all admins with phone numbers.
    """
    # Email to doctor
    await send_deterioration_alert(
        doctor_email=doctor_email,
        patient_id=patient_id,
        patient_name=patient_name,
        room_no=room_no,
        news_score=news_score,
    )

    message = _deterioration_sms_message(
        patient_name, patient_id, room_no, news_score
    )

    # SMS to doctor
    if doctor_phone:
        await send_sms(normalize_phone(doctor_phone), message)

    # SMS to patient (optional)
    if patient_phone:
        await send_sms(normalize_phone(patient_phone), message)

    # SMS to admins
    async for admin in db["admin"].find({"phone_number": {"$exists": True, "$ne": ""}}):
        if admin.get("phone_number"):
            await send_sms(normalize_phone(admin["phone_number"]), message)
