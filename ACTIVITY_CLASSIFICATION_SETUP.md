# Water Activity Classification Setup Guide

## 📊 What You Have

| Component | Details |
|-----------|---------|
| **Model** | `model32.h5` - GRU neural network for activity classification |
| **Accuracy** | 85.95% (F1-Score: 0.6881) |
| **Activities Detected** | no_activity, filling, flush, washing_machine, geyser |
| **Dataset** | 42,028 labeled water usage samples |
| **IoT Device** | ESP32 with ultrasonic sensor + temperature sensor |

---

## 🚀 Setup Steps

### STEP 1: Save the Model File

Place your trained model in the correct directory:

```
backend/saved_models/model32.h5
```

Your folder structure should look like:
```
backend/
├── main.py
├── config.py
├── saved_models/
│   ├── model32.h5                    ← YOUR TRAINED MODEL
│   ├── scaler.pkl (optional)
│   └── ...
├── ml_training/
│   ├── activity_classifier.py        ← NEW MODULE
│   └── model_loader.py
└── ...
```

### STEP 2: Verify Activity Classifier Module

The new file `backend/ml_training/activity_classifier.py` provides:
- `load_gru_model()` - Loads your model32.h5
- `predict_activity()` - Makes predictions
- Feature engineering for sensor data

### STEP 3: Update IoT Code (ESP32)

Your ESP32 code already has the correct endpoint! Just verify:

**Correct (in your code):**
```cpp
#define BACKEND_SERVER "192.168.29.128"  // ✓ Your backend IP
#define BACKEND_PORT 8001                 // ✓ Change if needed

void sendToBackendAPI(int distance, float temperature) {
  String url = "/api/v1/predict-activity";  // ✓ CORRECT ENDPOINT
  
  String jsonPayload = "{\"distance\":" + String(distance) + ",\"node_id\":\"node-1\"}";
  // ✓ Sends distance to backend
}
```

**What IoT sends:**
```json
{
  "distance": 50.0,        # cm from ultrasonic sensor
  "temperature": 28.5,     # °C
  "node_id": "node-1"      # Device ID
}
```

### STEP 4: Verify Backend Is Updated

The backend now has the new endpoint:
- **Endpoint**: `POST /api/v1/predict-activity`
- **Function**: `predict_water_activity()` in `main.py`
- **Uses**: `activity_classifier.py` to load and run model32.h5

---

## 🧪 Testing the System

### Test 1: Direct Model Test

```bash
cd backend
python -c "from ml_training.activity_classifier import predict_activity; \
print(predict_activity(distance=50.0, temperature=28.0, return_probs=True))"
```

Expected output:
```python
{
    'status': 'success',
    'activity': 'no_activity',  # Or detected activity
    'confidence': 0.85,
    'distance': 50.0,
    'temperature': 28.0,
    'probabilities': {
        'no_activity': 0.70,
        'filling': 0.15,
        'flush': 0.10,
        'washing_machine': 0.04,
        'geyser': 0.01
    }
}
```

### Test 2: API Endpoint Test

**Without running backend:**
```bash
# Check if model file exists
ls -la backend/saved_models/model32.h5
```

**With backend running:**
```bash
# Start backend
python backend/main.py

# In another terminal, test the activity prediction endpoint:
curl -X POST "http://127.0.0.1:8000/api/v1/predict-activity" \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 50.0,
    "temperature": 28.5,
    "node_id": "node-1"
  }'
```

Expected response:
```json
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

### Test 3: Model Info Endpoint

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/activity-model-info"
```

Response shows:
```json
{
  "status": "success",
  "model": {
    "model": "GRU (model32.h5)",
    "accuracy": "85.95%",
    "f1_score": "0.6881",
    "activities": ["no_activity", "filling", "flush", "washing_machine", "geyser"],
    "num_classes": 5
  }
}
```

### Test 4: IoT Device Test

**On your ESP32, the code already sends data:**

```cpp
void sendToBackendAPI(int distance, float temperature) {
  // This connects to backend and sends activity prediction request
  if (client.connect(BACKEND_SERVER, BACKEND_PORT)) {
    String jsonPayload = "{\"distance\":" + String(distance) + ",\"node_id\":\"node-1\"}";
    String url = "/api/v1/predict-activity";
    
    client.print(String("POST ") + url + " HTTP/1.1\r\n" + ...);
    delay(1000);
    while (client.available()) {
      String line = client.readStringUntil('\n');
      Serial.println(line);  // Prints response from backend
    }
  }
}
```

**Serial output should show:**
```
200 OK
...JSON response...
Detected activity: filling
Backend API call complete
```

---

## 📈 Understanding Activity Predictions

### What Each Activity Means

| Activity | Indicator | Distance Pattern | Example |
|----------|-----------|------------------|---------|
| **no_activity** | Tank is idle | Stable distance | No water usage |
| **filling** | Water being added to tank | Distance decreases steadily | Pump running, manually filling |
| **flush** | Rapid water removal | Sharp distance increase | Toilet flush, emergency drain |
| **washing_machine** | Extended usage | Multiple change cycles | Washing machine running |
| **geyser** | Hot water usage | Special temperature pattern | Water heater active |

### How Model Detects Activities

The model uses **4 features** extracted from sensor data:

```python
features = [
    distance,           # Current ultrasonic reading (cm)
    temperature,        # Current temperature (°C)
    diff,              # Change from previous reading (slope)
    slope              # Rate of change (acceleration)
]
```

**Example patterns:**
- **Filling**: distance -2cm/sec (water rising), temp ~same
- **Flush**: distance +5cm/sec (water draining), sudden change
- **No activity**: distance ~0cm/sec, temp ~same
- **Washing machine**: alternating patterns
- **Geyser**: high temperature + stable distance

---

## 🔧 Debugging

### Issue 1: Model File Not Found

**Error message:**
```
[ERROR] Model not found at backend/saved_models/model32.h5
```

**Solution:**
1. Verify file exists: `ls backend/saved_models/`
2. Check file size (should be >1MB): `ls -lh backend/saved_models/model32.h5`
3. Ensure it's not corrupted - try loading in Python:
   ```python
   import tensorflow as tf
   model = tf.keras.models.load_model('backend/saved_models/model32.h5')
   print(model.summary())
   ```

### Issue 2: IoT Device Can't Connect to Backend

**Error in ESP32 serial:**
```
Backend connection failed
```

**Solution:**
1. Verify backend is running: `python backend/main.py`
2. Check backend is listening on port 8001:
   ```bash
   netstat -ano | findstr 8001  # Windows
   lsof -i :8001                # Mac/Linux
   ```
3. Verify IP address (check `#define BACKEND_SERVER`):
   ```bash
   ipconfig getifaddr en0  # Mac
   ipconfig               # Windows
   ```

### Issue 3: Low Confidence Predictions

**Symptoms:**
```json
{
  "activity": "filling",
  "confidence": 0.45    # ← TOO LOW (<0.70)
}
```

**Causes:**
- Model needs retraining with more data
- Feature ranges don't match training data
- Sensor calibration is off

**Solution:**
1. Collect more training data (target: 500+ samples per activity)
2. Retrain the model with Colab script
3. Verify sensor readings are in expected range:
   - Distance: 0-100 cm
   - Temperature: 15-40°C

### Issue 4: All Predictions are "no_activity"

**Cause:**
- Model isn't learning the patterns
- Distance/temperature data is too stable

**Solution:**
1. Verify IoT sensor is working:
   - Distance should change when water level changes
   - Temperature should vary with ambient conditions
2. Check sensor calibration
3. Test with manual distance changes:
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/v1/predict-activity" \
     -d '{"distance": 10.0}' & # Lower distance = water rising
   curl -X POST "http://127.0.0.1:8000/api/v1/predict-activity" \
     -d '{"distance": 80.0}' & # Higher distance = water draining
   ```

---

## 📝 File Reference

| File | Purpose | Status |
|------|---------|--------|
| `backend/saved_models/model32.h5` | Trained GRU model | ✅ You have this |
| `backend/ml_training/activity_classifier.py` | Model loader & prediction | ✅ Created |
| `backend/main.py` | Updated with `/api/v1/predict-activity` endpoint | ✅ Updated |
| ESP32 code (your `.ino`) | Sends distance to backend | ✅ Already correct |

---

## 🎯 Quick Start Checklist

- [ ] Copy `model32.h5` to `backend/saved_models/`
- [ ] Verify `activity_classifier.py` exists in `backend/ml_training/`
- [ ] Start backend: `python backend/main.py`
- [ ] Upload ESP32 code to device
- [ ] Get ESP32 IP: Serial monitor should show it
- [ ] Update `#define BACKEND_SERVER` in ESP32 code with backend IP
- [ ] Test API: `curl -X POST http://BACKEND_IP:8001/api/v1/predict-activity -d '{"distance": 50}'`
- [ ] Check serial output on ESP32 - should show activity name

---

## 🚀 Next Steps

1. **Validate Model Performance**
   - Collect real water usage examples
   - Verify predictions match actual activities
   - Track accuracy over time

2. **Improve Accuracy**
   - Collect more training data (imbalanced classes → focus on minority classes)
   - Retrain model with augmented data
   - Fine-tune hyperparameters

3. **Production Deployment**
   - Set up monitoring dashboard
   - Log all predictions to database
   - Create alerts for abnormal patterns
   - Implement feedback loop to retrain monthly

4. **Advanced Features**
   - Combine with water level prediction (regression model)
   - Predict when to refill tank
   - Detect leaks (flush without any usage)
   - Optimize pumping schedules

---

## 📞 Troubleshooting

For issues, check these logs:
1. **Backend logs**: `python backend/main.py` (verbose output)
2. **ESP32 serial**: Arduino Serial Monitor at 115200 baud
3. **Database logs**: Check if predictions are stored: 
   ```sql
   SELECT * FROM predictions ORDER BY created_at DESC LIMIT 10;
   ```

For more help, see:
- `MODEL_PRECISION_GUIDE.md` - Understanding model metrics
- `COLAB_INTEGRATION_GUIDE.md` - Using regression models from Colab
- [TensorFlow docs](https://www.tensorflow.org/api_docs)
- [ESP32 docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
