"""
Example Usage of ML Training Pipeline

This script demonstrates how to use the ML training pipeline
for the skill-based assignment model.
"""

import numpy as np
from train import SkillAssignmentTrainer
from evaluate import ModelEvaluator
from predict import PredictionLogger


def example_train():
    """Example: Train a new model"""
    print("=" * 60)
    print("Example 1: Training a Model")
    print("=" * 60)
    
    # Initialize trainer
    trainer = SkillAssignmentTrainer(model_dir='ml/models')
    
    # Train the model
    results = trainer.train_pipeline(
        database_connection=None,  # Uses sample data if None
        use_sample_data=True,
        test_size=0.2,
        perform_cv=True
    )
    
    print(f"\nTraining completed!")
    print(f"Accuracy: {results['metrics']['accuracy']:.4f}")
    print(f"ROC-AUC: {results['metrics']['roc_auc']:.4f}")
    print(f"Model saved to: {results['artifact_paths']['latest_model_path']}")
    
    return results


def example_evaluate():
    """Example: Evaluate a trained model"""
    print("\n" + "=" * 60)
    print("Example 2: Evaluating a Model")
    print("=" * 60)
    
    # Load and evaluate model
    evaluator = ModelEvaluator('ml/models/skill_assignment_model_latest.pkl')
    
    # Generate test data
    np.random.seed(42)
    X_test = np.random.rand(50, 17)
    y_test = np.random.randint(0, 2, 50)
    
    # Evaluate
    metrics = evaluator.evaluate(X_test, y_test)
    
    print(f"\nEvaluation completed!")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    
    # Save results
    evaluator.save_evaluation_results(metrics)
    
    return metrics


def example_predict():
    """Example: Make predictions"""
    print("\n" + "=" * 60)
    print("Example 3: Making Predictions")
    print("=" * 60)
    
    # Initialize predictor
    predictor = PredictionLogger('ml/models/skill_assignment_model_latest.pkl')
    
    # Generate sample data
    np.random.seed(42)
    X_new = np.random.rand(5, 17)
    
    # Make predictions
    result = predictor.predict_and_log(
        X_new,
        metadata={'source': 'example', 'version': '1.0'}
    )
    
    print(f"\nPredictions: {result['predictions']}")
    print(f"Confidence scores: {[f'{c:.4f}' for c in result['confidence']]}")
    
    return result


def example_top_k_assignments():
    """Example: Get top K assignment recommendations"""
    print("\n" + "=" * 60)
    print("Example 4: Top K Assignment Recommendations")
    print("=" * 60)
    
    predictor = PredictionLogger('ml/models/skill_assignment_model_latest.pkl')
    
    # Create sample employee-task pairs with features
    np.random.seed(42)
    n_pairs = 20
    employee_task_pairs = [
        {f'feature_{i}': np.random.rand() for i in range(17)}
        for _ in range(n_pairs)
    ]
    
    # Get top 5 recommendations
    recommendations = predictor.get_top_k_assignments(
        employee_task_pairs,
        k=5
    )
    
    print(f"\nTop 5 Assignment Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. Pair #{rec['pair_index']} - "
              f"Success Probability: {rec['success_probability']:.4f}, "
              f"Confidence: {rec['confidence']:.4f}")
    
    return recommendations


def example_full_workflow():
    """Example: Complete workflow from training to prediction"""
    print("\n" + "=" * 60)
    print("Complete ML Workflow Example")
    print("=" * 60)
    
    # Step 1: Train
    print("\nStep 1: Training model...")
    train_results = example_train()
    
    # Step 2: Evaluate
    print("\nStep 2: Evaluating model...")
    eval_metrics = example_evaluate()
    
    # Step 3: Predict
    print("\nStep 3: Making predictions...")
    predictions = example_predict()
    
    # Step 4: Get recommendations
    print("\nStep 4: Getting top assignments...")
    recommendations = example_top_k_assignments()
    
    print("\n" + "=" * 60)
    print("Workflow completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    # Run complete workflow
    try:
        example_full_workflow()
    except FileNotFoundError:
        # If model doesn't exist, just train first
        print("Model not found. Training a new model first...")
        example_train()
        print("\nNow you can run the other examples!")
