"""
Skill Matching Module
Handles skill parsing, embedding generation, and similarity calculation
"""

import numpy as np
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillMatcher:
    """Handles skill matching and similarity calculation"""
    
    def __init__(self):
        """Initialize skill matcher with vectorizer"""
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            analyzer='word',
            ngram_range=(1, 2),
            max_features=1000
        )
        self.is_fitted = False
        
        # Skill synonyms for better matching
        self.skill_synonyms = {
            'ml': ['machine learning', 'ml', 'ai'],
            'frontend': ['frontend', 'front-end', 'ui', 'user interface'],
            'backend': ['backend', 'back-end', 'server-side'],
            'database': ['database', 'db', 'sql', 'postgresql', 'mysql'],
            'api': ['api', 'rest', 'restful', 'web service'],
        }
    
    def parse_skills(self, skill_string: str) -> List[str]:
        """
        Parse skill string into list of individual skills
        
        Args:
            skill_string: Comma-separated or space-separated skills
        
        Returns:
            List of cleaned skill strings
        """
        if not skill_string:
            return []
        
        # Split by comma or semicolon
        skills = skill_string.replace(';', ',').split(',')
        
        # Clean and normalize
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip().lower()
            if skill:
                cleaned_skills.append(skill)
        
        return cleaned_skills
    
    def expand_skills(self, skills: List[str]) -> List[str]:
        """
        Expand skills with synonyms for better matching
        
        Args:
            skills: List of skill strings
        
        Returns:
            Expanded list including synonyms
        """
        expanded = set(skills)
        
        for skill in skills:
            skill_lower = skill.lower()
            for key, synonyms in self.skill_synonyms.items():
                if skill_lower in synonyms:
                    expanded.update(synonyms)
        
        return list(expanded)
    
    def generate_embedding(self, skill_string: str) -> np.ndarray:
        """
        Generate embedding vector for skill string
        
        Args:
            skill_string: Raw skill string
        
        Returns:
            Embedding vector as numpy array
        """
        skills = self.parse_skills(skill_string)
        expanded_skills = self.expand_skills(skills)
        
        # Join skills into a single text
        text = ' '.join(expanded_skills)
        
        if not self.is_fitted:
            logger.warning("Vectorizer not fitted. Using basic embedding.")
            # Return a basic hash-based embedding
            return self._basic_embedding(text)
        
        # Generate TF-IDF embedding
        embedding = self.vectorizer.transform([text]).toarray()[0]
        return embedding
    
    def fit_vectorizer(self, skill_corpus: List[str]):
        """
        Fit vectorizer on corpus of skill strings
        
        Args:
            skill_corpus: List of skill strings for training
        """
        logger.info(f"Fitting vectorizer on {len(skill_corpus)} skill strings")
        
        # Parse and expand all skills
        processed_corpus = []
        for skill_string in skill_corpus:
            skills = self.parse_skills(skill_string)
            expanded = self.expand_skills(skills)
            processed_corpus.append(' '.join(expanded))
        
        self.vectorizer.fit(processed_corpus)
        self.is_fitted = True
        logger.info("Vectorizer fitted successfully")
    
    def calculate_similarity(
        self, 
        employee_skills: str, 
        task_skills: str
    ) -> float:
        """
        Calculate similarity between employee skills and task requirements
        
        Args:
            employee_skills: Employee's skill string
            task_skills: Task's required skill string
        
        Returns:
            Similarity score (0-1)
        """
        # Generate embeddings
        employee_embedding = self.generate_embedding(employee_skills)
        task_embedding = self.generate_embedding(task_skills)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            employee_embedding.reshape(1, -1),
            task_embedding.reshape(1, -1)
        )[0][0]
        
        # Ensure score is between 0 and 1
        similarity = max(0.0, min(1.0, similarity))
        
        return similarity
    
    def batch_calculate_similarity(
        self,
        employee_skills_list: List[str],
        task_skills: str
    ) -> List[float]:
        """
        Calculate similarity for multiple employees against one task
        
        Args:
            employee_skills_list: List of employee skill strings
            task_skills: Task's required skill string
        
        Returns:
            List of similarity scores
        """
        task_embedding = self.generate_embedding(task_skills)
        
        similarities = []
        for employee_skills in employee_skills_list:
            employee_embedding = self.generate_embedding(employee_skills)
            similarity = cosine_similarity(
                employee_embedding.reshape(1, -1),
                task_embedding.reshape(1, -1)
            )[0][0]
            similarities.append(max(0.0, min(1.0, similarity)))
        
        return similarities
    
    def match_employees_to_task(
        self,
        employees: List[Dict],
        task: Dict,
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find best matching employees for a task
        
        Args:
            employees: List of employee dictionaries with 'employee_id' and 'skills'
            task: Task dictionary with 'required_skills'
            top_k: Number of top matches to return
        
        Returns:
            List of (employee_id, similarity_score) tuples, sorted by score
        """
        task_skills = task.get('required_skills', '')
        
        matches = []
        for employee in employees:
            employee_id = employee.get('employee_id')
            employee_skills = employee.get('skills', '')
            
            similarity = self.calculate_similarity(employee_skills, task_skills)
            matches.append((employee_id, similarity))
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k matches
        return matches[:top_k]
    
    def get_skill_overlap(
        self,
        employee_skills: str,
        task_skills: str
    ) -> Dict[str, any]:
        """
        Get detailed skill overlap analysis
        
        Args:
            employee_skills: Employee's skill string
            task_skills: Task's required skill string
        
        Returns:
            Dictionary with overlap details
        """
        emp_skills = set(self.parse_skills(employee_skills))
        req_skills = set(self.parse_skills(task_skills))
        
        overlap = emp_skills.intersection(req_skills)
        missing = req_skills - emp_skills
        extra = emp_skills - req_skills
        
        overlap_ratio = len(overlap) / len(req_skills) if req_skills else 0
        
        return {
            'matching_skills': list(overlap),
            'missing_skills': list(missing),
            'extra_skills': list(extra),
            'overlap_ratio': overlap_ratio,
            'total_required': len(req_skills),
            'total_employee': len(emp_skills)
        }
    
    def _basic_embedding(self, text: str) -> np.ndarray:
        """
        Generate basic embedding when vectorizer not fitted
        
        Args:
            text: Text to embed
        
        Returns:
            Basic embedding vector
        """
        # Simple character-based hash embedding
        embedding = np.zeros(100)
        for i, char in enumerate(text[:100]):
            embedding[i] = ord(char) / 255.0
        return embedding


# Singleton instance
_skill_matcher = None

def get_skill_matcher() -> SkillMatcher:
    """Get or create singleton SkillMatcher instance"""
    global _skill_matcher
    if _skill_matcher is None:
        _skill_matcher = SkillMatcher()
    return _skill_matcher


# Example usage functions

def initialize_skill_matcher(database_connection):
    """
    Initialize skill matcher with data from database
    
    Args:
        database_connection: Database connection object
    """
    # TODO: Fetch all skill strings from database
    # Example:
    # cursor = database_connection.cursor()
    # cursor.execute("SELECT skills FROM Employees UNION SELECT required_skills FROM Tasks")
    # skill_corpus = [row[0] for row in cursor.fetchall()]
    
    # For now, use sample data
    skill_corpus = [
        "Python, React, PostgreSQL, ML",
        "Python, Flask, PostgreSQL, API",
        "React, JavaScript, CSS, Chart.js",
        "Python, TensorFlow, LightGBM, ML",
        "Python, React, PostgreSQL, Docker"
    ]
    
    matcher = get_skill_matcher()
    matcher.fit_vectorizer(skill_corpus)
    logger.info("Skill matcher initialized successfully")


def find_candidates_for_task(task_id: int, database_connection) -> List[Dict]:
    """
    Find candidate employees for a task
    
    Args:
        task_id: ID of the task
        database_connection: Database connection object
    
    Returns:
        List of candidate dictionaries with scores
    """
    # TODO: Implement database queries
    # Example implementation:
    
    matcher = get_skill_matcher()
    
    # Fetch task details
    # task = fetch_task(task_id, database_connection)
    task = {
        'task_id': task_id,
        'required_skills': 'Python, Flask, PostgreSQL'
    }
    
    # Fetch available employees
    # employees = fetch_available_employees(database_connection)
    employees = [
        {'employee_id': 1, 'name': 'Alice', 'skills': 'Python, React, PostgreSQL, ML'},
        {'employee_id': 2, 'name': 'Bob', 'skills': 'Python, Flask, PostgreSQL, API'},
        {'employee_id': 3, 'name': 'Carol', 'skills': 'React, JavaScript, CSS'},
    ]
    
    # Calculate matches
    matches = matcher.match_employees_to_task(employees, task, top_k=5)
    
    # Build result list
    candidates = []
    for employee_id, score in matches:
        employee = next(e for e in employees if e['employee_id'] == employee_id)
        
        overlap = matcher.get_skill_overlap(
            employee['skills'],
            task['required_skills']
        )
        
        candidates.append({
            'employee_id': employee_id,
            'name': employee['name'],
            'skill_match_score': score,
            'matching_skills': overlap['matching_skills'],
            'missing_skills': overlap['missing_skills']
        })
    
    return candidates
