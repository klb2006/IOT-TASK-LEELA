"""
ML Model Loader - XGBoost Version
==================================
Loads trained ML models and scalers from Colab training output
Supports: XGBoost (best), LSTM, GRU, Random Forest, Linear Regression
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


def get_ml_training_path():
    """Get absolute path to ml_training directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir


def load_scaler():
    """Load and cache the data scaler"""
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
            print(f"[WARNING] Scaler not found at {scaler_path}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load scaler: {e}")
        return None


def get_best_model_name():
    """Read which model performed best from best_model_name.txt"""
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
            # Default to XGBoost if file doesn't exist
            print(f"[WARNING] best_model_name.txt not found, defaulting to XGBoost")
            BEST_MODEL_NAME = "XGBoost"
            return BEST_MODEL_NAME
    except Exception as e:
        print(f"[ERROR] Failed to read best model name: {e}")
        return "XGBoost"


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
            return model
        else:
            print(f"[WARNING] XGBoost model not found at {model_path}")
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
            print(f"[WARNING] Random Forest model not found")
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
            print(f"[OK] Linear Regression model loaded")
            return model
        else:
            print(f"[WARNING] Linear Regression model not found")
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
            model = load_model(model_path, safe_mode=False)
            LOADED_MODELS["lstm"] = model
            print(f"[OK] LSTM model loaded")
            return model
        else:
            print(f"[WARNING] LSTM model not found")
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
            model = load_model(model_path, safe_mode=False)
            LOADED_MODELS["gru"] = model
            print(f"[OK] GRU model loaded")
            return model
        else:
            print(f"[WARNING] GRU model not found")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load GRU: {e}")
        return None


def load_best_model():
    """Load the best performing model (XGBoost by default)"""
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
        # Default to XGBoost
        return load_xgboost_model()


def preprocess_input(distance: float, temperature: float, water_percent: float, 
                     minute: int, hour: int) -> np.ndarray:
    """
    Preprocess input using the trained scaler
    Returns shape (1, 5) - ready for prediction
    """
    scaler = load_scaler()
    if scaler is None:
        print("[WARNING] Scaler not available, using raw values")
        return np.array([[distance, temperature, water_percent, minute, hour]])
    
    try:
        raw_input = np.array([[distance, temperature, water_percent, minute, hour]])
        scaled_input = scaler.transform(raw_input)
        return scaled_input
    except Exception as e:
        print(f"[WARNING] Preprocessing failed: {e}, using raw values")
        return np.array([[distance, temperature, water_percent, minute, hour]])


def predict_water_percent(distance: float, temperature: float, water_percent: float,
                         minute: int, hour: int, model_name: str = None) -> Dict[str, Any]:
    """
    Make a prediction using the specified model or best model
    
    Args:
        distance: Distance sensor reading (cm)
        temperature: Temperature reading (°C)
        water_percent: Current water percentage
        minute: Current minute (0-59)
        hour: Current hour (0-23)
        model_name: Optional model name (XGBoost, Random Forest, etc.)
    
    Returns:
        Dict with prediction result and metadata
    """
    try:
        # Choose model
        if model_name is None:
            model_name = get_best_model_name()
        
        if model_name == "XGBoost":
            model = load_xgboost_model()
        elif model_name == "Random Forest":
            model = load_random_forest_model()
        elif model_name == "Linear Regression":
            model = load_linear_regression_model()
        elif model_name == "LSTM":
            model = load_lstm_model()
        elif model_name == "GRU":
            model = load_gru_model()
        else:
            model = load_best_model()
        
        if model is None:
            return {
                "status": "error",
                "message": f"Model {model_name} not available",
                "model_used": model_name
            }
        
        # Preprocess input
        X_scaled = preprocess_input(distance, temperature, water_percent, minute, hour)
        
        # Make prediction
        if model_name in ["LSTM", "GRU"]:
            # Neural network models need sequence (samples, timesteps, features)
            X_model = X_scaled.reshape((1, 1, 5))
            prediction = model.predict(X_model, verbose=0)
            predicted_value = float(prediction[0][0])
        else:
            # Traditional ML models
            prediction = model.predict(X_scaled)
            predicted_value = float(prediction[0])
        
        return {
            "status": "success",
            "predicted_water_percent": predicted_value,
            "model_used": model_name,
            "input": {
                "distance": distance,
                "temperature": temperature,
                "water_percent": water_percent,
                "minute": minute,
                "hour": hour
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "model_used": model_name
        }


def get_model_comparison() -> Dict[str, Any]:
    """Load and return model comparison results"""
    try:
        ml_path = get_ml_training_path()
        csv_path = os.path.join(ml_path, "model_comparison_results.csv")
        
        if os.path.exists(csv_path):
            import pandas as pd
            df = pd.read_csv(csv_path)
            return {
                "status": "success",
                "models": df.to_dict(orient="records")
            }
        else:
            return {"status": "error", "message": "Comparison file not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_available_models() -> Dict[str, bool]:
    """Check which models are available"""
    ml_path = get_ml_training_path()
    
    return {
        "xgboost": os.path.exists(os.path.join(ml_path, "xgboost.pkl")),
        "random_forest": os.path.exists(os.path.join(ml_path, "random_forest.pkl")),
        "linear_regression": os.path.exists(os.path.join(ml_path, "linear_regression.pkl")),
        "lstm": os.path.exists(os.path.join(ml_path, "lstm_model.h5")),
        "gru": os.path.exists(os.path.join(ml_path, "gru_model.h5")),
        "scaler": os.path.exists(os.path.join(ml_path, "scaler.pkl"))
    }


# Initialize on import
if __name__ == "__main__":
    print("\n" + "="*60)
    print("ML Model Loader Test")
    print("="*60)
    
    print("\nAvailable models:")
    available = get_available_models()
    for model, available_flag in available.items():
        status = "✓" if available_flag else "✗"
        print(f"  {status} {model}")
    
    print(f"\nBest model: {get_best_model_name()}")
    
    print("\nModel comparison:")
    comparison = get_model_comparison()
    if comparison["status"] == "success":
        import pandas as pd
        df = pd.DataFrame(comparison["models"])
        print(df)
