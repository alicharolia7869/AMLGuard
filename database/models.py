from datetime import datetime
# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='investigator') # 'admin', 'investigator'
    created_at = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(30), unique=True, nullable=False)
    account_type = db.Column(db.String(20), default='Savings')
    account_age_months = db.Column(db.Integer, default=12)
    avg_monthly_income = db.Column(db.Float, default=50000.0)
    risk_level = db.Column(db.String(20), default='LOW')
    country = db.Column(db.String(50), default='India')
    created_at = db.Column(db.DateTime, default=datetime.now)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    sender_account = db.Column(db.String(30), nullable=False)
    receiver_account = db.Column(db.String(30), nullable=False)
    sender_name = db.Column(db.String(100))
    receiver_name = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(30), default='TRANSFER')
    transaction_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(100), default='Mumbai, IN')
    status = db.Column(db.String(30), default='COMPLETED')
    risk_score = db.Column(db.Integer, default=0)
    ml_prediction = db.Column(db.Float, default=0.0)
    anomaly_score = db.Column(db.Float, default=0.0)
    rule_score = db.Column(db.Integer, default=0)
    risk_tier = db.Column(db.String(20), default='LOW')
    created_at = db.Column(db.DateTime, default=datetime.now)

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), db.ForeignKey('transactions.transaction_id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False) # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    reasons = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='PENDING') # 'PENDING', 'UNDER_REVIEW', 'ESCALATED', 'CLEARED'
    assigned_to = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    transaction = db.relationship('Transaction', backref=db.backref('alerts', lazy=True))

class Investigation(db.Model):
    __tablename__ = 'investigations'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), db.ForeignKey('transactions.transaction_id'), nullable=False)
    investigator = db.Column(db.String(100), nullable=False)
    decision = db.Column(db.String(50), nullable=False) # 'UNDER_REVIEW', 'ESCALATED_SAR', 'CLEARED', 'REJECTED'
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    transaction = db.relationship('Transaction', backref=db.backref('investigations', lazy=True))

class Rule(db.Model):
    __tablename__ = 'rules'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_code = db.Column(db.String(30), unique=True, nullable=False)
    rule_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points = db.Column(db.Integer, default=15)
    is_active = db.Column(db.Boolean, default=True)
