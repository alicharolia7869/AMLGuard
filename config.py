import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = 'VERCEL' in os.environ or os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL') == 'true'

if IS_VERCEL:
    DB_PATH = "/tmp/amlguard.db"
    UPLOAD_DIR = "/tmp/uploads"
    MODEL_DIR = "/tmp/models"
else:
    DB_PATH = os.path.join(BASE_DIR, 'amlguard.db')
    UPLOAD_DIR = os.path.join(BASE_DIR, 'data', 'uploads')
    MODEL_DIR = os.path.join(BASE_DIR, 'models')

# Check if model files exist in repository models/ folder first
REPO_MODEL_DIR = os.path.join(BASE_DIR, 'models')
EFF_MODEL_DIR = REPO_MODEL_DIR if os.path.exists(REPO_MODEL_DIR) and not IS_VERCEL else MODEL_DIR

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'amlguard-secure-secret-key-2026-financial-compliance'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Settings
    UPLOAD_FOLDER = UPLOAD_DIR
    ALLOWED_EXTENSIONS = {'csv'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    
    # Model Artifact Paths
    MODEL_DIR = EFF_MODEL_DIR
    CLASSIFIER_MODEL_PATH = os.path.join(EFF_MODEL_DIR, 'aml_model.pkl')
    ANOMALY_MODEL_PATH = os.path.join(EFF_MODEL_DIR, 'anomaly_model.pkl')
    SCALER_PATH = os.path.join(EFF_MODEL_DIR, 'scaler.pkl')
    FEATURE_NAMES_PATH = os.path.join(EFF_MODEL_DIR, 'features.pkl')
