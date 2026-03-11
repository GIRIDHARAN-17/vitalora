# Vitalora - Backend API

Production-ready FastAPI backend for ICU patient deterioration monitoring with real-time alerts, LSTM predictions, and multi-channel notifications.

## 📋 Overview

The Vitalora backend provides:
- **REST API** - RESTful endpoints for patient monitoring
- **Real-time Monitoring** - Automatic patient monitoring service (60-second intervals)
- **LSTM Predictions** - Neural network-based NEWS2 score prediction
- **Multi-Channel Alerts** - Email and SMS notifications
- **JWT Authentication** - Secure role-based access control
- **MongoDB Database** - Async data persistence
- **LLM Integration** - Disease severity analysis with Ollama

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115.8
- **Server**: Uvicorn 0.30.6
- **Database**: MongoDB 5.0+ with Motor (async)
- **Authentication**: JWT + Argon2 hashing
- **ML/AI**: TensorFlow 2.17.1, scikit-learn, LangChain, Ollama
- **Notifications**: SMTP (Gmail), Twilio
- **Web Scraping**: BeautifulSoup4
- **Server**: Python 3.10+

See [requirements.txt](../requirements.txt) for full dependency list.

## 🚀 Quick Start

### 1. Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file in project root:

```env
# MongoDB (local or Atlas)
MONGODB_URI=mongodb://localhost:27017/vitalora
# OR for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/vitalora?retryWrites=true&w=majority

# Authentication
JWT_SECRET=your-secret-key-must-be-at-least-32-characters-long
JWT_EXPIRE_MINUTES=1440  # 24 hours

# Email Alerts (Gmail)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-16-char-app-password  # App password, not regular password
EMAIL_FROM_NAME=Vitalora Alerts

# SMS Alerts (Twilio - optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890

# LLM Configuration (optional)
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Disease Signal Collection
DISEASE_UPDATE_INTERVAL_MINUTES=60

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:8888

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

### 4. ML Model Files

Place trained models in `backend/models/`:

- `news_lstm_regression.h5` - LSTM model for NEWS2 prediction
- `news_scaler.save` - Feature scaler (joblib)
- `consciousness_encoder.save` - Label encoder (joblib)

These files are auto-loaded on startup.

### 5. Setup Ollama (Optional - for LLM features)

Install Ollama: https://ollama.ai

```powershell
# Pull a language model
ollama pull llama3
# OR: ollama pull mistral

# Start Ollama service
ollama serve
```

Ollama runs on `http://localhost:11434` by default.

### 6. Start Backend

```powershell
# Development (with auto-reload)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Production (no reload)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Access:**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 📡 API Endpoints

### Authentication

```
POST /auth/login
Content-Type: application/json

{
  "email": "doctor@hospital.com",
  "password": "securepassword"
}

Response: {
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "doctor@hospital.com",
    "role": "doctor"
  }
}
```

### Admin Endpoints (requires admin role)

```
POST /admin/users
- Create new user (admin/doctor)

GET /admin/users
- List all users with pagination

PUT /admin/users/{user_id}
- Update user details

DELETE /admin/users/{user_id}
- Delete user

POST /admin/patients
- Register new patient

GET /admin/patients
- List all patients

GET /admin/analysis
- System-wide analysis and statistics
```

### Doctor Endpoints (requires doctor role)

```
GET /doctor/patients
- Get all assigned patients

GET /doctor/patients/{patient_id}
- Get specific patient details

GET /doctor/patients/{patient_id}/vitals
- Get patient vitals history (with pagination)

GET /doctor/alerts
- Get active alerts for assigned patients

POST /doctor/alerts/{alert_id}/acknowledge
- Mark alert as acknowledged

GET /doctor/reports/{patient_id}
- Generate risk report for patient
```

### Patient Endpoints

```
POST /patient/vitals
- Submit new vital signs
{
  "heart_rate": 92,
  "respiratory_rate": 18,
  "systolic_bp": 135,
  "diastolic_bp": 85,
  "temperature": 37.5,
  "oxygen_saturation": 98,
  "consciousness_level": "Alert"
}

GET /patient/vitals
- Get personal vitals history

GET /patient/alerts
- Get personal alerts
```

Full API documentation available at `/docs` when backend is running.

## 💾 Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique),
  hashed_password: String (Argon2),
  role: String ("admin" | "doctor" | "nurse"),
  full_name: String,
  phone: String,
  is_active: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Patients Collection
```javascript
{
  _id: ObjectId,
  patient_id: String (unique, e.g., "P-101"),
  full_name: String,
  age: Number,
  gender: String ("M" | "F"),
  admission_date: DateTime,
  assigned_doctor_id: ObjectId (ref: Users),
  condition: String,
  allergies: [String],
  created_at: DateTime,
  updated_at: DateTime
}
```

### Vitals Collection
```javascript
{
  _id: ObjectId,
  patient_id: ObjectId (ref: Patients),
  timestamp: DateTime,
  heart_rate: Number (50-150 bpm),
  respiratory_rate: Number (8-40 breaths/min),
  systolic_bp: Number (mmHg),
  diastolic_bp: Number (mmHg),
  temperature: Number (35-42°C),
  oxygen_saturation: Number (88-100%),
  consciousness_level: String ("Alert" | "Verbal" | "Pain" | "Unresponsive"),
  news2_score: Number (0-20),
  created_at: DateTime,
  updated_at: DateTime
}
```

### Alerts Collection
```javascript
{
  _id: ObjectId,
  patient_id: ObjectId (ref: Patients),
  severity: String ("low" | "medium" | "high" | "critical"),
  alert_type: String ("vitals" | "prediction" | "manual"),
  message: String,
  triggered_at: DateTime,
  triggered_by: String (service name),
  acknowledged_at: DateTime,
  acknowledged_by: ObjectId (ref: Users),
  is_active: Boolean,
  data: {
    news2_score: Number,
    vital_causing_alert: String
  }
}
```

## 🔄 Core Services

### Real-time Monitoring Service
Runs automatically on backend startup:

```python
# Monitors all patients every 60 seconds
# Calculates NEWS2 scores from latest vitals
# Compares against dynamic thresholds
# Triggers email/SMS alerts if critical
# Stores/updates alert status in database
```

### LSTM Prediction Engine
```python
# Predicts NEWS2 score 1-2 hours ahead
# Uses past 4 hours of vital signs
# Input: Time-series vital data
# Output: Predicted score + confidence
# Triggers early warning alerts
```

### Disease Signal Collector
```python
# Searches web for disease outbreaks/pandemic updates
# Scrapes news using BeautifulSoup
# Runs every 60 minutes (configurable)
# Updates severity context in database
```

### Severity Analyzer (LLM)
```python
# Uses LangChain + Ollama for disease severity analysis
# Processes web disease signals
# Generates severity scores
# Adjusts alert thresholds dynamically
```

### Alert Services
- **Email Service**: Sends Gmail SMTP notifications
- **SMS Service**: Sends Twilio SMS notifications
- Both triggered on critical patient deterioration

## 🧪 Testing & Data Generation

### Generate Synthetic Data

```powershell
# Create synthetic ICU dataset
python -m backend.scripts.generate_data
# Creates fake patients and vitals in CSV

# Train LSTM model (if needed)
python -m backend.scripts.train_lstm
```

### Simulate Patient Vitals

Perfect for testing alerts and dashboards:

```powershell
# Normal stable vitals (auto-healthy data)
python -m backend.scripts.simulate_vitals --patient-id P-101 \
  --interval-seconds 120 --mode normal

# Force HIGH vitals (triggers alerts!)
python -m backend.scripts.simulate_vitals --patient-id P-101 \
  --interval-seconds 10 --mode high --steps 40

# Gradually deteriorating (realistic scenario)
python -m backend.scripts.simulate_vitals --patient-id P-101 \
  --interval-seconds 30 --mode deteriorating --steps 20
```

### Create Admin User

```powershell
python -m backend.scripts.create_admin \
  --email admin@hospital.com \
  --password securepassword123
```

## 🔐 Authentication & Authorization

### JWT Token Flow
1. User logs in with email + password
2. Backend verifies against Argon2 hash
3. If valid, JWT token issued with user role
4. Token valid for 24 hours (JWT_EXPIRE_MINUTES in .env)
5. Client includes token in Authorization header

### User Roles
- **Admin**: Full system access, user management
- **Doctor**: Monitor assigned patients, acknowledge alerts
- **Nurse**: Enter vitals, view patient data (optional)

### Token Refresh
```python
# After 24 hours, client automatically logged out
# Must login again to receive new token
# No refresh token endpoint (stateless design)
```

## 📁 Project Structure

```
backend/
├── main.py                  # FastAPI app entry point
├── api/                     # API Route handlers
│   ├── __init__.py
│   ├── auth_routes.py       # Login, token refresh
│   ├── admin_routes.py      # User & admin endpoints
│   ├── doctor_routes.py     # Doctor patient endpoints
│   ├── patient_routes.py    # Patient vitals endpoints
│   ├── deps.py              # Auth dependencies, pagination
│   └── schemas.py           # Pydantic request/response models
├── services/                # Business logic
│   ├── __init__.py
│   ├── monitor_service.py   # Real-time monitoring (bg task)
│   ├── lstm_predictor.py    # LSTM prediction engine
│   ├── news2_rules.py       # NEWS2 score calculation
│   ├── severity_analyzer.py # LLM-based analysis
│   ├── threshold_engine.py  # Dynamic alert thresholds
│   ├── disease_signal_collector.py  # Web scraping
│   ├── email_service.py     # SMTP email notifications
│   ├── sms_service.py       # Twilio SMS notifications
│   ├── notification_service.py      # Alert orchestration
│   ├── monitor_service.py   # Background monitoring
│   └── vitals_simulator.py  # Test data generation
├── database/
│   ├── __init__.py
│   └── mongodb.py           # MongoDB connection & setup
├── utils/
│   ├── __init__.py
│   ├── jwt_handler.py       # JWT token creation/validation
│   └── security.py          # Argon2 password hashing
├── core/
│   ├── __init__.py
│   └── config.py            # Settings from .env
├── models/                  # ML models (NOT in git)
│   ├── news_lstm_regression.h5
│   ├── news_scaler.save
│   ├── consciousness_encoder.save
│   └── README.md            # Model documentation
├── scripts/                 # Utility scripts
│   ├── __init__.py
│   ├── create_admin.py      # Create admin user
│   ├── generate_data.py     # Synthetic ICU data
│   ├── train_lstm.py        # Train LSTM model
│   ├── simulate_vitals.py   # Simulate patient vitals
│   └── populate_db.py       # Populate test data
├── dataset/
│   └── synthetic_icu_timeseries.csv  # Sample dataset
└── __pycache__/             # Compiled Python files
```

## 🚨 Error Handling

### Common Errors

**401 Unauthorized**
- Invalid or expired JWT token
- Solution: Login again to get new token

**403 Forbidden**
- Authenticated but insufficient permissions
- Solution: Use correct role (admin vs doctor)

**422 Unprocessable Entity**
- Invalid request body format
- Solution: Check Swagger docs at /docs for request format

**500 Internal Server Error**
- Backend exception
- Solution: Check server logs, verify .env config

## 🐛 Troubleshooting

### MongoDB Connection Issues

**Error:** "Connection refused"
```powershell
# Ensure MongoDB is running
# Local: mongod
# Atlas: Verify URI and network access

# Test connection:
mongosh "mongodb://localhost:27017/vitalora"
```

### LSTM Model Not Found

**Error:** "news_lstm_regression.h5 not found"
```powershell
# Place model files in backend/models/
# Files needed:
# - news_lstm_regression.h5
# - news_scaler.save
# - consciousness_encoder.save
```

### Ollama Connection Failed

**Error:** "Connection refused" for Ollama
```powershell
# Start Ollama:
ollama serve

# Test connection:
curl http://localhost:11434/api/tags
```

### Email Alerts Not Sending

**Error:** "SMTPAuthenticationError"
```
1. Use Gmail App Password (not regular password)
2. Enable 2FA on Gmail account
3. Verify EMAIL_USER and EMAIL_PASS in .env
4. Check recipient email addresses are valid
```

### SMS Not Sending

**Error:** "Twilio API error"
```
1. Verify TWILIO_ACCOUNT_SID and AUTH_TOKEN
2. Ensure TWILIO_FROM_NUMBER is verified
3. Recipient phone number format: +1234567890
```

### Import Errors

**Error:** "ModuleNotFoundError"
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

## 📊 Performance Optimization

### Database Indexing
```python
# Create indexes for faster queries
db.patients.create_index("patient_id", unique=True)
db.vitals.create_index("patient_id")
db.vitals.create_index("timestamp", -1)  # Reverse for latest first
db.alerts.create_index("patient_id")
db.alerts.create_index("is_active")
```

### Connection Pooling
```python
# Motor handles connection pooling automatically
# Default: 50 connections per replica set
# Adjust if needed in config.py
```

### Pagination
```python
# All list endpoints use pagination
GET /doctor/patients?skip=0&limit=20
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```powershell
docker build -t vitalora-backend .
docker run -p 8000:8000 --env-file .env vitalora-backend
```

### Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Use production MongoDB cluster (Atlas)
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up environment variables on server
- [ ] Use strong JWT_SECRET (32+ chars)
- [ ] Enable CORS for frontend domain only
- [ ] Run with multiple workers: `--workers 4`
- [ ] Set up log aggregation
- [ ] Configure monitoring/alerting
- [ ] Regular database backups

## 🧮 NEWS2 Scoring System

The National Early Warning Score 2 (NEWS2) combines vital signs:

| Parameter | 0 | 1 | 2 | 3 |
|-----------|---|---|---|---|
| HR (bpm) | 51-90 | 41-50 / 91-110 | 111-130 | ≤40 or ≥131 |
| RR (breaths/min) | 12-20 | 9-11 / 21-24 | ≤8 or ≥25 | - |
| SBP (mmHg) | 111-219 | 101-110 / 220-229 | 91-100 / ≥230 | ≤90 |
| DBP (mmHg) | 51-90 | 41-50 / 91-110 | ≤40 or ≥111 | - |
| Temp (°C) | 36.1-38.0 | 35.1-36.0 / 38.1-39.0 | ≤35.0 or ≥39.1 | - |
| O2 Sat (%) | ≥96 | 94-95 | 92-93 | ≤91 |
| Consciousness | Alert | - | - | Verbal/Pain/Unresponsive |

**Total Score Interpretation:**
- 0-4: Low risk (green)
- 5-6: Medium risk (yellow)
- 7-8: High risk (orange)
- ≥9: Critical risk (red)

## 📚 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [MongoDB Python Docs](https://pymongo.readthedocs.io/)
- [TensorFlow LSTM Guide](https://tensorflow.org/guide/keras/rnn)
- [NEWS2 Official](https://www.rcplondon.ac.uk/news-scoring-system)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)

## 📄 License

Proprietary - All rights reserved

---

**Last Updated**: March 2026 | **Version**: 1.0.0 | **Status**: Production Ready


