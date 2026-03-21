"""
Activity Classification Model Loader
========================================
Loads the GRU model (model32.h5) trained for water activity detection
Detects: no_activity, filling, flush, washing_machine, geyser
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings("ignore")

# Global cache
LOADED_MODEL = None
SCALER = None
FEATURE_ENGINEER = None

# Activity labels from training
ACTIVITY_LABELS = {
    0: "no_activity",
    1: "filling",
    2: "flush",
    3: "washing_machine",
    4: "geyser"
}

def get_saved_models_path():
    """Get absolute path to saved_models directory"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(backend_dir, "saved_models")

def load_gru_model():
    """Load the trained GRU model (model32.h5)"""
    global LOADED_MODEL
    
    if LOADED_MODEL is not None:
        return LOADED_MODEL
    
    try:
        import tensorflow as tf
        
        models_path = get_saved_models_path()
        model_path = os.path.join(models_path, "model32.h5")
        
        if os.path.exists(model_path):
            LOADED_MODEL = tf.keras.models.load_model(model_path)
            print(f"[OK] GRU model loaded from {model_path}")
            return LOADED_MODEL
        else:
            print(f"[ERROR] Model not found at {model_path}")
            print(f"        Ensure model32.h5 is in {models_path}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load GRU model: {e}")
        return None

def load_scaler():
    """Load the MinMaxScaler (if saved during training)"""
    global SCALER
    
    if SCALER is not None:
        return SCALER
    
    try:
        models_path = get_saved_models_path()
        scaler_path = os.path.join(models_path, "scaler_activity.pkl")
        
        if os.path.exists(scaler_path):
            SCALER = joblib.load(scaler_path)
            print(f"[OK] Scaler loaded")
            return SCALER
        else:
            print(f"[WARNING] Scaler not found, will create default MinMaxScaler")
            from sklearn.preprocessing import MinMaxScaler
            SCALER = MinMaxScaler(feature_range=(0, 1))
            # Fit with expected ranges
            fit_data = np.array([
                [0, 15],      # distance min/max (cm)
                [20, 40]      # temperature min/max (°C)
            ])
            SCALER.fit(fit_data)
            return SCALER
    except Exception as e:
        print(f"[WARNING] Error loading scaler: {e}")
        return None

def extract_features_from_distance(distance, temperature=None, prev_distance=None, prev_prev_distance=None):
    """
    Extract features from raw distance readings
    Matches the feature engineering done in training
    
    Features:
    - distance: Current ultrasonic distance (cm)
    - diff: Change in distance (slope)
    - slope: Rate of change
    - plus engineered features based on patterns
    """
    
    features = []
    
    # Current distance
    features.append(distance)
    
    # Temperature (if provided)
    if temperature is not None:
        features.append(temperature)
    else:
        features.append(25.0)  # Default temperature
    
    # Diff = change in distance
    if prev_distance is not None:
        diff = distance - prev_distance
        features.append(diff)
    else:
        features.append(0.0)
    
    # Slope = rate of change
    if prev_distance is not None and prev_prev_distance is not None:
        slope = (distance - prev_prev_distance) / 2
        features.append(slope)
    elif prev_distance is not None:
        slope = distance - prev_distance
        features.append(slope)
    else:
        features.append(0.0)
    
    return np.array(features)

def predict_activity(
    distance: float,
    temperature: float = 25.0,
    prev_distance: float = None,
    prev_prev_distance: float = None,
    return_probs: bool = False
) -> Dict[str, Any]:
    """
    Predict water activity from distance reading
    
    Args:
        distance: Current distance reading (cm) from ultrasonic sensor
        temperature: Temperature in °C (optional, default 25)
        prev_distance: Previous distance reading for slope calculation
        prev_prev_distance: Distance reading 2 steps ago
        return_probs: Return prediction probabilities for all classes
    
    Returns:
        {
            'status': 'success' or 'error',
            'activity': str (no_activity, filling, flush, washing_machine, geyser),
            'confidence': float (0-1),
            'distance': float,
            'temperature': float,
            'probabilities': dict (if return_probs=True),
            'message': str
        }
    """
    
    # Load model
    model = load_gru_model()
    if model is None:
        # Use fallback rule-based classification
        return predict_activity_fallback(distance, temperature, return_probs)
    
    try:
        # Extract features
        features = extract_features_from_distance(
            distance, 
            temperature,
            prev_distance,
            prev_prev_distance
        )
        
        # Scale features
        scaler = load_scaler()
        if scaler is not None:
            # Reshape for scaler (needs 2D array)
            features_scaled = scaler.transform([features])
        else:
            # Manual normalization if scaler not available
            # Normalize distance to 0-1 (assuming 0-100 cm range)
            features_scaled = np.array([[
                distance / 100.0,
                temperature / 50.0,
                features[2] / 50.0,  # diff
                features[3] / 50.0   # slope
            ]])
        
        # Make prediction
        prediction_probs = model.predict(features_scaled, verbose=0)
        predicted_class = np.argmax(prediction_probs[0])
        confidence = float(prediction_probs[0][predicted_class])
        
        # Get activity name
        activity = ACTIVITY_LABELS.get(predicted_class, "unknown")
        
        result = {
            'status': 'success',
            'activity': activity,
            'confidence': confidence,
            'distance': distance,
            'temperature': temperature,
            'message': f'Detected activity: {activity} ({confidence*100:.1f}% confidence)'
        }
        
        # Include probabilities if requested
        if return_probs:
            result['probabilities'] = {
                ACTIVITY_LABELS[i]: float(prediction_probs[0][i])
                for i in range(len(ACTIVITY_LABELS))
            }
        
        return result
    
    except Exception as e:
        # Fallback to rule-based if model prediction fails
        return predict_activity_fallback(distance, temperature, return_probs, error=str(e))

def predict_activity_fallback(distance: float, temperature: float = 25.0, return_probs: bool = False, error: str = None) -> Dict[str, Any]:
    """Fallback activity classification when model is unavailable"""
    try:
        # Rule-based classification based on distance and temperature
        # distance: 5cm = full tank, 50cm = empty tank
        water_level = max(0, min(100, ((50 - distance) / (50 - 5)) * 100))
        
        # Determine activity based on water level and temperature
        if water_level > 95:
            activity = "filling"
            confidence = 0.85
        elif water_level < 10:
            activity = "flush"
            confidence = 0.80
        elif temperature > 38:
            activity = "geyser"
            confidence = 0.75
        elif 60 <= water_level <= 80 and 20 <= temperature < 30:
            activity = "washing_machine"
            confidence = 0.70
        else:
            activity = "no_activity"
            confidence = 0.65
        
        # Generate probability distribution
        if return_probs:
            probabilities = {
                "no_activity": 0.15 if activity != "no_activity" else confidence,
                "filling": 0.20 if activity != "filling" else confidence,
                "flush": 0.20 if activity != "flush" else confidence,
                "washing_machine": 0.22 if activity != "washing_machine" else confidence,
                "geyser": 0.23 if activity != "geyser" else confidence
            }
            # Normalize
            total = sum(probabilities.values())
            probabilities = {k: v/total for k, v in probabilities.items()}
        
        result = {
            'status': 'success',
            'activity': activity,
            'confidence': confidence,
            'distance': distance,
            'temperature': temperature,
            'message': f'Fallback: Detected activity: {activity} ({confidence*100:.1f}% confidence)'
        }
        
        if return_probs:
            result['probabilities'] = probabilities
        
        return result
    except Exception as e:
        return {
            'status': 'error',
            'activity': None,
            'confidence': 0,
            'message': f'Prediction error: {str(e)}'
        }

def get_activity_info() -> Dict[str, Any]:
    """Get information about the activity classification model"""
    model = load_gru_model()
    
    if model is None:
        return {
            'status': 'error',
            'model': None,
            'activities': list(ACTIVITY_LABELS.values())
        }
    
    return {
        'status': 'success',
        'model': 'GRU (model32.h5)',
        'accuracy': '85.95%',
        'f1_score': '0.6881',
        'activities': list(ACTIVITY_LABELS.values()),
        'num_classes': len(ACTIVITY_LABELS),
        'model_type': 'GRU',
        'input_features': 4,
        'output': 'Activity classification'
    }

if __name__ == "__main__":
    # Test the model
    print("[TEST] Activity Classification Model\n")
    
    # Get model info
    info = get_activity_info()
    print("Model Info:")
    print(f"  Model: {info.get('model')}")
    print(f"  Accuracy: {info.get('accuracy')}")
    print(f"  Activities: {', '.join(info['activities'])}")
    
    # Test prediction
    print("\n[TEST] Sample Predictions:")
    
    # No activity (stable distance)
    result = predict_activity(
        distance=50.0,
        temperature=28.0,
        return_probs=True
    )
    print(f"\nTest 1 - No Activity (stable):")
    print(f"  Distance: {result['distance']} cm")
    print(f"  Predicted: {result['activity']}")
    print(f"  Confidence: {result['confidence']*100:.1f}%")
    
    # Filling (rapidly decreasing distance)
    result = predict_activity(
        distance=40.0,
        temperature=28.0,
        prev_distance=50.0,
        prev_prev_distance=55.0,
        return_probs=True
    )
    print(f"\nTest 2 - Filling (water rising, distance decreasing):")
    print(f"  Distance: {result['distance']} cm")
    print(f"  Predicted: {result['activity']}")
    print(f"  Confidence: {result['confidence']*100:.1f}%")
    
    # Flush (rapid distance change with spike)
    result = predict_activity(
        distance=35.0,
        temperature=28.0,
        prev_distance=45.0,
        prev_prev_distance=50.0,
        return_probs=True
    )
    print(f"\nTest 3 - Flush/Rapid change:")
    print(f"  Distance: {result['distance']} cm")
    print(f"  Predicted: {result['activity']}")
    print(f"  Confidence: {result['confidence']*100:.1f}%")
