from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    role: Literal["admin", "doctor"]


class AddDoctorRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    specialization: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(min_length=10, max_length=15)


class DoctorOut(BaseModel):
    name: str
    email: EmailStr
    specialization: str
    phone_number: str | None = None
    role: Literal["doctor"] = "doctor"


class AddPatientRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    patient_id: str = Field(min_length=1, max_length=64)
    room_no: str = Field(min_length=1, max_length=32)
    condition: str = Field(min_length=10, max_length=255)
    doctor_email: EmailStr
    age: int
    gender: Literal["male", "female", "other"]
    contact_number: str = Field(min_length=10, max_length=15)
    address: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=120)
    state: str = Field(min_length=1, max_length=120)
    room_no: str = Field(min_length=1, max_length=32)


class PatientOut(BaseModel):
    patient_id: str
    name: str
    room_no: str
    condition: str
    doctor_email: EmailStr
    age: int
    gender: Literal["male", "female", "other"]
    contact_number: str
    address: str
    city: str
    state: str


class VitalOut(BaseModel):
    patient_id: str
    timestamp: datetime
    respiration_rate: int
    spo2: int
    oxygen_support: int
    systolic_bp: int
    heart_rate: int
    temperature: float
    consciousness: str


class NewsTrendPointOut(BaseModel):
    patient_id: str
    timestamp: datetime
    news_score: float
    outbreak_severity: float
    adjusted_score: float
    alert_level: Literal["low", "medium", "high", "critical"]


class AnalyzePatientRequest(BaseModel):
    patient_id: str = Field(min_length=1, max_length=64)
    location: str = Field(min_length=1, max_length=120)


class AnalyzePatientResponse(BaseModel):
    news_score: float
    outbreak_severity: float
    adjusted_score: float
    alert_level: Literal["low", "medium", "high", "critical"]

class AddVitalRequest(BaseModel):
    patient_id: str = Field(min_length=1, max_length=64)
    timestamp: datetime | None = None  # If None, uses current time
    respiration_rate: int = Field(ge=0, le=60)
    spo2: int = Field(ge=0, le=100)
    oxygen_support: int = Field(ge=0, le=100)
    systolic_bp: int = Field(ge=0, le=300)
    heart_rate: int = Field(ge=0, le=250)
    temperature: float = Field(ge=30.0, le=45.0)
    consciousness: Literal["A", "V", "P", "U"] = Field(description="A=Alert, V=Voice, P=Pain, U=Unresponsive")


class BulkAddVitalsRequest(BaseModel):
    patient_id: str = Field(min_length=1, max_length=64)
    vitals: list[AddVitalRequest] = Field(min_length=1, max_length=100)