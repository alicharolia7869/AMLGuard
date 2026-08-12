from flask import Blueprint, render_template, jsonify
from routes.auth import login_required
from database.models import db, Transaction, Alert
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics_view():
    return render_template('analytics.html')

@analytics_bp.route('/api/analytics/charts')
@login_required
def analytics_data():
    # 1. Risk Tier Counts
    tier_counts = db.session.query(
        Transaction.risk_tier, func.count(Transaction.id)
    ).group_by(Transaction.risk_tier).all()

    risk_dist = {tier: count for tier, count in tier_counts}

    # 2. Transaction Type Counts
    type_counts = db.session.query(
        Transaction.transaction_type, func.count(Transaction.id)
    ).group_by(Transaction.transaction_type).all()

    type_dist = {t_type: count for t_type, count in type_counts}

    # 3. Daily Volume Trend (Recent 10 days)
    daily_vol = db.session.query(
        func.date(Transaction.transaction_time), func.sum(Transaction.amount), func.count(Transaction.id)
    ).group_by(func.date(Transaction.transaction_time)).order_by(func.date(Transaction.transaction_time).asc()).limit(15).all()

    timeline_data = {
        'dates': [str(item[0]) for item in daily_vol],
        'amounts': [float(item[1] or 0) for item in daily_vol],
        'counts': [int(item[2]) for item in daily_vol]
    }

    # 4. Alert Status Counts
    alert_counts = db.session.query(
        Alert.status, func.count(Alert.id)
    ).group_by(Alert.status).all()

    alert_dist = {status: count for status, count in alert_counts}

    return jsonify({
        'risk_distribution': risk_dist,
        'type_distribution': type_dist,
        'timeline': timeline_data,
        'alert_distribution': alert_dist
    })
