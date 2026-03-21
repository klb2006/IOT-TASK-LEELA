#!/usr/bin/env python3
"""
Quick Setup Script - Verify Activity Classification System
Run this to check if everything is configured correctly
"""

import os
import sys

def check_model_file():
    """Check if model32.h5 exists"""
    model_path = "backend/saved_models/model32.h5"
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✓ Model file found: {model_path} ({size_mb:.2f} MB)")
        return True
    else:
        print(f"✗ Model file MISSING: {model_path}")
        print("  → Download model32.h5 and place in backend/saved_models/")
        return False

def check_classifier_module():
    """Check if activity_classifier.py exists"""
    classifier_path = "backend/ml_training/activity_classifier.py"
    if os.path.exists(classifier_path):
        print(f"✓ Classifier module found: {classifier_path}")
        return True
    else:
        print(f"✗ Classifier module MISSING: {classifier_path}")
        print("  → Should be auto-created during setup")
        return False

def check_backend_main():
    """Check if main.py has activity prediction endpoint"""
    main_path = "backend/main.py"
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            content = f.read()
            if 'predict-activity' in content:
                print(f"✓ Backend has /api/v1/predict-activity endpoint")
                return True
            else:
                print(f"✗ Backend missing /api/v1/predict-activity endpoint")
                print("  → Run setup again")
                return False
    else:
        print(f"✗ Backend main.py not found: {main_path}")
        return False

def test_activity_classifier():
    """Try to load and test the classifier"""
    try:
        from ml_training.activity_classifier import predict_activity, get_activity_info
        
        # Get model info
        info = get_activity_info()
        if info['status'] == 'success':
            print(f"✓ Activity classifier module loaded successfully")
            print(f"  Model: {info['model'].get('model')}")
            print(f"  Accuracy: {info['model'].get('accuracy')}")
            print(f"  Activities: {', '.join(info['model'].get('activities', []))}")
            
            # Try a test prediction
            result = predict_activity(distance=50.0, temperature=28.0)
            if result['status'] == 'success':
                print(f"✓ Test prediction successful!")
                print(f"  Detected: {result['activity']}")
                print(f"  Confidence: {result['confidence']*100:.1f}%")
                return True
            else:
                print(f"✗ Test prediction failed: {result['message']}")
                return False
        else:
            print(f"✗ Activity classifier error: {info.get('message')}")
            return False
    except ImportError as e:
        print(f"✗ Cannot import activity_classifier: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Classifier test error: {str(e)}")
        return False

def print_setup_instructions():
    """Print setup instructions"""
    print("\n" + "="*70)
    print("ACTIVITY CLASSIFICATION SETUP")
    print("="*70)
    print("\nFOLLOW THESE STEPS:\n")
    
    print("1. COPY MODEL FILE")
    print("   Location: backend/saved_models/model32.h5")
    print("   Ensure the file is from your Google Colab training\n")
    
    print("2. RUN THIS SCRIPT TO VERIFY")
    print("   python verify_setup.py\n")
    
    print("3. START BACKEND SERVER")
    print("   python backend/main.py")
    print("   Output should show: [OK] API Server ready!\n")
    
    print("4. TEST ACTIVITY PREDICTION")
    print("   curl -X POST http://127.0.0.1:8000/api/v1/predict-activity \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"distance\": 50.0, \"temperature\": 28.0}'\n")
    
    print("5. UPLOAD ESP32 CODE")
    print("   - Update #define BACKEND_SERVER with your backend IP")
    print("   - Upload to ESP32")
    print("   - Check serial monitor for activity predictions\n")

def main():
    print("\n" + "="*70)
    print("SYSTEM CHECK - Activity Classification Setup")
    print("="*70 + "\n")
    
    checks = [
        ("Model File", check_model_file),
        ("Classifier Module", check_classifier_module),
        ("Backend Endpoint", check_backend_main),
        ("Classifier Test", test_activity_classifier)
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n[CHECK] {name}:")
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"✗ Check failed: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All checks passed! System is ready!")
        print("\nNext: Run 'python backend/main.py' to start the backend server")
    else:
        print("\n✗ Some checks failed. Follow the instructions above.")
        print_setup_instructions()
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
