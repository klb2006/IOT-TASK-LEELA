# Complete System Architecture - Water Tank IoT with ML Activity Classification

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          YOUR SYSTEM                             │
└─────────────────────────────────────────────────────────────────┘

     ESP32 IoT Device              Backend Server              Database
     ═════════════════            ═══════════════            ════════════
     
  ┌─────────────────┐          ┌──────────────────┐       ┌──────────────┐
  │  Ultrasonic     │          │  FastAPI main.py │       │  PostgreSQL  │
  │  + Temp Sensor  │─HTTP POST─→ /api/v1/        │       │   Database   │
  │                 │ (JSON)     │ predict-activity│──────→│              │
  │ Every 20 sec    │          │                  │       │ sensor_data  │
  └─────────────────┘          └──────────────────┘       │ predictions  │
        │                            │                     └──────────────┘
        │                            ↓
        │                      ┌──────────────────┐
        │                      │ ml_training/     │
        │                      │ activity_        │
        └─────────────────────→ classifier.py    │
         (distance, temp)      │                  │
                               │ model32.h5 (GRU)│
                               │                  │
                               │ → Predicts:     │
                               │  - no_activity   │
                               │  - filling       │
                               │  - flush         │
                               │  - washing_m...  │
                               │  - geyser        │
                               └──────────────────┘
```

---

## 🔄 Data Flow

### 1. IoT Device (ESP32) Collects Data
**Every 20 seconds:**
```cpp
// Gets sensor readings
int distance = getDistance();        // cm (ultrasonic sensor)
float temperature = tempSensor...;   // °C

// Converts to water metrics
waterLevel = tankHeight - distance;
waterPercent = (waterLevel / tankHeight) * 100;
waterLiters = (waterLevel / tankHeight) * tankCapacity;

// Sends to backend
sendToBackendAPI(distance, temperature);
```

**HTTP Request to backend:**
```json
POST /api/v1/predict-activity HTTP/1.1
Host: 192.168.29.128:8001
Content-Type: application/json
Content-Length: 45

{
  "distance": 50.0,
  "temperature": 28.5,
  "node_id": "node-1"
}
```

---

### 2. Backend Receives Request

**Endpoint: `POST /api/v1/predict-activity`**

```python
@app.post("/api/v1/predict-activity")
async def predict_water_activity(request: dict):
    # Extract sensor data
    distance = request['distance']
    temperature = request.get('temperature', 25.0)
    
    # Call activity classifier
    from ml_training.activity_classifier import predict_activity
    result = predict_activity(distance, temperature)
    
    return result
```

---

### 3. Activity Classifier Processes Data

**File: `backend/ml_training/activity_classifier.py`**

```python
def predict_activity(distance, temperature, prev_distance=None):
    # Load GRU model (model32.h5)
    model = load_gru_model()
    
    # Extract features from raw sensor data
    features = extract_features_from_distance(
        distance, 
        temperature,
        prev_distance
    )
    
    # Scale features (0-1 range)
    scaler = load_scaler()
    features_scaled = scaler.transform([features])
    
    # Make prediction using GRU model
    prediction_probs = model.predict(features_scaled)
    activity = ACTIVITY_LABELS[argmax(prediction_probs)]
    confidence = max(prediction_probs)
    
    return {
        'activity': activity,           # 'filling', 'flush', etc.
        'confidence': confidence,       # 0.85
        'probabilities': {...}         # Breakdown per class
    }
```

**Features extracted (4 inputs to GRU):**
```
[distance, temperature, diff (slope), slope (rate)]
```

**GRU Model (trained in your Colab):**
- **Architecture**: 2 GRU layers (128, 64 units)
- **Dropouts**: 0.3, 0.2, 0.2 (prevents overfitting)
- **Output**: 5 classes (no_activity, filling, flush, washing_machine, geyser)
- **Accuracy**: 85.95%
- **F1-Score**: 0.6881

---

### 4. Backend Returns Prediction

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "activity": "filling",
  "confidence": 0.89,
  "distance": 50.0,
  "temperature": 28.5,
  "probabilities": {
    "no_activity": 0.05,
    "filling": 0.89,
    "flush": 0.03,
    "washing_machine": 0.02,
    "geyser": 0.01
  },
  "node_id": "node-1",
  "timestamp": "2024-03-21T14:30:00"
}
```

---

### 5. Data Stored in Database

**Table: `predictions`**
```sql
INSERT INTO predictions (
    node_id,
    distance,
    temperature,
    water_percent,
    prediction,
    confidence,
    created_at
) VALUES (
    'node-1',
    50.0,
    28.5,
    0,
    'filling',
    0.89,
    NOW()
);
```

**Query to see predictions:**
```sql
SELECT * FROM predictions 
WHERE node_id = 'node-1'
ORDER BY created_at DESC 
LIMIT 20;
```

---

## 📁 File Structure

```
IOT-TASK-LEELA-main/
│
├── backend/
│   ├── main.py                          ← Backend API with endpoints
│   ├── config.py                        ← Configuration
│   ├── requirements.txt                 ← Dependencies
│   │
│   ├── saved_models/
│   │   ├── model32.h5          ⭐      ← YOUR TRAINED GRU MODEL
│   │   ├── scaler.pkl                  ← Data scaler (optional)
│   │   └── ...
│   │
│   └── ml_training/
│       ├── activity_classifier.py       ← NEW: GRU classifier
│       ├── model_loader.py              ← Old model loader
│       └── model_loader_colab.py        ← Colab regression models
│
├── frontend/                             ← React frontend for dashboard
│   └── src/
│       ├── App.js
│       ├── pages/
│       │   ├── Home.js
│       │   ├── Prediction.js
│       │   └── ...
│       └── ...
│
├── IoT_Firmware/
│   └── water_tank.ino                   ← ESP32 code (your code)
│
├── ACTIVITY_CLASSIFICATION_SETUP.md     ← NEW: Setup guide
├── verify_setup.py                      ← NEW: Verification script
├── COLAB_INTEGRATION_GUIDE.md            ← Regression models guide
└── MODEL_PRECISION_GUIDE.md              ← Model accuracy guide
```

---

## 🔧 Endpoints Available

### Activity Classification (NEW)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/predict-activity` | Predict water activity from distance sensor |
| GET | `/api/v1/activity-model-info` | Get model metadata (accuracy, activities, etc.) |

### Original Endpoints (Still Available)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/predict-water` | Predict next water percentage (regression) |
| GET | `/api/v1/sensor/latest` | Get latest sensor data |
| GET | `/api/v1/sensor/history` | Get sensor history |
| GET | `/api/v1/predictions/history` | Get prediction history |

---

## 🚀 Deployment Checklist

### Local Testing
- [ ] Copy `model32.h5` to `backend/saved_models/`
- [ ] Run verification: `python verify_setup.py`
- [ ] Start backend: `python backend/main.py`
- [ ] Get backend IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- [ ] Update ESP32 code with backend IP
- [ ] Upload ESP32 code and open serial monitor
- [ ] Verify activity predictions appear in serial output

### Cloud Deployment (Render/Heroku)
- [ ] Push code to GitHub
- [ ] Update backend IP in environment variables
- [ ] Deploy backend
- [ ] Update ESP32 with cloud backend URL
- [ ] Deploy frontend to static hosting
- [ ] Test with cloud URL

---

## 📊 Example Scenarios

### Scenario 1: Water Filling

**Time**: T=0s
```
Distance: 86 cm (sensor reads high, water far away)
Activity: no_activity
Confidence: 0.92
```

**Time**: T=10s
```
Distance: 70 cm (water level rising)
Activity: filling
Confidence: 0.87
```

**Time**: T=30s
```
Distance: 50 cm (water rising continues)
Activity: filling
Confidence: 0.91
```

**Time**: T=60s
```
Distance: 45 cm (water stopped rising)
Activity: no_activity
Confidence: 0.88
```

**Database records:**
```sql
SELECT * FROM predictions ORDER BY created_at;

| activity    | confidence | distance | timestamp          |
|-------------|------------|----------|-------------------|
| no_activity | 0.92       | 86       | 2024-03-21 14:00  |
| filling     | 0.87       | 70       | 2024-03-21 14:00:10 |
| filling     | 0.91       | 50       | 2024-03-21 14:00:30 |
| no_activity | 0.88       | 45       | 2024-03-21 14:01   |
```

---

### Scenario 2: Toilet Flush

**Time**: T=0s
```
Distance: 45 cm (normal)
Activity: no_activity
```

**Time**: T=2s
```
Distance: 80 cm (water drains suddenly!)
Slope: -35 cm/s (RAPID change)
Activity: flush
Confidence: 0.93
```

**Time**: T=3s
```
Distance: 45 cm (refilled by pump)
Activity: no_activity
```

---

## 🔍 Monitoring & Analytics

### Track Activity Patterns

```sql
-- Most common activity per day
SELECT 
    DATE(created_at) as date,
    prediction as activity,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM predictions
GROUP BY DATE(created_at), prediction
ORDER BY date DESC, count DESC;
```

**Output:**
```
date       | activity    | count | avg_confidence
-----------|-------------|-------|---------------
2024-03-21 | no_activity | 287   | 0.94
2024-03-21 | filling     | 45    | 0.87
2024-03-21 | flush       | 12    | 0.91
2024-03-21 | geyser      | 8     | 0.76
```

### Detect Anomalies

```sql
-- High confidence predictions of unusual activities
SELECT * FROM predictions
WHERE prediction IN ('flush', 'geyser')
AND confidence > 0.8
ORDER BY created_at DESC
LIMIT 10;
```

---

## 📱 Frontend Integration

Your React frontend can display:

```javascript
// Get latest activity
GET /api/v1/activity-model-info

// Display predictions history
GET /api/v1/predictions/history?limit=100

// Real-time dashboard
setInterval(async () => {
  const response = await fetch('/api/v1/sensor/latest');
  const data = await response.json();
  
  // Show: Current activity, Confidence, Water %, Time
  updateDashboard(data);
}, 10000);
```

---

## ✅ Success Criteria

Your system is working correctly when:

1. ✓ ESP32 boots and connects to WiFi
2. ✓ Serial monitor shows: "Detecting activity: filling" (every 20s)
3. ✓ Backend logs show: "[OK] Activity prediction successful"
4. ✓ Database has predictions: `SELECT COUNT(*) FROM predictions; → > 0`
5. ✓ Frontend dashboard shows activity history
6. ✓ Accuracy is consistent: >80% confidence for most predictions

---

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Model not found" | missing model32.h5 | Place in `backend/saved_models/` |
| "Backend connection failed" | Wrong IP/port | Update `#define BACKEND_SERVER` in ESP32 |
| "Low confidence" | Sensor data out of range | Calibrate ultrasonic sensor |
| "Always no_activity" | Feature scaling mismatch | Verify scaler.pkl |
| "API timeout" | Backend too slow | Check if model is loading |

---

## 📚 Related Documentation

- [ACTIVITY_CLASSIFICATION_SETUP.md](ACTIVITY_CLASSIFICATION_SETUP.md) - Detailed setup guide
- [COLAB_INTEGRATION_GUIDE.md](COLAB_INTEGRATION_GUIDE.md) - Using regression models
- [MODEL_PRECISION_GUIDE.md](MODEL_PRECISION_GUIDE.md) - Understanding metrics
- [FastAPI Docs](http://127.0.0.1:8000/docs) - Interactive API documentation
- [Swagger UI](http://127.0.0.1:8000/swagger) - Request/response examples

---

## 🎯 Next Features to Implement

1. **Anomaly Detection** - Detect leaks (constant flush without usage)
2. **Predictive Maintenance** - Predict when tank needs cleaning
3. **Usage Trends** - Identify peak usage hours
4. **Smart Alerts** - Notify when pump fails to refill
5. **Multi-Node Support** - Track multiple tanks/locations
6. **ML Retraining** - Auto-retrain model with new data monthly

---

Generated: 2024-03-21
For support: Check error messages and refer to documentation above
