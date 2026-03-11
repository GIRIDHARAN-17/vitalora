from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.admin_routes import router as admin_router
from backend.api.auth_routes import router as auth_router
from backend.api.doctor_routes import router as doctor_router
from backend.api.patient_routes import router as patient_router
from backend.core.config import settings
from backend.database.mongodb import Mongo, get_db
from backend.services.monitor_service import MonitorService
from backend.services.news2_rules import calculate_news2_score_from_vitals
from fastapi import Depends
from fastapi.responses import StreamingResponse
import csv
import io
import motor.motor_asyncio
from datetime import datetime


def create_app() -> FastAPI:
    app = FastAPI(
        title="ICU AI Early Warning Backend",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.parsed_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def _startup() -> None:
        Mongo.connect()
        await MonitorService.start()

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await MonitorService.stop()
        Mongo.close()

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(admin_router, prefix="/admin", tags=["admin"])
    app.include_router(doctor_router, prefix="/doctor", tags=["doctor"])
    app.include_router(patient_router, prefix="/patient", tags=["patient"])

    @app.get("/auto_stream")
    async def auto_stream(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
        latest_vital = await db["patient_vitals"].find_one(sort=[("timestamp", -1)])
        if not latest_vital:
            return {"status": "error", "message": "No data"}
        
        news_score = calculate_news2_score_from_vitals(latest_vital)
        
        return {
            "hr": latest_vital["heart_rate"],
            "spo2": latest_vital["spo2"],
            "bp": latest_vital["systolic_bp"],
            "resp": latest_vital["respiration_rate"],
            "temp": latest_vital["temperature"],
            "oxygen": latest_vital["oxygen_support"],
            "gcs": latest_vital["consciousness"],
            "news": news_score,
            "time": latest_vital["timestamp"].strftime("%H:%M:%S")
        }

    @app.get("/export_csv")
    async def export_csv(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Patient ID", "Time", "HR", "SpO2", "BP", "Resp", "Temp", "Oxygen", "GCS"])
        
        async for v in db["patient_vitals"].find().sort("timestamp", -1).limit(200):
            writer.writerow([
                v.get("patient_id", "N/A"),
                v["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(v["timestamp"], datetime) else v["timestamp"],
                v.get("heart_rate", ""),
                v.get("spo2", ""),
                v.get("systolic_bp", ""),
                v.get("respiration_rate", ""),
                v.get("temperature", ""),
                v.get("oxygen_support", ""),
                v.get("consciousness", "")
            ])
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=vitals_export.csv"}
        )

    return app


app = create_app()

