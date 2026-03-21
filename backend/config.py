"""
Configuration for ML Model and Data Preprocessing
Easily adjust these values based on your actual sensor ranges
"""

# Feature ranges for MinMaxScaler normalization
# Adjust these based on your actual sensor data ranges
# If sensors read values outside these ranges, update them here
FEATURE_RANGES = {
    'distance': {
        'min': 5,      # Minimum expected distance in cm
        'max': 50,     # Maximum expected distance in cm
        'description': 'Ultrasonic sensor distance reading (cm)',
        'unit': 'cm'
    },
    'temperature': {
        'min': 15,     # Minimum temperature in °C
        'max': 40,     # Maximum temperature in °C
        'description': 'Ambient temperature reading',
        'unit': '°C'
    },
    'water_percent': {
        'min': 0,      # Minimum water percentage
        'max': 100,    # Maximum water percentage
        'description': 'Water tank fill percentage',
        'unit': '%'
    },
    'minute': {
        'min': 0,      # Minimum minute (0-59)
        'max': 59,
        'description': 'Minute of the hour (0-59)',
        'unit': 'min'
    },
    'hour': {
        'min': 0,      # Minimum hour (0-23)
        'max': 23,
        'description': 'Hour of the day (0-23)',
        'unit': 'hour'
    }
}

# ML Model Configuration
ML_MODEL_CONFIG = {
    'model_path': 'best_model.h5',
    'model_type': 'GRU',
    'input_features': 5,
    'input_timesteps': 1,
    'description': 'GRU Neural Network for water level prediction',
    'version': '1.0'
}

# Data Preprocessing Configuration
PREPROCESSING_CONFIG = {
    'scaler_type': 'MinMaxScaler',
    'feature_range': (0, 1),  # Normalize to 0-1 range
    'handle_out_of_range': 'clip',  # Options: 'clip', 'scale', 'error'
}

# How to handle values outside the defined ranges:
# 'clip': Force values to stay within min-max range
# 'scale': Allow scaler to extrapolate beyond range
# 'error': Raise an error if value is outside range

def get_feature_range(feature_name):
    """
    Get min-max range for a feature
    Usage: min_val, max_val = get_feature_range('distance')
    """
    if feature_name not in FEATURE_RANGES:
        raise ValueError(f"Unknown feature: {feature_name}")
    return (FEATURE_RANGES[feature_name]['min'], 
            FEATURE_RANGES[feature_name]['max'])

def get_all_feature_ranges_dict():
    """
    Get all features as a dict for MinMaxScaler
    Returns: {'distance': (5, 50), 'temperature': (15, 40), ...}
    """
    return {
        name: (config['min'], config['max']) 
        for name, config in FEATURE_RANGES.items()
    }

def print_feature_ranges():
    """Print all feature ranges in a readable format"""
    print("\n" + "="*60)
    print("ML MODEL FEATURE RANGES")
    print("="*60)
    for feature_name, config in FEATURE_RANGES.items():
        min_val = config['min']
        max_val = config['max']
        unit = config['unit']
        desc = config['description']
        print(f"\n{feature_name.upper()}")
        print(f"  Range: [{min_val}, {max_val}] {unit}")
        print(f"  Description: {desc}")
    print("\n" + "="*60)
    print("⚠️  If your sensors read values OUTSIDE these ranges,")
    print("   update the ranges in config.py and restart the server!")
    print("="*60 + "\n")

if __name__ == "__main__":
    print_feature_ranges()
