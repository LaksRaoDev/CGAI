"""
Configuration settings for Content Generation AI
File: backend/config.py
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # App Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'content-ai-dev-key-2024'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:root@localhost/content_ai_db?charset=utf8mb4'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Model Configuration
    MODEL_CACHE_DIR = os.environ.get('MODEL_CACHE_DIR') or './data/models'
    DEFAULT_MODEL = 'gpt2'  # Free Hugging Face model
    MAX_TOKENS = 512
    TEMPERATURE = 0.7
    
    # API Configuration
    API_PREFIX = '/api/v1'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:5000', 'http://localhost:5000', 'http://127.0.0.1:5500', 'http://localhost:5500', 'file://', '*']
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    
    # Content Generation Settings
    CONTENT_TYPES = {
        'product': {
            'max_length': 300,
            'min_length': 50,
            'temperature': 0.7
        },
        'social': {
            'max_length': 280,  # Twitter limit
            'min_length': 10,
            'temperature': 0.8
        },
        'blog': {
            'max_length': 2000,
            'min_length': 100,
            'temperature': 0.6
        },
        'marketing': {
            'max_length': 1000,
            'min_length': 50,
            'temperature': 0.8
        }
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/content_ai_db?charset=utf8mb4'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:root@localhost/content_ai_db?charset=utf8mb4'
    
    # Production AI model settings
    DEFAULT_MODEL = 'microsoft/DialoGPT-medium'
    MAX_TOKENS = 1024

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/test_content_ai_db?charset=utf8mb4'
    DEBUG = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Model configurations for different content types
MODEL_CONFIGS = {
    'product_description': {
        'model_name': 'gpt2',
        'max_length': 200,
        'temperature': 0.7,
        'top_p': 0.9,
        'repetition_penalty': 1.1
    },
    'social_media': {
        'model_name': 'gpt2',
        'max_length': 100,
        'temperature': 0.8,
        'top_p': 0.95,
        'repetition_penalty': 1.05
    },
    'blog_content': {
        'model_name': 'gpt2',
        'max_length': 500,
        'temperature': 0.6,
        'top_p': 0.9,
        'repetition_penalty': 1.2
    },
    'marketing_copy': {
        'model_name': 'gpt2',
        'max_length': 300,
        'temperature': 0.8,
        'top_p': 0.9,
        'repetition_penalty': 1.1
    }
}