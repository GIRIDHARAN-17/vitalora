from __future__ import annotations

import asyncio
import os
import random
import sys
from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

# Ensure we can import from the backend package
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from backend.core.config import settings
    from backend.services.news2_rules import calculate_news2_score_from_vitals
    from backend.services.notification_service import send_deterioration_notification
except ImportError:
    print("Error: Could not import backend modules. Make sure you are running this from the project root.")
    sys.exit(1)

async def generate_vitals_for_patient(db: Any, patient: dict[str, Any], high_alert: bool) -> None:
    """Generate and store vital signs for a patient."""
    patient_id = patient["patient_id"]
    name = patient.get("name", "Unknown Patient")
    
    if high_alert:
        # Generate critical vitals (Extreme values to trigger alerts)
        vitals = {
            "patient_id": patient_id,
            "timestamp": datetime.utcnow(),
            "respiration_rate": random.randint(25, 35),  # Score 3
            "spo2": random.randint(80, 88),            # Score 3
            "oxygen_support": 5,                       # Score 2
            "systolic_bp": random.randint(70, 85),      # Score 3
            "heart_rate": random.randint(135, 160),     # Score 3
            "temperature": round(random.uniform(39.5, 41.0), 1), # Score 2/3
            "consciousness": random.choice(["V", "P", "U"]), # Score 3
        }
    else:
        # Generate stable, normal vitals
        vitals = {
            "patient_id": patient_id,
            "timestamp": datetime.utcnow(),
            "respiration_rate": random.randint(12, 18),
            "spo2": random.randint(96, 100),
            "oxygen_support": 0,
            "systolic_bp": random.randint(115, 135),
            "heart_rate": random.randint(65, 85),
            "temperature": round(random.uniform(36.4, 37.4), 1),
            "consciousness": "A",
        }
    
    # 1. Store in patient_vitals
    await db["patient_vitals"].insert_one(vitals)
    
    # 2. Calculate NEWS2 Score
    news_score = calculate_news2_score_from_vitals(vitals)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {name} (ID: {patient_id}) - NEWS2: {news_score}")
    
    # 3. Handle Alerting
    if news_score >= 5 or high_alert:
        print(f"  🔴 [ALERT] NEWS2 Score {news_score} is CRITICAL!")
        
        # Fetch doctor phone
        doctor = await db["doctor"].find_one({"email": patient["doctor_email"]})
        doctor_phone = doctor.get("phone_number") if doctor else None
        patient_phone = patient.get("contact_number") or patient.get("phone_number")
        
        # Send Email and SMS notifications
        await send_deterioration_notification(
            db=db,
            doctor_email=patient["doctor_email"],
            doctor_phone=doctor_phone,
            patient_phone=patient_phone,
            patient_id=patient_id,
            patient_name=name,
            room_no=patient.get("room_no", "N/A"),
            news_score=float(news_score)
        )
        print(f"  ✅ Alerts sent to Doctor ({patient['doctor_email']}) and Patient.")

async def run_simulator(high_alert: bool, interval: int) -> None:
    """Main simulation loop."""
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]
    
    print("=" * 60)
    print(" ICU VITALS REAL-TIME SIMULATOR ".center(60, "="))
    print(f" Mode: {'🚨 HIGH ALERT (Simulating Deterioration)' if high_alert else '✅ Normal Monitoring'}")
    print(f" Interval: {interval} seconds")
    print(f" Database: {settings.mongodb_db}")
    print("=" * 60)
    
    try:
        while True:
            # Fetch all patients
            patients = []
            async for p in db["patient"].find({}):
                patients.append(p)
            
            if not patients:
                print("No patients found in the database. Please register patients first.")
            else:
                for patient in patients:
                    try:
                        await generate_vitals_for_patient(db, patient, high_alert)
                    except Exception as e:
                        print(f"Error simulating for {patient.get('patient_id')}: {e}")
            
            print(f"\nCycle complete. Waiting {interval}s for next update...")
            await asyncio.sleep(interval)
            
    except asyncio.CancelledError:
        print("\nSimulator task cancelled.")
    except Exception as e:
        print(f"\nUnexpected error in simulator: {e}")
    finally:
        client.close()
        print("Simulator shutdown complete.")

if __name__ == "__main__":
    # Parse CLI args
    is_high = "--high" in sys.argv
    
    # Default interval: 2 minutes as requested, but shorter (30s) if not specified for better demo feel
    # unless they strictly want 2 or 5.
    interval_sec = 120 
    if "--interval" in sys.argv:
        try:
            idx = sys.argv.index("--interval")
            interval_sec = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            pass
    elif "--fast" in sys.argv:
        interval_sec = 5 # Very fast for testing
        
    try:
        asyncio.run(run_simulator(is_high, interval_sec))
    except KeyboardInterrupt:
        print("\nManually stopped by user.")
