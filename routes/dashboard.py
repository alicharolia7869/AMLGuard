from flask import Blueprint, render_template, jsonify
from routes.auth import login_required
from database.models import db, Transaction, Alert, Customer
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Summary KPI Statistics
    total_txns = Transaction.query.count()
    suspicious_count = Transaction.query.filter(Transaction.risk_score >= 61).count()
    critical_alerts = Alert.query.filter_by(severity='CRITICAL', status='PENDING').count()
    high_risk_customers = Customer.query.filter(Customer.risk_level.in_(['HIGH', 'CRITICAL'])).count()
    
    total_amount_sum = db.session.query(func.sum(Transaction.amount)).scalar() or 0.0
    
    # Recent Critical / High Alerts
    recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(6).all()
    
    # Top Suspicious Transactions
    top_suspicious = Transaction.query.order_by(Transaction.risk_score.desc()).limit(5).all()

    return render_template('dashboard.html',
                           total_txns=total_txns,
                           suspicious_count=suspicious_count,
                           critical_alerts=critical_alerts,
                           high_risk_customers=high_risk_customers,
                           total_amount_sum=total_amount_sum,
                           recent_alerts=recent_alerts,
                           top_suspicious=top_suspicious)
