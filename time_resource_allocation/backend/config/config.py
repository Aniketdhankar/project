"""
Configuration Module
Centralized configuration for the application
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""
    
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:password@localhost:5432/time_resource_allocation'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # ML Models
    MODEL_DIR = Path(__file__).parent.parent.parent / 'ml_models' / 'trained'
    DATA_DIR = Path(__file__).parent.parent.parent / 'ml_models' / 'data'
    
    # Logging
    LOG_DIR = Path(__file__).parent.parent.parent / 'logs'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Task Assignment
    DEFAULT_ASSIGNMENT_METHOD = os.getenv('DEFAULT_ASSIGNMENT_METHOD', 'balanced')
    MAX_ASSIGNMENTS_PER_EMPLOYEE = int(os.getenv('MAX_ASSIGNMENTS_PER_EMPLOYEE', '5'))
    
    # Real-time Detection
    ANOMALY_DETECTION_INTERVAL = int(os.getenv('ANOMALY_DETECTION_INTERVAL', '300'))  # seconds
    DEADLINE_RISK_THRESHOLD = int(os.getenv('DEADLINE_RISK_THRESHOLD', '3'))  # days
    
    # WebSocket
    WEBSOCKET_PING_INTERVAL = 25
    WEBSOCKET_PING_TIMEOUT = 120
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '20'))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '100'))
    
    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Override with production values
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'postgresql://postgres:password@localhost:5432/time_resource_allocation_test'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None) -> Config:
    """
    Get configuration based on environment
    
    Args:
        env: Environment name (development, production, testing)
    
    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
