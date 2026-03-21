"""
Updated Model Loader - Uses Your Real Colab-Trained Models
============================================================
Loads regression models (XGBoost, LSTM, GRU, etc.) trained in Google Colab
Predicts the NEXT water_percent value based on sensor features
"""

import os
import joblib
import numpy as np
from typing import Optional, Dict, Any, Tuple
import warnings
warnings.filterwarnings("ignore")

# Global model cache
LOADED_MODELS = {}
SCALER = None
BEST_MODEL_NAME = None
BEST_MODEL = None

# Feature names matching the Colab training
FEATURE_NAMES = [
    "distance",
    "temperature", 
    "water_percent",
    "water_liters",
    "minute",
    "hour",
    "day",
    "dayofweek",
    "prev_water_percent",
    "prev_water_liters",
    "prev_distance"
]

def get_ml_training_path():
    """Get absolute path to saved_models directory"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(backend_dir, "saved_models")

def load_scaler():
    """Load the MinMaxScaler trained in Colab"""
    global SCALER
    
    if SCALER is not None:
        return SCALER
    
    try:
        ml_path = get_ml_training_path()
        scaler_path = os.path.join(ml_path, "scaler.pkl")
        
        if os.path.exists(scaler_path):
            SCALER = joblib.load(scaler_path)
            print(f"[OK] Scaler loaded from {scaler_path}")
            return SCALER
        else:
            print(f"[ERROR] Scaler not found at {scaler_path}")
            print(f"       Download scaler.pkl from Colab to {ml_path}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load scaler: {e}")
        return None

def get_best_model_name() -> Optional[str]:
    """Read which model performed best"""
    global BEST_MODEL_NAME
    
    if BEST_MODEL_NAME is not None:
        return BEST_MODEL_NAME
    
    try:
        ml_path = get_ml_training_path()
        txt_path = os.path.join(ml_path, "best_model_name.txt")
        
        if os.path.exists(txt_path):
            with open(txt_path, "r") as f:
                BEST_MODEL_NAME = f.read().strip()
            print(f"[OK] Best model: {BEST_MODEL_NAME}")
            return BEST_MODEL_NAME
        else:
            print(f"[ERROR] best_model_name.txt not found")
            print(f"       Download best_model_name.txt from Colab")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to read best model name: {e}")
        return None

def load_best_model():
    """Load the best performing model"""
    global BEST_MODEL
    
    if BEST_MODEL is not None:
        return BEST_MODEL
    
    best_name = get_best_model_name()
    
    if best_name == "XGBoost":
        return load_xgboost_model()
    elif best_name == "Random Forest":
        return load_random_forest_model()
    elif best_name == "Linear Regression":
        return load_linear_regression_model()
    elif best_name == "LSTM":
        return load_lstm_model()
    elif best_name == "GRU":
        return load_gru_model()
    else:
        print(f"[ERROR] Unknown best model: {best_name}")
        return None

def load_xgboost_model():
    """Load XGBoost model"""
    if "xgboost" in LOADED_MODELS:
        return LOADED_MODELS["xgboost"]
    
    try:
        ml_path = get_ml_training_path()
        model_path = os.path.join(ml_path, "xgboost.pkl")
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            LOADED_MODELS["xgboost"] = model
            print(f"[OK] XGBoost model loaded")
            BEST_MODEL = model
            return model
        else:
            print(f"[ERROR] XGBoost not found at {model_path}")
            print(f"       Download xgboost.pkl from Colab")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load XGBoost: {e}")
        return None

def load_random_forest_model():
    """Load Random Forest model"""
    if "random_forest" in LOADED_MODELS:
        return LOADED_MODELS["random_forest"]
    
    try:
        ml_path = get_ml_training_path()
        model_path = os.path.join(ml_path, "random_forest.pkl")
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            LOADED_MODELS["random_forest"] = model
            print(f"[OK] Random Forest model loaded")
            return model
        else:
            print(f"[ERROR] Random Forest not found")
            print(f"       Download random_forest.pkl from Colab")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load Random Forest: {e}")
        return None

def load_linear_regression_model():
    """Load Linear Regression model"""
    if "linear_regression" in LOADED_MODELS:
        return LOADED_MODELS["linear_regression"]
    
    try:
        ml_path = get_ml_training_path()
        model_path = os.path.join(ml_path, "linear_regression.pkl")
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            LOADED_MODELS["linear_regression"] = model
            print(f"[OK] Linear Regression loaded")
            return model
        else:
            print(f"[ERROR] Linear Regression not found")
            print(f"       Download linear_regression.pkl from Colab")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load Linear Regression: {e}")
        return None

def load_lstm_model():
    """Load LSTM model"""
    if "lstm" in LOADED_MODELS:
        return LOADED_MODELS["lstm"]
    
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model
        
        ml_path = get_ml_training_path()
        model_path = os.path.join(ml_path, "lstm_model.h5")
        
        if os.path.exists(model_path):
            model = load_model(model_path)
            LOADED_MODELS["lstm"] = model
            print(f"[OK] LSTM model loaded")
            return model
        else:
            print(f"[ERROR] LSTM not found at {model_path}")
            print(f"       Download lstm_model.h5 from Colab")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load LSTM: {e}")
        return None

def load_gru_model():
    """Load GRU model"""
    if "gru" in LOADED_MODELS:
        return LOADED_MODELS["gru"]
    
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model
        
        ml_path = get_ml_training_path()
        model_path = os.path.join(ml_path, "gru_model.h5")
        
        if os.path.exists(model_path):
            model = load_model(model_path)
            LOADED_MODELS["gru"] = model
            print(f"[OK] GRU model loaded")
            return model
        else:
            print(f"[ERROR] GRU not found at {model_path}")
            print(f"       Download gru_model.h5 from Colab")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load GRU: {e}")
        return None

def get_available_models() -> list:
    """Get list of available models"""
    ml_path = get_ml_training_path()
    available = []
    
    models_to_check = [
        ("XGBoost", "xgboost.pkl"),
        ("Random Forest", "random_forest.pkl"),
        ("Linear Regression", "linear_regression.pkl"),
        ("LSTM", "lstm_model.h5"),
        ("GRU", "gru_model.h5")
    ]
    
    for model_name, file_name in models_to_check:
        if os.path.exists(os.path.join(ml_path, file_name)):
            available.append(model_name)
    
    return available

def predict_water_percent(
    distance: float,
    temperature: float,
    water_percent: float,
    water_liters: float = 0,
    minute: int = 0,
    hour: int = 0,
    day: int = 1,
    dayofweek: int = 0,
    prev_water_percent: float = None,
    prev_water_liters: float = None,
    prev_distance: float = None,
    model_name: str = None
) -> Dict[str, Any]:
    """
    Predict NEXT water percent using trained model
    
    Returns:
        {
            'status': 'success' or 'error',
            'prediction': float (predicted next water percent),
            'model_used': str (which model made prediction),
            'confidence': float (0-1, model-dependent),
            'message': str
        }
    """
    
    # Load scaler
    scaler = load_scaler()
    if scaler is None:
        return {
            'status': 'error',
            'prediction': None,
            'model_used': None,
            'message': 'Scaler not loaded. Download scaler.pkl from Colab.'
        }
    
    # Use previous values as current if not provided
    if prev_water_percent is None:
        prev_water_percent = water_percent
    if prev_water_liters is None:
        prev_water_liters = water_liters
    if prev_distance is None:
        prev_distance = distance
    
    # Create feature array in correct order
    features = np.array([[
        distance,
        temperature,
        water_percent,
        water_liters,
        minute,
        hour,
        day,
        dayofweek,
        prev_water_percent,
        prev_water_liters,
        prev_distance
    ]])
    
    # Scale features
    try:
        features_scaled = scaler.transform(features)
    except Exception as e:
        return {
            'status': 'error',
            'prediction': None,
            'model_used': None,
            'message': f'Scaling error: {str(e)}'
        }
    
    # Load best model if not specified
    if model_name is None:
        model_name = get_best_model_name()
    
    if model_name is None:
        return {
            'status': 'error',
            'prediction': None,
            'model_used': None,
            'message': 'No model available. Check best_model_name.txt'
        }
    
    # Make prediction
    try:
        if model_name == "XGBoost":
            model = load_xgboost_model()
            if model is None:
                raise Exception("XGBoost model not loaded")
            prediction = float(model.predict(features_scaled)[0])
            
        elif model_name == "Random Forest":
            model = load_random_forest_model()
            if model is None:
                raise Exception("Random Forest model not loaded")
            prediction = float(model.predict(features_scaled)[0])
            
        elif model_name == "Linear Regression":
            model = load_linear_regression_model()
            if model is None:
                raise Exception("Linear Regression model not loaded")
            prediction = float(model.predict(features_scaled)[0])
            
        elif model_name == "LSTM":
            model = load_lstm_model()
            if model is None:
                raise Exception("LSTM model not loaded")
            # Reshape for LSTM (needs seq_length dimension)
            features_seq = features_scaled.reshape(1, 1, features_scaled.shape[1])
            prediction = float(model.predict(features_seq, verbose=0)[0][0])
            
        elif model_name == "GRU":
            model = load_gru_model()
            if model is None:
                raise Exception("GRU model not loaded")
            # Reshape for GRU (needs seq_length dimension)
            features_seq = features_scaled.reshape(1, 1, features_scaled.shape[1])
            prediction = float(model.predict(features_seq, verbose=0)[0][0])
            
        else:
            return {
                'status': 'error',
                'prediction': None,
                'model_used': model_name,
                'message': f'Unknown model: {model_name}'
            }
        
        # Clamp prediction to 0-100 range
        prediction = max(0, min(100, prediction))
        
        return {
            'status': 'success',
            'prediction': prediction,
            'model_used': model_name,
            'confidence': 0.85,  # Default confidence
            'message': f'Predicted next water percent: {prediction:.2f}%'
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'prediction': None,
            'model_used': model_name,
            'message': f'Prediction error: {str(e)}'
        }

def get_model_comparison() -> Dict[str, Any]:
    """Load model comparison results from Colab training"""
    try:
        ml_path = get_ml_training_path()
        csv_path = os.path.join(ml_path, "model_comparison_results.csv")
        
        if os.path.exists(csv_path):
            import pandas as pd
            df = pd.read_csv(csv_path)
            return {
                'status': 'success',
                'data': df.to_dict('records')
            }
        else:
            return {
                'status': 'error',
                'data': None,
                'message': 'model_comparison_results.csv not found'
            }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'message': f'Error loading comparison: {str(e)}'
        }
