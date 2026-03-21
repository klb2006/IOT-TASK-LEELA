# IoT Water Tank Monitoring System

🌊 A modern real-time water tank monitoring dashboard with live sensor data, beautiful animations, and responsive design. Built with React and FastAPI.

## ✨ Features

✅ **Real-time Monitoring** - Live updates every 15 seconds
✅ **Smooth Animations** - Realistic water tank fill with wave effects  
✅ **Sensor Integration** - Temperature, distance, and water level sensors
✅ **Responsive Design** - Works on desktop, tablet, mobile
✅ **Live Status Indicator** - Connection status display
✅ **FastAPI Backend** - High-performance async API
✅ **PostgreSQL Database** - Production-ready data persistence
✅ **Modern UI** - Clean, professional interface

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── run.py                   # Server launcher
│   ├── requirements.txt          # Python dependencies
│   ├── requirements-prod.txt    # Production deps (no TensorFlow)
│   └── saved_models/            # ML models
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── WaterLevelIndicator.js  # Water tank animation
│   │   │   ├── SensorCard.js
│   │   │   └── ProgressBar.js
│   │   ├── pages/               # Route pages
│   │   │   └── Home.js          # Dashboard
│   │   ├── hooks/
│   │   │   └── useSensorData.js
│   │   └── styles/
│   └── package.json
├── README.md                     # This file
├── FRONTEND_DEPLOYMENT.md        # Frontend deployment guide
├── BACKEND_DEPLOYMENT.md         # Backend deployment guide
└── .gitignore
```

## 🎯 Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- Node.js 14+
- Git

### Backend (Port 8000)

```bash
cd backend
pip install -r requirements.txt
python run.py
```

✅ API available at: `http://localhost:8000`
📖 Swagger docs: `http://localhost:8000/docs`

### Frontend (Port 3000)

```bash
cd frontend
npm install
npm start
```

✅ Dashboard available at: `http://localhost:3000`

### Test the System

1. Open browser: `http://localhost:3000`
2. See real sensor data flowing
3. Watch the water tank animation
4. Check connection status

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/status` | System status & health |
| GET | `/api/v1/sensor/latest` | Latest sensor reading |
| GET | `/api/v1/sensor/history` | Sensor data history |
| POST | `/api/v1/predict-water` | Predict water level |
| GET | `/api/v1/model-info` | ML model information |
| GET | `/api/v1/predictions/history` | Prediction history |

## 🚀 Deployment

### Complete Deployment Guides:

📖 **[FRONTEND_DEPLOYMENT.md](./FRONTEND_DEPLOYMENT.md)**
- Step-by-step React app deployment to Render
- Environment configuration
- Build and deploy commands
- Troubleshooting

📖 **[BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md)**
- FastAPI server deployment
- PostgreSQL setup on Render
- Environment variables configuration  
- API health checks

### Quick Summary:

**Backend**: Render Web Service (Python 3.11)
**Frontend**: Render Static Site (Node.js build)
**Database**: Render PostgreSQL
**Total Setup Time**: ~15 minutes

## 📝 Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Key Variables:
- `DB_HOST`: Database host (localhost for dev, render.com host for production)
- `DB_PORT`: Database port (5432)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `VITE_API_URL`: Backend API URL for frontend
- `FRONTEND_URL`: Frontend URL for CORS

## 🎯 Features

✅ Real-time sensor data monitoring
✅ ML-based water level prediction
✅ Historical data visualization
✅ Responsive dashboard
✅ REST API with Swagger documentation
✅ CORS-enabled for cross-origin requests
✅ PostgreSQL data persistence

## 📚 Technologies

**Backend:**
- FastAPI (HTTP framework)
- TensorFlow/Keras (ML)
- Psycopg2 (PostgreSQL adapter)
- Uvicorn (ASGI server)

**Frontend:**
- React 18
- Vite (Build tool)
- Tailwind CSS (Styling)
- Recharts (Charting)
- Lucide React (Icons)

## 🔧 Development

### Run Both Services (Local)

Terminal 1 (Backend):
```bash
cd backend
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### Build Frontend
```bash
cd frontend
npm run build
npm run preview
```

## 📦 Production Build

### Backend
No build needed - runs directly with Python

### Frontend
```bash
cd frontend
npm run build  # Creates dist/ folder
```

## 🚨 Important Notes

⚠️ **Before Production:**
1. Change `allow_origins=["*"]` in backend CORS to specific domains
2. Use environment variables for sensitive data (DB credentials, API keys)
3. Set up proper database with strong passwords
4. Enable HTTPS for all connections
5. Regenerate GitHub token after deployment

## 📞 Support

For issues or questions, check the API documentation at `/docs` or review the code comments.

## 📄 License

This project is part of an academic assessment.

---

**Note**: The ML model (`best_model.h5`) is included in the repository. For production, consider using a dedicated model server.
