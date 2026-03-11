from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.api.deps import require_admin
from backend.api.schemas import AddDoctorRequest, AddPatientRequest, DoctorOut, PatientOut, AddVitalRequest, BulkAddVitalsRequest, VitalOut
from backend.database.mongodb import get_db
from backend.utils.security import hash_password
from datetime import datetime, timedelta

router = APIRouter(dependencies=[Depends(require_admin)])


@router.post("/add_doctor", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
async def add_doctor(
    req: AddDoctorRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> DoctorOut:
    existing = await db["doctor"].find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=409, detail="Doctor already exists")

    doc = {
        "name": req.name,
        "email": req.email,
        "password_hash": hash_password(req.password),
        "role": "doctor",
        "specialization": req.specialization,
        "phone_number": req.phone_number,
    }
    await db["doctor"].insert_one(doc)
    return DoctorOut(name=req.name, email=req.email, specialization=req.specialization, phone_number=req.phone_number)


@router.post("/add_patient", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def add_patient(
    req: AddPatientRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> PatientOut:
    # ensure doctor exists
    doctor = await db["doctor"].find_one({"email": req.doctor_email})
    if not doctor:
        raise HTTPException(status_code=404, detail="Assigned doctor not found")

    existing = await db["patient"].find_one({"patient_id": req.patient_id})
    if existing:
        raise HTTPException(status_code=409, detail="Patient already exists")

    patient = {
        "patient_id": req.patient_id,
        "name": req.name,
        "age": req.age,
        "gender": req.gender,
        "contact_number": req.contact_number,
        "address": req.address,
        "city": req.city,
        "state": req.state,
        "room_no": req.room_no,
        "condition": req.condition,
        "doctor_email": req.doctor_email,
    }
    await db["patient"].insert_one(patient)
    return PatientOut(**patient)


@router.get("/doctors", response_model=list[DoctorOut])
async def list_doctors(db: AsyncIOMotorDatabase = Depends(get_db)) -> list[DoctorOut]:
    docs: list[DoctorOut] = []
    async for d in db["doctor"].find({}, {"_id": 0, "password_hash": 0}):
        docs.append(DoctorOut(**d))
    return docs


@router.get("/patients", response_model=list[PatientOut])
async def list_patients(db: AsyncIOMotorDatabase = Depends(get_db)) -> list[PatientOut]:
    patients: list[PatientOut] = []
    async for p in db["patient"].find({}, {"_id": 0}):
        patients.append(PatientOut(**p))
    return patients

@router.post("/patient/{patient_id}/vitals", response_model=VitalOut, status_code=status.HTTP_201_CREATED)
async def add_patient_vital(
    patient_id: str,
    vital: AddVitalRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> VitalOut:
    """Add a single vital sign record for a patient."""
    # Verify patient exists
    patient = await db["patient"].find_one({"patient_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Use provided timestamp or current time
    timestamp = vital.timestamp if vital.timestamp else datetime.utcnow()
    
    vital_doc = {
        "patient_id": patient_id,
        "timestamp": timestamp,
        "respiration_rate": vital.respiration_rate,
        "spo2": vital.spo2,
        "oxygen_support": vital.oxygen_support,
        "systolic_bp": vital.systolic_bp,
        "heart_rate": vital.heart_rate,
        "temperature": vital.temperature,
        "consciousness": vital.consciousness,
    }
    
    await db["patient_vitals"].insert_one(vital_doc)
    return VitalOut(**vital_doc)


@router.post("/patient/{patient_id}/vitals/bulk", response_model=dict, status_code=status.HTTP_201_CREATED)
async def bulk_add_patient_vitals(
    patient_id: str,
    req: BulkAddVitalsRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    """Add multiple vital sign records for a patient at once."""
    # Verify patient exists
    patient = await db["patient"].find_one({"patient_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Ensure all vitals are for the same patient
    if any(v.patient_id != patient_id for v in req.vitals):
        raise HTTPException(status_code=400, detail="All vitals must be for the same patient_id")
    
    vital_docs = []
    base_time = datetime.utcnow()
    
    for i, vital in enumerate(req.vitals):
        # If no timestamp provided, space them 1 hour apart
        timestamp = vital.timestamp if vital.timestamp else base_time - timedelta(hours=len(req.vitals) - i - 1)
        
        vital_doc = {
            "patient_id": patient_id,
            "timestamp": timestamp,
            "respiration_rate": vital.respiration_rate,
            "spo2": vital.spo2,
            "oxygen_support": vital.oxygen_support,
            "systolic_bp": vital.systolic_bp,
            "heart_rate": vital.heart_rate,
            "temperature": vital.temperature,
            "consciousness": vital.consciousness,
        }
        vital_docs.append(vital_doc)
    
    if vital_docs:
        await db["patient_vitals"].insert_many(vital_docs)
    
    return {
        "message": f"Successfully added {len(vital_docs)} vital records",
        "patient_id": patient_id,
        "count": len(vital_docs),
    }


@router.post("/patient/{patient_id}/vitals/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_sample_vitals(
    patient_id: str,
    count: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    """Generate sample vital sign records for testing (30 records by default)."""
    # Verify patient exists
    patient = await db["patient"].find_one({"patient_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if count < 1 or count > 100:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 100")
    
    import random
    
    # Realistic ranges for ICU vitals
    vital_docs = []
    base_time = datetime.utcnow()
    
    for i in range(count):
        # Generate realistic values with some variation
        timestamp = base_time - timedelta(hours=count - i - 1)
        
        vital_doc = {
            "patient_id": patient_id,
            "timestamp": timestamp,
            "respiration_rate": random.randint(12, 24),
            "spo2": random.randint(92, 100),
            "oxygen_support": random.choice([0, 0, 0, 2, 4, 6]),  # Mostly no support, some low flow
            "systolic_bp": random.randint(100, 140),
            "heart_rate": random.randint(60, 100),
            "temperature": round(random.uniform(36.5, 38.5), 1),
            "consciousness": random.choice(["A", "A", "A", "V"]),  # Mostly Alert
        }
        vital_docs.append(vital_doc)
    
    await db["patient_vitals"].insert_many(vital_docs)
    
    return {
        "message": f"Successfully generated {count} sample vital records",
        "patient_id": patient_id,
        "count": count,
    }