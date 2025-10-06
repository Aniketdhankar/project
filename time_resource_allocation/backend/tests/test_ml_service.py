"""
Unit tests for ml_service module
"""

import pytest
import sys
from pathlib import Path
import numpy as np

# Add scripts directory to path
scripts_path = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_path))

from ml_service import MLService, get_ml_service


@pytest.fixture
def sample_employee():
    """Sample employee for testing"""
    return {
        'employee_id': 1,
        'name': 'Alice Johnson',
        'skills': 'Python,React,PostgreSQL,ML',
        'experience_years': 5.5,
        'current_workload': 20,
        'max_workload': 40,
        'availability_status': 'available',
        'performance_rating': 4.5
    }


@pytest.fixture
def sample_task():
    """Sample task for testing"""
    return {
        'task_id': 1,
        'title': 'Implement Authentication',
        'required_skills': 'Python,Flask,JWT',
        'priority': 'high',
        'estimated_hours': 20,
        'deadline': '2024-02-15',
        'complexity_score': 4.0
    }


class TestMLService:
    """Test cases for MLService"""
    
    def test_ml_service_initialization(self):
        """Test ML service initialization"""
        ml_service = MLService()
        assert ml_service is not None
        assert ml_service.feature_builder is not None
    
    def test_singleton_pattern(self):
        """Test that get_ml_service returns singleton"""
        service1 = get_ml_service()
        service2 = get_ml_service()
        assert service1 is service2
    
    def test_predict_proba_returns_valid_scores(self, sample_employee, sample_task):
        """Test that predict_proba returns valid scores"""
        ml_service = MLService()
        
        score, confidence = ml_service.predict_proba(
            sample_employee,
            sample_task,
            include_gemini=False
        )
        
        # Verify score and confidence are valid
        assert isinstance(score, float)
        assert isinstance(confidence, float)
        assert 0 <= score <= 1
        assert 0 <= confidence <= 1
    
    def test_predict_proba_with_gemini(self, sample_employee, sample_task):
        """Test predict_proba with Gemini features"""
        ml_service = MLService()
        
        # Should work even without Gemini API (uses fallback)
        score, confidence = ml_service.predict_proba(
            sample_employee,
            sample_task,
            include_gemini=True
        )
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_score_candidates(self, sample_task):
        """Test scoring multiple candidates"""
        ml_service = MLService()
        
        employees = [
            {
                'employee_id': 1,
                'name': 'Alice',
                'skills': 'Python,Flask,PostgreSQL',
                'experience_years': 5.0,
                'current_workload': 20,
                'max_workload': 40,
                'availability_status': 'available',
                'performance_rating': 4.5
            },
            {
                'employee_id': 2,
                'name': 'Bob',
                'skills': 'Python,Django,MySQL',
                'experience_years': 3.0,
                'current_workload': 15,
                'max_workload': 40,
                'availability_status': 'available',
                'performance_rating': 4.0
            }
        ]
        
        candidates = ml_service.score_candidates(
            sample_task,
            employees,
            top_k=2
        )
        
        # Verify candidates structure
        assert len(candidates) == 2
        
        for candidate in candidates:
            assert 'employee_id' in candidate
            assert 'task_id' in candidate
            assert 'employee_name' in candidate
            assert 'match_score' in candidate
            assert 'confidence' in candidate
            assert 'features' in candidate
            
            # Verify scores are valid
            assert 0 <= candidate['match_score'] <= 1
            assert 0 <= candidate['confidence'] <= 1
        
        # Verify candidates are sorted by score (descending)
        scores = [c['match_score'] for c in candidates]
        assert scores == sorted(scores, reverse=True)
    
    def test_score_candidates_top_k(self, sample_task):
        """Test that top_k limits results"""
        ml_service = MLService()
        
        employees = [
            {'employee_id': i, 'name': f'Employee{i}', 'skills': 'Python',
             'experience_years': 3.0, 'current_workload': 10, 'max_workload': 40,
             'availability_status': 'available', 'performance_rating': 4.0}
            for i in range(10)
        ]
        
        # Request top 3
        candidates = ml_service.score_candidates(sample_task, employees, top_k=3)
        
        assert len(candidates) == 3
    
    def test_extract_features(self, sample_employee, sample_task):
        """Test feature extraction"""
        ml_service = MLService()
        
        features = ml_service.extract_features(
            sample_employee,
            sample_task,
            include_gemini=False
        )
        
        # Verify features are numpy array
        assert isinstance(features, np.ndarray)
        assert len(features) > 0
        
        # All feature values should be finite
        assert np.all(np.isfinite(features))
    
    def test_get_feature_names(self):
        """Test getting feature names"""
        ml_service = MLService()
        
        # Without Gemini
        feature_names = ml_service.get_feature_names(include_gemini=False)
        assert isinstance(feature_names, list)
        assert len(feature_names) > 0
        
        # With Gemini
        feature_names_gemini = ml_service.get_feature_names(include_gemini=True)
        assert len(feature_names_gemini) > len(feature_names)
    
    def test_fallback_scoring(self, sample_employee, sample_task):
        """Test fallback scoring when ML model is not available"""
        ml_service = MLService()
        
        # Force use of fallback by ensuring no model is loaded
        ml_service.scoring_model = None
        
        score, confidence = ml_service.predict_proba(
            sample_employee,
            sample_task
        )
        
        # Should still return valid scores using fallback
        assert isinstance(score, float)
        assert isinstance(confidence, float)
        assert 0 <= score <= 1
        assert 0 <= confidence <= 1
        # Fallback should have lower confidence
        assert confidence < 1.0
    
    def test_skill_matching_in_scoring(self):
        """Test that skill matching contributes to scoring"""
        ml_service = MLService()
        ml_service.scoring_model = None  # Use fallback for predictable results
        
        task = {
            'task_id': 1,
            'title': 'Python Development',
            'required_skills': 'Python,Flask,PostgreSQL',
            'priority': 'high',
            'estimated_hours': 20,
            'complexity_score': 3.0
        }
        
        # Employee with matching skills
        employee_match = {
            'employee_id': 1,
            'name': 'Alice',
            'skills': 'Python,Flask,PostgreSQL,React',
            'experience_years': 5.0,
            'current_workload': 10,
            'max_workload': 40
        }
        
        # Employee with poor skill match
        employee_no_match = {
            'employee_id': 2,
            'name': 'Bob',
            'skills': 'Java,Spring,Oracle',
            'experience_years': 5.0,
            'current_workload': 10,
            'max_workload': 40
        }
        
        score_match, _ = ml_service.predict_proba(employee_match, task)
        score_no_match, _ = ml_service.predict_proba(employee_no_match, task)
        
        # Employee with matching skills should score higher
        assert score_match > score_no_match
    
    def test_workload_affects_scoring(self):
        """Test that workload affects scoring"""
        ml_service = MLService()
        ml_service.scoring_model = None  # Use fallback
        
        task = {
            'task_id': 1,
            'title': 'Python Development',
            'required_skills': 'Python',
            'priority': 'high',
            'estimated_hours': 10,
            'complexity_score': 3.0
        }
        
        # Employee with low workload
        employee_low_workload = {
            'employee_id': 1,
            'name': 'Alice',
            'skills': 'Python,Flask',
            'experience_years': 5.0,
            'current_workload': 5,
            'max_workload': 40
        }
        
        # Employee with high workload
        employee_high_workload = {
            'employee_id': 2,
            'name': 'Bob',
            'skills': 'Python,Flask',
            'experience_years': 5.0,
            'current_workload': 35,
            'max_workload': 40
        }
        
        score_low, _ = ml_service.predict_proba(employee_low_workload, task)
        score_high, _ = ml_service.predict_proba(employee_high_workload, task)
        
        # Employee with lower workload should score higher
        assert score_low > score_high
    
    def test_experience_complexity_match(self):
        """Test that experience matches complexity in scoring"""
        ml_service = MLService()
        ml_service.scoring_model = None  # Use fallback
        
        # Simple task
        simple_task = {
            'task_id': 1,
            'title': 'Simple Task',
            'required_skills': 'Python',
            'priority': 'low',
            'estimated_hours': 5,
            'complexity_score': 2.0
        }
        
        # Complex task
        complex_task = {
            'task_id': 2,
            'title': 'Complex Task',
            'required_skills': 'Python',
            'priority': 'high',
            'estimated_hours': 20,
            'complexity_score': 5.0
        }
        
        # Junior employee
        junior = {
            'employee_id': 1,
            'name': 'Junior',
            'skills': 'Python',
            'experience_years': 1.0,
            'current_workload': 10,
            'max_workload': 40
        }
        
        # Senior employee
        senior = {
            'employee_id': 2,
            'name': 'Senior',
            'skills': 'Python',
            'experience_years': 8.0,
            'current_workload': 10,
            'max_workload': 40
        }
        
        # Senior should score higher for complex task
        score_senior_complex, _ = ml_service.predict_proba(senior, complex_task)
        score_junior_complex, _ = ml_service.predict_proba(junior, complex_task)
        assert score_senior_complex > score_junior_complex
        
        # For simple task, junior should be competitive
        score_junior_simple, _ = ml_service.predict_proba(junior, simple_task)
        assert score_junior_simple > 0.5  # Should still get reasonable score
