"""
Configuration module for MindCare API
Loads settings from environment variables with defaults
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DB_PATH = os.getenv('DB_PATH', 'mental_health.db')
    DB_TIMEOUT = int(os.getenv('DB_TIMEOUT', 30))
    
    # Model
    MODEL_PATH = os.getenv('MODEL_PATH', 'model.pkl')
    SCALER_PATH = os.getenv('SCALER_PATH', 'scaler.pkl')
    DATASET_PATH = os.getenv('DATASET_PATH', 'stress_dataset.csv')
    
    # API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Input limits
    MIN_SLEEP = float(os.getenv('MIN_SLEEP', 0))
    MAX_SLEEP = float(os.getenv('MAX_SLEEP', 24))
    MIN_SCREEN_TIME = float(os.getenv('MIN_SCREEN_TIME', 0))
    MAX_SCREEN_TIME = float(os.getenv('MAX_SCREEN_TIME', 24))
    MIN_WORKLOAD = float(os.getenv('MIN_WORKLOAD', 0))
    MAX_WORKLOAD = float(os.getenv('MAX_WORKLOAD', 24))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', 500))
    
    # Training
    RANDOM_STATE = int(os.getenv('RANDOM_STATE', 42))
    TEST_SIZE = float(os.getenv('TEST_SIZE', 0.2))
    CROSS_VAL_FOLDS = int(os.getenv('CROSS_VAL_FOLDS', 5))
    TRAINING_SAMPLES = int(os.getenv('TRAINING_SAMPLES', 200))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DB_PATH = ':memory:'  # Use in-memory database for tests


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration object"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, config_by_name['default'])
