from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.core.config import settings
from backend.database.mongodb import get_db
from backend.services.disease_signal_collector import collect_disease_signals
from backend.services.notification_service import send_deterioration_notification
from backend.services.lstm_predictor import predict_news_score
from backend.services.news2_rules import calculate_news2_score_from_vitals
from backend.services.severity_analyzer import analyze_outbreak_severity
from backend.services.threshold_engine import (
    adjusted_thresholds,
    compute_adjusted_score,
    compute_alert_level,
)


class MonitorService:
    _running: bool = False
    _task: asyncio.Task | None = None

    @classmethod
    async def start(cls) -> None:
        """Start the monitoring service."""
        if cls._running:
            return
        cls._running = True
        cls._task = asyncio.create_task(cls._monitor_loop())

    @classmethod
    async def stop(cls) -> None:
        """Stop the monitoring service."""
        cls._running = False
        if cls._task:
            await cls._task
            cls._task = None

    @classmethod
    async def _monitor_loop(cls) -> None:
        """Main monitoring loop that runs every monitor_interval_seconds."""
        db = get_db()

        while cls._running:
            try:
                await cls._monitor_all_patients(db)
            except Exception:
                # Log error in production, continue monitoring
                pass

            await asyncio.sleep(settings.monitor_interval_seconds)

    @classmethod
    async def _monitor_all_patients(cls, db: AsyncIOMotorDatabase) -> None:
        """Monitor all patients and trigger alerts if needed."""
        # Get all patients
        patients = []
        async for p in db["patient"].find({}, {"_id": 0}):
            patients.append(p)

        for patient in patients:
            try:
                await cls._analyze_patient(db, patient)
            except Exception:
                # Continue with next patient on error
                continue

    @classmethod
    async def _analyze_patient(
        cls, db: AsyncIOMotorDatabase, patient: dict
    ) -> None:
        """Analyze a single patient and trigger alert if critical."""
        patient_id = patient["patient_id"]
        condition = patient.get("condition", "covid-19")
        # Default location, could be stored in patient doc
        location = patient.get("location", "Chennai")

        # Fetch latest 30 vitals (then reverse to chronological for LSTM)
        vitals_cursor = (
            db["patient_vitals"]
            .find({"patient_id": patient_id}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(30)
        )

        vitals_list = []
        async for v in vitals_cursor:
            vitals_list.append(v)

        if len(vitals_list) < 30:
            # Not enough data yet
            return

        vitals_list = list(reversed(vitals_list))

        # Run LSTM prediction
        try:
            lstm_score = predict_news_score(vitals_list)
        except Exception:
            return

        # Rule-based score from the latest vitals to ensure high vitals => high score in demos
        rule_score = float(calculate_news2_score_from_vitals(vitals_list[-1]))

        # Use the higher of LSTM or rule-based
        news_score = float(max(lstm_score, rule_score))

        # Collect disease signals
        article_text = await collect_disease_signals(condition, location)

        # Analyze outbreak severity
        severity_result = await analyze_outbreak_severity(article_text, condition)
        outbreak_severity = severity_result.get("severity_score", 0.3)

        # Adjust thresholds and compute alert level
        thresholds = adjusted_thresholds(outbreak_severity)
        adjusted_score = compute_adjusted_score(news_score, outbreak_severity)
        alert_level = compute_alert_level(adjusted_score, thresholds)

        # Store trend point for graphing (always)
        trend_doc = {
            "patient_id": patient_id,
            "timestamp": datetime.utcnow(),
            "news_score": float(news_score),
            "lstm_score": float(lstm_score),
            "rule_score": float(rule_score),
            "outbreak_severity": float(outbreak_severity),
            "adjusted_score": float(adjusted_score),
            "alert_level": alert_level,
        }
        await db["patient_news_trend"].insert_one(trend_doc)

        # Sustained-high alert: if last N points are high/critical, notify doctor + admins
        n = max(2, int(settings.sustained_alert_points))
        recent_points = []
        cursor = (
            db["patient_news_trend"]
            .find({"patient_id": patient_id}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(n)
        )
        async for p in cursor:
            recent_points.append(p)

        sustained_high = (
            len(recent_points) == n
            and all(p.get("alert_level") in ("high", "critical") for p in recent_points)
        )

        # Check if we should alert (only if critical and not already alerted recently)
        if alert_level == "critical" or sustained_high:
            # Check if alert was already sent in last 5 minutes
            cooldown_minutes = int(
                settings.sustained_alert_cooldown_minutes) if sustained_high else 5
            since = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
            recent_alert = await db["alerts"].find_one(
                {
                    "patient_id": patient_id,
                    "alert_level": "critical" if not sustained_high else {"$in": ["high", "critical"]},
                    "timestamp": {"$gte": since},
                    "reason": "sustained_high" if sustained_high else {"$exists": True},
                },
                sort=[("timestamp", -1)],
            )

            if not recent_alert:
                # Fetch doctor for phone number
                doctor = await db["doctor"].find_one(
                    {"email": patient["doctor_email"]},
                    {"phone_number": 1},
                )
                doctor_phone = doctor.get("phone_number") if doctor else None
                patient_phone = patient.get(
                    "contact_number") or patient.get("phone_number")

                # Send email + SMS to doctor and admins
                await send_deterioration_notification(
                    db=db,
                    doctor_email=patient["doctor_email"],
                    doctor_phone=doctor_phone,
                    patient_phone=patient_phone,
                    patient_id=patient_id,
                    patient_name=patient["name"],
                    room_no=patient["room_no"],
                    news_score=adjusted_score,
                )

                # Store alert record
                alert_doc = {
                    "patient_id": patient_id,
                    "doctor_email": patient["doctor_email"],
                    "news_score": float(adjusted_score),
                    "alert_level": alert_level,
                    "timestamp": datetime.utcnow(),
                    "reason": "sustained_high" if sustained_high else "critical",
                }
                await db["alerts"].insert_one(alert_doc)

    @classmethod
    def is_running(cls) -> bool:
        """Check if monitoring service is running."""
        return cls._running
