# How to Use Your Real Colab-Trained Models

## 🔴 Current Problem
Your backend is using a **fake dummy model** (`best_model.h5` with only 8 hardcoded samples). Your real trained models are still in **Google Colab**.

## ✅ Solution: Download Colab Models & Integrate

### STEP 1: Download Files from Google Colab

Go to your Colab notebook and run this at the end:

```python
# Download all files locally
from google.colab import files

print("Downloading trained models...")
files.download("scaler.pkl")
files.download("xgboost.pkl")
files.download("random_forest.pkl")
files.download("linear_regression.pkl")
files.download("lstm_model.h5")
files.download("gru_model.h5")
files.download("best_model_name.txt")
files.download("model_comparison_results.csv")
print("[OK] Downloads complete!")
```

### STEP 2: Upload Files to Backend

All files go in: `backend/saved_models/`

```
backend/saved_models/
├── scaler.pkl                           ⭐ CRITICAL
├── best_model_name.txt                  (e.g., "XGBoost")
├── xgboost.pkl
├── random_forest.pkl
├── linear_regression.pkl
├── lstm_model.h5
├── gru_model.h5
└── model_comparison_results.csv
```

**Replace** the current dummy `best_model.h5` with your real trained models!

### STEP 3: Verify File Structure

Check that your saved_models folder has all files:

```bash
# In Windows PowerShell:
dir backend\saved_models\
```

Should show:
```
    Directory: C:\...\backend\saved_models

Mode                 LastWriteTime         Length Name
----                 -----------          ------ ----
-a---          2024-03-21  14:30           12345 scaler.pkl
-a---          2024-03-21  14:30          543210 xgboost.pkl
-a---          2024-03-21  14:30            5678 best_model_name.txt
-a---          2024-03-21  14:30          987654 random_forest.pkl
-a---          2024-03-21  14:30          234567 linear_regression.pkl
-a---          2024-03-21  14:30         1234567 lstm_model.h5
-a---          2024-03-21  14:30         2345678 gru_model.h5
-a---          2024-03-21  14:30           67890 model_comparison_results.csv
```

### STEP 4: Update Backend Code

Create a new file `backend/use_colab_models.py` to use the real models:

```python
from ml_training.model_loader_colab import (
    predict_water_percent,
    get_best_model_name,
    get_available_models,
    get_model_comparison,
    load_scaler
)

# Test the models are loaded
print("Available models:", get_available_models())
print("Best model:", get_best_model_name())

# Make a test prediction
result = predict_water_percent(
    distance=20.5,
    temperature=28.3,
    water_percent=75.0,
    water_liters=150.0,
    minute=30,
    hour=14,
    day=21,
    dayofweek=3,
    prev_water_percent=74.5,
    prev_water_liters=149.0,
    prev_distance=20.6
)

print(f"\nPrediction: {result}")
```

### STEP 5: Update main.py to Use Real Models

Replace the import in `backend/main.py`:

**OLD:**
```python
from ml_training.model_loader import predict_water_percent  # FAKE MODEL
```

**NEW:**
```python
from ml_training.model_loader_colab import predict_water_percent  # REAL COLAB MODELS
```

---

## 📊 Understanding Your Colab Model

Your Colab training script does:

1. **Loads 11 Features** (not 3 like dummy model):
   - `distance` - Distance sensor reading (cm)
   - `temperature` - Temperature (°C)
   - `water_percent` - Current water level (%)
   - `water_liters` - Water volume (L)
   - `minute` - Current minute (0-59)
   - `hour` - Current hour (0-23)
   - `day` - Day of month
   - `dayofweek` - Day of week (0-6)
   - `prev_water_percent` - Previous water level
   - `prev_water_liters` - Previous water volume
   - `prev_distance` - Previous distance reading

2. **Trains 5 Different Models**:
   - Linear Regression
   - Random Forest
   - XGBoost ← Usually best
   - LSTM (neural network for sequences)
   - GRU (another sequence model)

3. **Predicts**: The **NEXT water_percent** (regression, not classification)
   - NOT classifying "LOW/MEDIUM/HIGH/FULL"
   - Predicting the actual next value like: 75.3%, 74.8%, etc.

4. **Evaluates on Test Data**: Shows REAL metrics:
   - Training accuracy (how well it memorized)
   - Test accuracy (how well it generalizes) ← THE REAL ONE
   - MAE, RMSE, R² scores

---

## 🚀 How to Use in Your Backend

### Simple Prediction
```python
from ml_training.model_loader_colab import predict_water_percent

# Current sensor readings
result = predict_water_percent(
    distance=20.5,
    temperature=28.3,
    water_percent=75.0,
    water_liters=150.0,
    minute=30,
    hour=14
)

if result['status'] == 'success':
    next_water = result['prediction']  # e.g., 74.8
    print(f"Predicted next water level: {next_water}%")
    
    # Show on frontend
    return {
        "current_water": 75.0,
        "predicted_next": next_water,
        "model": result['model_used'],
        "confidence": result['confidence']
    }
```

### Compare All Models
```python
from ml_training.model_loader_colab import get_model_comparison

results = get_model_comparison()
# Shows: MAE, RMSE, R² for each model
# Tells you which performed best
```

---

## ⚠️ Troubleshooting

### Error: "Scaler not found"
→ Upload `scaler.pkl` to `backend/saved_models/`

### Error: "Best model name not found"
→ Upload `best_model_name.txt` to `backend/saved_models/`

### Error: "XGBoost/LSTM/GRU model not loaded"
→ Upload the corresponding `.pkl` or `.h5` file

### Predictions are always the same
→ Check if the model file is actually from Colab (not dummy)
→ Verify scaler.pkl matches the training data

### Predictions don't make sense
→ Ensure all 11 features are provided (or set defaults)
→ Check feature ranges match your training data

---

## 📈 Next Steps

1. ✅ Download files from Colab
2. ✅ Upload to `backend/saved_models/`
3. ✅ Update `main.py` imports
4. ✅ Restart backend: `python backend/main.py`
5. ✅ Test predictions via API

---

## Testing the API

Once models are loaded, test with:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 20.5,
    "temperature": 28.3,
    "water_percent": 75.0,
    "water_liters": 150.0,
    "minute": 30,
    "hour": 14,
    "day": 21,
    "dayofweek": 3
  }'
```

Should return:
```json
{
  "status": "success",
  "prediction": 74.5,
  "model_used": "XGBoost",
  "confidence": 0.85,
  "message": "Predicted next water percent: 74.5%"
}
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `model_loader_colab.py` | New loader for Colab models ⭐ |
| `scaler.pkl` | Data normalization (MinMaxScaler) |
| `xgboost.pkl` | XGBoost regression model |
| `random_forest.pkl` | Random Forest model |
| `linear_regression.pkl` | Linear Regression model |
| `lstm_model.h5` | LSTM neural network |
| `gru_model.h5` | GRU neural network |
| `best_model_name.txt` | Which model is best |
| `model_comparison_results.csv` | Performance metrics |

Delete these old files (they're fake):
- ❌ `create_model.py`
- ❌ `best_model.h5` (the dummy one)
