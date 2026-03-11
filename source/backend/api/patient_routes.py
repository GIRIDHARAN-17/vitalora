from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.api.deps import get_current_user_payload, require_doctor
from backend.api.schemas import AnalyzePatientRequest, AnalyzePatientResponse
from backend.database.mongodb import get_db
from backend.services.disease_signal_collector import collect_disease_signals
from backend.services.email_service import send_deterioration_alert
from backend.services.lstm_predictor import predict_news_score
from backend.services.news2_rules import calculate_news2_score_from_vitals
from backend.services.severity_analyzer import analyze_outbreak_severity
from backend.services.threshold_engine import (
    adjusted_thresholds,
    compute_adjusted_score,
    compute_alert_level,
)


router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzePatientResponse,
    dependencies=[Depends(require_doctor)],
)
async def analyze_patient(
    req: AnalyzePatientRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> AnalyzePatientResponse:
    """
    Analyze patient vitals, predict NEWS2 score, check disease signals,
    adjust thresholds, and determine alert level.
    """
    # Fetch patient
    patient = await db["patient"].find_one({"patient_id": req.patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Verify doctor access
    doctor_email = payload.get("sub")
    if patient["doctor_email"] != doctor_email:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Fetch latest 30 vitals (then reverse to chronological order for LSTM)
    vitals_cursor = (
        db["patient_vitals"]
        .find({"patient_id": req.patient_id}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(30)
    )

    vitals_list = []
    async for v in vitals_cursor:
        vitals_list.append(v)

    if len(vitals_list) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient vitals data. Need 30 records, found {len(vitals_list)}",
        )

    vitals_list = list(reversed(vitals_list))

    # Step 1: Run LSTM prediction
    lstm_score = predict_news_score(vitals_list)
    rule_score = float(calculate_news2_score_from_vitals(vitals_list[-1]))
    news_score = float(max(lstm_score, rule_score))

    # Step 2: Collect disease signals from web
    condition = patient.get("condition", "covid-19")
    article_text = await collect_disease_signals(condition, req.location)

    # Step 3: Analyze outbreak severity using LLM
    severity_result = await analyze_outbreak_severity(article_text, condition)
    outbreak_severity = severity_result.get("severity_score", 0.3)

    # Step 4: Adjust thresholds and compute adjusted score
    thresholds = adjusted_thresholds(outbreak_severity)
    adjusted_score = compute_adjusted_score(news_score, outbreak_severity)
    alert_level = compute_alert_level(adjusted_score, thresholds)

    # Step 5: If critical, send email alert and store alert record
    if alert_level == "critical":
        await send_deterioration_alert(
            doctor_email=patient["doctor_email"],
            patient_id=req.patient_id,
            patient_name=patient["name"],
            room_no=patient["room_no"],
            news_score=adjusted_score,
        )

        # Store alert in database
        alert_doc = {
            "patient_id": req.patient_id,
            "doctor_email": patient["doctor_email"],
            "news_score": float(adjusted_score),
            "alert_level": alert_level,
            "timestamp": datetime.utcnow(),
        }
        await db["alerts"].insert_one(alert_doc)

    return AnalyzePatientResponse(
        news_score=round(news_score, 2),
        outbreak_severity=round(outbreak_severity, 3),
        adjusted_score=round(adjusted_score, 2),
        alert_level=alert_level,
    )
