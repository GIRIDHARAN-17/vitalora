# Vitalora Web Frontend

A responsive web dashboard for ICU patient monitoring, built with vanilla HTML5, CSS3, and JavaScript. Provides real-time vital signs display, NEWS2 scoring, risk analysis, and alert management for doctors and administrators.

## 📋 Overview

The frontend communicates with the FastAPI backend at `http://localhost:8000` to display:

- Patient vital signs and trends
- Real-time NEWS2 risk scores
- Active patient alerts
- Doctor dashboards
- Risk analysis and predictions

**Demo Pages:**

- Dashboard - Patient overview
- Patient Details - Individual patient vitals history
- News Score - NEWS2 scoring visualization
- Risk Analysis - Risk stratification
- Pattern Predictions - AI-powered predictions
- Pandemic Threshold - Disease severity trends

## 🛠️ Tech Stack

- **HTML5** - Semantic markup
- **CSS3** - Responsive grid/flexbox styling
- **JavaScript (ES6+)** - Vanilla (no frameworks)
- **API Client** - Fetch API
- **Storage** - LocalStorage for JWT tokens and settings

## 🚀 Quick Start

### Prerequisites

- HTTP server (Python, Node, or browser)
- Backend API running at http://localhost:8000

### Run Locally

**Option 1: Python HTTP Server**

```powershell
python -m http.server 8080 --directory frontend
# Access: http://localhost:8080
```

**Option 2: Node Live Server**

```powershell
npm install -g live-server
live-server frontend
# Auto-opens browser
```

**Option 3: VS Code Live Server Extension**

- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

## 📁 Project Structure

```
frontend/
├── index.html                # Home page
├── css/
│   └── style.css            # All styling (responsive design)
├── js/
│   ├── main.js              # Global setup, auth, navigation
│   ├── dashboard.js         # Patient list and overview
│   ├── patient-details.js   # Individual patient vitals
│   └── posts.js             # News/alerts display
├── pages/
│   ├── dashboard.html       # Patient dashboard
│   ├── patient-details.html # Patient detail view
│   ├── news-score.html      # NEWS2 scoring UI
│   ├── risk-analysis.html   # Risk stratification
│   ├── pattern-predictions.html  # Predictions
│   ├── pandemic-threshold.html   # Severity trends
│   ├── login.html           # Login page
│   ├── about.html           # About page
│   ├── features.html        # Features page
│   └── posts.html           # Posts/alerts
└── assets/                  # Images and media

```

## 🔧 Configuration

### Backend API URL

Edit `js/main.js`:

```javascript
const API_BASE_URL = "http://localhost:8000"; // Change if needed
```

### JWT Token Storage

Tokens are stored in `localStorage` under key `access_token`.

## 📖 API Integration

### Authentication

```javascript
// Login
POST /auth/login
{ "email": "user@example.com", "password": "..." }
Response: { "access_token": "...", "token_type": "bearer" }

// Token is auto-stored in localStorage
```

### Patient Data

```javascript
// Get patients
GET /doctor/patients
Headers: { "Authorization": "Bearer {token}" }

// Get patient vitals
GET /doctor/patients/{patient_id}/vitals

// Get alerts
GET /doctor/alerts
```

## 🎨 Styling

### Color Scheme

- **Primary**: Dark blue (#1a2c4a)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Danger**: Red (#ef4444)

### Responsive Breakpoints

- **Desktop**: 1024px+
- **Tablet**: 768px - 1023px
- **Mobile**: <768px

## 🔐 Security

### HTTPS (Production)

Always use HTTPS in production:

```javascript
const API_BASE_URL = "https://your-domain.com/api";
```

### CORS

Backend must allow frontend origin:

```python
# backend/core/config.py
ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "https://your-domain.com"
]
```

### Token Handling

- Tokens stored in localStorage (consider sessionStorage for sensitive environments)
- Auto-refresh on 401 responses
- Clear on logout

## 🚨 Common Issues

### CORS Error

**Problem:** "Access to XMLHttpRequest has been blocked by CORS policy"

**Solution:**

1. Verify backend is running: `http://localhost:8000/docs`
2. Check CORS_ORIGINS in backend .env
3. Ensure API_BASE_URL in main.js matches backend address

### No Data Displayed

1. Check browser DevTools (F12) → Console for errors
2. Verify JWT token in localStorage: `localStorage.getItem('access_token')`
3. Login again if token expired
4. Verify backend has patient data

### Styling Issues

1. Hard refresh: `Ctrl+Shift+Delete` (DevTools) or `Ctrl+Shift+R`
2. Clear browser cache
3. Check style.css is loaded in DevTools → Network tab

## 📱 Mobile Responsiveness

Desktop-first design:

- Auto-scales for tablets (landscape and portrait)
- Mobile optimized (touch-friendly buttons, readable text)
- Horizontal scrolling for wide tables on small screens

Test with browser DevTools → Device Toolbar (Ctrl+Shift+M)

## 📊 Real-time Updates

Currently uses **manual polling** (refresh page to see updates).

**Future:** Implement WebSocket for real-time live updates:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/patient-alerts");
ws.onmessage = (event) => updateDashboard(event.data);
```

## 🧪 Testing

### Manual Testing

1. Open DevTools (F12)
2. Check Console tab for JavaScript errors
3. Check Network tab to verify API calls
4. Monitor LocalStorage for token presence

### Test Accounts

Use credentials created via backend:

```powershell
python -m backend.scripts.create_admin --email doctor@test.com --password test123
```

## 🔗 Backend Integration Points

| Page            | Endpoint                       | Method |
| --------------- | ------------------------------ | ------ |
| Dashboard       | `/doctor/patients`             | GET    |
| Patient Details | `/doctor/patients/{id}/vitals` | GET    |
| Alerts          | `/doctor/alerts`               | GET    |
| News Score      | `/patient/vitals`              | GET    |
| Risk Analysis   | `/admin/analysis`              | GET    |

## 📚 Resources

- [MDN Web Docs](https://developer.mozilla.org/)
- [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [Responsive Design](https://web.dev/responsive-web-design-basics/)

## 🚀 Deployment

### Static Hosting (GitHub Pages, Vercel, Netlify)

```bash
# Copy frontend directory to host
# Set API_BASE_URL to production backend URL
```

### Docker

```dockerfile
FROM nginx:alpine
COPY frontend/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Configuration

For multiple environments, use a config file:

```javascript
// config.js
const configs = {
  development: { API_BASE_URL: "http://localhost:8000" },
  production: { API_BASE_URL: "https://api.vitalora.com" },
};
const ENV = process.env.NODE_ENV || "development";
export default configs[ENV];
```

## 📋 Features

- ✅ Patient dashboard with vital signs
- ✅ Real-time alert display
- ✅ NEWS2 score visualization
- ✅ JWT authentication
- ✅ Responsive design
- ✅ Dark/glass theme support
- 🔄 WebSocket real-time updates (planned)
- 🔄 Export to PDF (planned)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes maintaining code style
3. Test on multiple screen sizes
4. Commit with clear message
5. Push and create Pull Request

### Code Style

- Use meaningful variable names
- Add comments for complex logic
- Keep CSS organized (media queries at end)
- Use semantic HTML5 elements

## 📄 License

Proprietary - All rights reserved

---

**Last Updated**: March 2026 | **Version**: 1.0.0
