# Vitalora - ICU Early Warning System

An intelligent patient monitoring system for ICU environments using AI-powered predictive analytics to detect patient deterioration early, enabling timely clinical interventions.

## 📋 Quick Overview

Vitalora combines **LSTM AI models**, **real-time monitoring**, and **multi-channel alerts** to detect ICU patient deterioration before it becomes critical.

**Key Features:**

- LSTM-based NEWS2 score prediction
- Real-time vital signs monitoring (every 60 seconds)
- Dynamic alert thresholding
- Email & SMS notifications
- Multi-user dashboard (Admin, Doctor roles)
- Web disease signal integration

## 🏗️ Project Structure

```
vitalora/
├── backend/               # FastAPI REST API + monitoring service  → See backend/README.md
├── frontend/              # Web dashboard (HTML/JS/CSS)           → See frontend/README.md
├── flutter_app/           # Flutter mobile app (template version)  → See flutter_app/README.md
├── vitalora_app/          # Flutter mobile app (primary)           → See vitalora_app/README.md
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Getting Started

### Quick Prerequisites

- **Python 3.10+** + MongoDB
- **Flutter 3.4+** (for mobile, optional)
- **.env file** with credentials (see sections below)

### 1. Backend Setup (5 min)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Configure .env:**

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/vitalora
JWT_SECRET=your-secret-key-min-32-chars
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
```

**Run:**

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

→ **Full guide**: [backend/README.md](backend/README.md)

### 3. Mobile Apps (Optional)

**Primary App (vitalora_app):**

```powershell
cd vitalora_app
flutter pub get
flutter run
```

→ **Full guide**: [vitalora_app/README.md](vitalora_app/README.md)

**Alternative (flutter_app):**
→ **Full guide**: [flutter_app/README.md](flutter_app/README.md)

## 🛠️ Tech Stack

| Component          | Technologies                                      |
| ------------------ | ------------------------------------------------- |
| **Backend**        | FastAPI, Uvicorn, MongoDB, Motor                  |
| **ML/AI**          | TensorFlow, LSTM, Scikit-learn, LangChain, Ollama |
| **Alerts**         | Email (SMTP), SMS (Twilio)                        |
| **Frontend**       | HTML5, CSS3, JavaScript                           |
| **Mobile**         | Flutter 3.4+, Dart, Riverpod, GoRouter            |
| **Authentication** | JWT, Argon2                                       |

## 📁 Documentation by Component

| Component                              | README                     | Purpose                                 |
| -------------------------------------- | -------------------------- | --------------------------------------- |
| [Backend](backend/README.md)           | Core API, Models, Services | FastAPI REST API + Real-time monitoring |
| [Frontend](frontend/README.md)         | Web Dashboard              | Doctor/Admin web interface              |
| [vitalora_app](vitalora_app/README.md) | Mobile App (Primary)       | Flutter mobile application              |
| [flutter_app](flutter_app/README.md)   | Mobile Template            | Flutter reference template              |
| [Models](backend/models/README.md)     | ML Models                  | LSTM, Scalers, Encoders documentation   |

## 🚀 Quick Commands

```powershell
# Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Python)
python -m http.server 8080 --directory frontend

# Frontend (Node)
npx live-server frontend

# Mobile
cd vitalora_app && flutter run
```

## 📋 Features

- ✅ Real-time patient monitoring (60s intervals)
- ✅ LSTM-based NEWS2 prediction
- ✅ Multi-channel alerts (Email, SMS)
- ✅ Dynamic thresholding
- ✅ JWT authentication
- ✅ Dashboard + Mobile interfaces

## 🔗 Quick Links

- **API Docs**: http://localhost:8000/docs (after running backend)
- **Web Dashboard**: http://localhost:8080 (after running frontend)
- **GitHub**: [Repository URL]
- **Issues**: Internal tracking

## 📄 License

Proprietary - All rights reserved

---

**Last Updated**: March 2026 | **Version**: 1.0.0
