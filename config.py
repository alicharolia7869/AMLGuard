import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'amlguard-secure-secret-key-2026-financial-compliance'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'amlguard.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
    ALLOWED_EXTENSIONS = {'csv'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    
    # Model Artifact Paths
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    CLASSIFIER_MODEL_PATH = os.path.join(MODEL_DIR, 'aml_model.pkl')
    ANOMALY_MODEL_PATH = os.path.join(MODEL_DIR, 'anomaly_model.pkl')
    SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
    FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, 'features.pkl')
