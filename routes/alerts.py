from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from database.models import db, Alert, Transaction

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alerts')
@login_required
def list_alerts():
    severity = request.args.get('severity', '')
    status = request.args.get('status', '')
    assigned_me = request.args.get('assigned_me', '')

    query = Alert.query.join(Transaction, Alert.transaction_id == Transaction.transaction_id)

    if severity:
        query = query.filter(Alert.severity == severity)

    if status:
        query = query.filter(Alert.status == status)

    if assigned_me == '1':
        query = query.filter(Alert.assigned_to == session.get('user_name'))

    alerts = query.order_by(Alert.created_at.desc()).all()

    return render_template('alerts.html',
                           alerts=alerts,
                           current_severity=severity,
                           current_status=status,
                           assigned_me=assigned_me)

@alerts_bp.route('/alerts/<int:alert_id>/update-status', methods=['POST'])
@login_required
def update_status(alert_id):
    new_status = request.form.get('status')
    alert = db.get_or_404(Alert, alert_id)
    
    if new_status in ['PENDING', 'UNDER_REVIEW', 'ESCALATED', 'CLEARED']:
        alert.status = new_status
        alert.assigned_to = session.get('user_name', 'Investigator')
        db.session.commit()
        flash(f"Alert #{alert.id} status updated to '{new_status}'.", "success")
    else:
        flash("Invalid status selection.", "danger")

    return redirect(url_for('alerts.list_alerts'))
