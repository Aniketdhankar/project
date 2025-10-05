"""
Gemini API Client
Handles all interactions with Google Gemini API including:
- Prompt management
- Response caching
- Retry logic
- Error handling
"""

import os
import time
import json
from typing import Dict, List, Optional, Any
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("No Gemini API key provided. Using mock responses.")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-pro"
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        # Cache for storing recent responses
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    def _get_cache_key(self, prompt: str, context: Dict) -> str:
        """Generate cache key from prompt and context"""
        return f"{hash(prompt)}_{hash(json.dumps(context, sort_keys=True))}"
    
    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check if response exists in cache"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_data['response']
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        return None
    
    def _store_cache(self, cache_key: str, response: str):
        """Store response in cache"""
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def _make_request(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Make actual API request to Gemini
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature (0-1)
        
        Returns:
            Generated text response
        """
        # TODO: Implement actual Gemini API call
        # For now, return mock response
        logger.info(f"Making Gemini API request (mock mode)")
        
        # Mock response based on prompt content
        if "triage" in prompt.lower():
            return self._mock_triage_response()
        elif "eta" in prompt.lower() or "deadline" in prompt.lower():
            return self._mock_eta_response()
        elif "anomaly" in prompt.lower():
            return self._mock_anomaly_response()
        else:
            return self._mock_general_response()
    
    def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict] = None,
        use_cache: bool = True,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response from Gemini API with retry logic
        
        Args:
            prompt: The prompt to send
            context: Additional context information
            use_cache: Whether to use cached responses
            temperature: Sampling temperature
        
        Returns:
            Generated text response
        """
        context = context or {}
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(prompt, context)
            cached_response = self._check_cache(cache_key)
            if cached_response:
                return cached_response
        
        # Try making request with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self._make_request(prompt, temperature)
                
                # Store in cache
                if use_cache:
                    self._store_cache(cache_key, response)
                
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        # All retries failed
        logger.error(f"All retries failed: {str(last_error)}")
        return self._fallback_response()
    
    def generate_triage_notes(self, anomaly_data: Dict) -> Dict[str, Any]:
        """
        Generate triage notes for an anomaly
        
        Args:
            anomaly_data: Dictionary containing anomaly information
        
        Returns:
            Dictionary with triage notes and recommended actions
        """
        prompt = f"""
        Analyze the following task anomaly and provide triage notes:
        
        Task: {anomaly_data.get('task_title', 'Unknown')}
        Anomaly Type: {anomaly_data.get('anomaly_type', 'Unknown')}
        Severity: {anomaly_data.get('severity', 'Unknown')}
        Description: {anomaly_data.get('description', 'No description')}
        
        Employee: {anomaly_data.get('employee_name', 'Unknown')}
        Current Workload: {anomaly_data.get('workload', 'Unknown')}
        Task Progress: {anomaly_data.get('progress', 0)}%
        
        Provide:
        1. Root cause analysis
        2. Impact assessment
        3. 3-5 specific recommended actions
        4. Priority level for resolution
        """
        
        response = self.generate_response(prompt, anomaly_data)
        
        # Parse response and extract structured data
        return {
            'triage_notes': response,
            'recommended_actions': self._extract_actions(response),
            'priority': self._extract_priority(response)
        }
    
    def predict_eta(self, task_data: Dict) -> Dict[str, Any]:
        """
        Predict ETA for a task using Gemini
        
        Args:
            task_data: Dictionary containing task information
        
        Returns:
            Dictionary with ETA prediction and explanation
        """
        prompt = f"""
        Predict the completion time for the following task:
        
        Task: {task_data.get('title', 'Unknown')}
        Description: {task_data.get('description', 'No description')}
        Required Skills: {task_data.get('required_skills', 'Not specified')}
        Complexity: {task_data.get('complexity', 'Medium')}
        Estimated Hours: {task_data.get('estimated_hours', 'Unknown')}
        
        Assigned To: {task_data.get('employee_name', 'Not assigned')}
        Employee Experience: {task_data.get('experience_years', 'Unknown')} years
        Current Workload: {task_data.get('current_workload', 'Unknown')} hours
        
        Historical Data:
        - Similar tasks average: {task_data.get('historical_avg', 'N/A')} hours
        - Employee average velocity: {task_data.get('velocity', 'N/A')} hours/task
        
        Provide:
        1. Predicted completion time in hours
        2. Confidence level (0-1)
        3. Key factors affecting the estimate
        4. Potential risks or delays
        """
        
        response = self.generate_response(prompt, task_data)
        
        return {
            'predicted_hours': self._extract_hours(response),
            'confidence': self._extract_confidence(response),
            'explanation': response,
            'factors': self._extract_factors(response)
        }
    
    def augment_features(self, task_data: Dict, employee_data: Dict) -> Dict[str, Any]:
        """
        Generate additional features for ML model
        
        Args:
            task_data: Task information
            employee_data: Employee information
        
        Returns:
            Dictionary with augmented features
        """
        prompt = f"""
        Analyze the match between this task and employee:
        
        Task: {task_data.get('title')}
        Required Skills: {task_data.get('required_skills')}
        Priority: {task_data.get('priority')}
        
        Employee: {employee_data.get('name')}
        Skills: {employee_data.get('skills')}
        Experience: {employee_data.get('experience_years')} years
        
        Provide numerical scores (0-1) for:
        1. Skill match quality
        2. Experience relevance
        3. Task complexity fit
        4. Potential for success
        """
        
        response = self.generate_response(prompt, {'task': task_data, 'employee': employee_data})
        
        return {
            'skill_match_quality': self._extract_score(response, 'skill'),
            'experience_relevance': self._extract_score(response, 'experience'),
            'complexity_fit': self._extract_score(response, 'complexity'),
            'success_potential': self._extract_score(response, 'success')
        }
    
    # Helper methods for parsing responses
    
    def _extract_actions(self, response: str) -> List[str]:
        """Extract action items from response"""
        # TODO: Implement actual parsing logic
        return [
            "Review task requirements and clarify ambiguities",
            "Reassign or redistribute workload if necessary",
            "Schedule check-in meeting with stakeholders"
        ]
    
    def _extract_priority(self, response: str) -> str:
        """Extract priority level from response"""
        # TODO: Implement actual parsing logic
        if "critical" in response.lower() or "urgent" in response.lower():
            return "high"
        elif "low" in response.lower():
            return "low"
        return "medium"
    
    def _extract_hours(self, response: str) -> float:
        """Extract predicted hours from response"""
        # TODO: Implement actual parsing logic
        return 16.5
    
    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from response"""
        # TODO: Implement actual parsing logic
        return 0.75
    
    def _extract_factors(self, response: str) -> List[str]:
        """Extract key factors from response"""
        # TODO: Implement actual parsing logic
        return [
            "Task complexity",
            "Employee experience",
            "Current workload",
            "Historical performance"
        ]
    
    def _extract_score(self, response: str, score_type: str) -> float:
        """Extract numerical score from response"""
        # TODO: Implement actual parsing logic
        return 0.75
    
    # Mock response methods (for development)
    
    def _mock_triage_response(self) -> str:
        return """
        Root Cause Analysis:
        The task is experiencing delays due to increased complexity and unclear requirements.
        
        Impact Assessment:
        - Project deadline at risk
        - Team morale may be affected
        - Downstream dependencies blocked
        
        Recommended Actions:
        1. Schedule requirements clarification meeting with stakeholders
        2. Consider breaking task into smaller subtasks
        3. Assign additional resource for pair programming
        4. Update project timeline and notify affected teams
        5. Implement daily standup for this specific task
        
        Priority: High - Requires immediate attention
        """
    
    def _mock_eta_response(self) -> str:
        return """
        Predicted Completion Time: 18.5 hours
        
        Confidence Level: 0.78 (High)
        
        Key Factors:
        1. Task complexity is above average for this employee
        2. Current workload is at 85% capacity
        3. Similar tasks historically took 16-20 hours
        4. Employee has strong relevant experience
        
        Potential Risks:
        - Dependencies on external APIs may cause delays
        - Testing phase may require additional time
        - Code review process typically adds 2-3 hours
        """
    
    def _mock_anomaly_response(self) -> str:
        return """
        Anomaly detected in task progress pattern.
        
        Analysis:
        The task is showing slower progress than expected based on historical data.
        Current velocity is 60% of normal pace.
        
        Possible Causes:
        1. Unexpected technical challenges
        2. Insufficient requirements documentation
        3. Resource constraints or competing priorities
        
        Recommendations:
        1. Conduct technical review session
        2. Verify all dependencies are resolved
        3. Consider pair programming or mentorship
        """
    
    def _mock_general_response(self) -> str:
        return """
        Analysis complete. Based on the provided information, the system has
        identified several key factors that should be considered. Detailed
        recommendations and insights have been generated to support decision-making.
        """
    
    def _fallback_response(self) -> str:
        """Return fallback response when API fails"""
        return "Unable to generate AI response at this time. Please try again later or use manual analysis."


# Singleton instance
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Get or create singleton Gemini client instance"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
