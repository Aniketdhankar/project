"""
Integration Test for ML Training Pipeline

This script tests the integration of the ML training pipeline
with the existing time_resource_allocation backend code.
"""

import os
import sys
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'time_resource_allocation', 'backend'))

from train import SkillAssignmentTrainer


def test_feature_compatibility():
    """Test that feature builder integration works"""
    print("Testing feature compatibility...")
    
    trainer = SkillAssignmentTrainer()
    
    # Check if feature builder is accessible
    if trainer.feature_builder:
        print("✓ Feature builder loaded successfully")
        
        # Get feature names
        feature_names = trainer.feature_builder.get_feature_names(include_gemini=False)
        print(f"✓ Feature names available: {len(feature_names)} features")
        
        expected_features = [
            'employee_experience', 'employee_workload_ratio', 'employee_availability',
            'task_priority', 'task_complexity', 'skill_match_score'
        ]
        
        for feat in expected_features:
            if feat in feature_names:
                print(f"  ✓ {feat}")
            else:
                print(f"  ✗ {feat} missing")
        
        return True
    else:
        print("⚠ Feature builder not available (expected for standalone tests)")
        return False


def test_training_pipeline():
    """Test the complete training pipeline"""
    print("\nTesting training pipeline...")
    
    trainer = SkillAssignmentTrainer()
    
    # Run training with sample data
    results = trainer.train_pipeline(
        database_connection=None,
        use_sample_data=True,
        test_size=0.2,
        perform_cv=True
    )
    
    # Verify results structure
    assert 'metrics' in results, "Missing metrics in results"
    assert 'artifact_paths' in results, "Missing artifact_paths in results"
    
    # Verify metrics
    metrics = results['metrics']
    required_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
    
    for metric in required_metrics:
        assert metric in metrics, f"Missing {metric} in results"
        assert 0 <= metrics[metric] <= 1, f"{metric} out of valid range"
        print(f"  ✓ {metric}: {metrics[metric]:.4f}")
    
    # Verify artifacts were saved
    artifact_paths = results['artifact_paths']
    for key, path in artifact_paths.items():
        if os.path.exists(path):
            print(f"  ✓ {key}: {path}")
        else:
            print(f"  ✗ {key} not saved: {path}")
    
    print("✓ Training pipeline test passed")
    return True


def test_model_loading():
    """Test that saved models can be loaded"""
    print("\nTesting model loading...")
    
    import joblib
    
    model_path = 'ml/models/skill_assignment_model_latest.pkl'
    
    if os.path.exists(model_path):
        try:
            pipeline = joblib.load(model_path)
            print(f"✓ Model loaded successfully from {model_path}")
            
            # Test prediction
            X_test = np.random.rand(5, 17)
            predictions = pipeline.predict(X_test)
            probabilities = pipeline.predict_proba(X_test)
            
            print(f"✓ Made predictions: {predictions}")
            print(f"✓ Got probabilities with shape: {probabilities.shape}")
            
            return True
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False
    else:
        print(f"⚠ Model not found at {model_path}")
        return False


def test_data_extraction():
    """Test data extraction methods"""
    print("\nTesting data extraction...")
    
    trainer = SkillAssignmentTrainer()
    
    # Test sample data generation
    X, y = trainer.extract_training_data(use_sample_data=True)
    
    assert isinstance(X, pd.DataFrame), "X should be a DataFrame"
    assert isinstance(y, pd.Series), "y should be a Series"
    assert len(X) == len(y), "X and y should have same length"
    assert X.shape[1] == 17, "Should have 17 features"
    
    print(f"✓ Extracted {len(X)} samples with {X.shape[1]} features")
    print(f"✓ Label distribution: {y.value_counts().to_dict()}")
    
    return True


def test_preprocessing():
    """Test feature preprocessing"""
    print("\nTesting preprocessing...")
    
    trainer = SkillAssignmentTrainer()
    
    # Generate sample data
    X = pd.DataFrame(np.random.rand(100, 17))
    X_train, X_test = X[:80], X[80:]
    
    # Add some missing values
    X_train.iloc[0, 0] = np.nan
    X_test.iloc[0, 0] = np.nan
    
    # Preprocess
    X_train_processed, X_test_processed = trainer.preprocess_features(X_train, X_test)
    
    assert not np.isnan(X_train_processed).any(), "Training data should have no NaN"
    assert not np.isnan(X_test_processed).any(), "Test data should have no NaN"
    
    # Check scaling (mean ~0, std ~1)
    mean = np.mean(X_train_processed, axis=0)
    std = np.std(X_train_processed, axis=0)
    
    assert np.allclose(mean, 0, atol=0.1), "Mean should be close to 0"
    assert np.allclose(std, 1, atol=0.2), "Std should be close to 1"
    
    print(f"✓ Preprocessing working correctly")
    print(f"  ✓ No missing values")
    print(f"  ✓ Data scaled properly (mean≈0, std≈1)")
    
    return True


def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("ML Training Pipeline Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Feature Compatibility", test_feature_compatibility),
        ("Data Extraction", test_data_extraction),
        ("Preprocessing", test_preprocessing),
        ("Training Pipeline", test_training_pipeline),
        ("Model Loading", test_model_loading),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("=" * 60)
    
    return all(results.values())


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
