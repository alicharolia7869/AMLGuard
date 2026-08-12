import os
import io
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, make_response
from routes.auth import login_required
from database.models import db, Transaction, Alert, Investigation, Customer
from engine.risk_engine import RiskEngine

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

investigations_bp = Blueprint('investigations', __name__)
risk_engine = RiskEngine()

@investigations_bp.route('/investigation/<txn_id>')
@login_required
def view_investigation(txn_id):
    txn = Transaction.query.filter_by(transaction_id=txn_id).first_or_404()
    alert = Alert.query.filter_by(transaction_id=txn_id).first()
    investigations = Investigation.query.filter_by(transaction_id=txn_id).order_by(Investigation.created_at.desc()).all()

    sender_cust = Customer.query.filter_by(account_number=txn.sender_account).first()
    receiver_cust = Customer.query.filter_by(account_number=txn.receiver_account).first()

    cust_avg = sender_cust.avg_monthly_income if sender_cust else 50000.0
    
    # Re-evaluate risk breakdown for explainability
    txn_dict = {
        'amount': txn.amount,
        'transaction_type': txn.transaction_type,
        'hour_of_day': txn.transaction_time.hour if txn.transaction_time else 12,
        'is_new_beneficiary': 1 if (not receiver_cust) else 0,
        'is_high_risk_country': 1 if any(loc in str(txn.location) for loc in ['Panama', 'Cayman', 'Seychelles']) else 0,
        'location': txn.location,
        'sender_customer_id': sender_cust.customer_id if sender_cust else 'UNKNOWN'
    }

    risk_eval = risk_engine.compute_risk(txn_dict, cust_avg=cust_avg)

    # Historical transactions from sender
    history_txns = Transaction.query.filter(
        (Transaction.sender_account == txn.sender_account) & (Transaction.transaction_id != txn.transaction_id)
    ).order_by(Transaction.transaction_time.desc()).limit(8).all()

    return render_template('investigation.html',
                           txn=txn,
                           alert=alert,
                           investigations=investigations,
                           sender_cust=sender_cust,
                           receiver_cust=receiver_cust,
                           risk_eval=risk_eval,
                           history_txns=history_txns)

@investigations_bp.route('/investigation/<txn_id>/submit-decision', methods=['POST'])
@login_required
def submit_decision(txn_id):
    txn = Transaction.query.filter_by(transaction_id=txn_id).first_or_404()
    decision = request.form.get('decision')
    comments = request.form.get('comments', '').strip()
    investigator_name = session.get('user_name', 'Investigator')

    if decision in ['UNDER_REVIEW', 'ESCALATED_SAR', 'CLEARED', 'REJECTED']:
        investigation = Investigation(
            transaction_id=txn_id,
            investigator=investigator_name,
            decision=decision,
            comments=comments
        )
        db.session.add(investigation)

        # Sync Alert Status
        alert = Alert.query.filter_by(transaction_id=txn_id).first()
        if alert:
            if decision == 'UNDER_REVIEW':
                alert.status = 'UNDER_REVIEW'
            elif decision == 'ESCALATED_SAR':
                alert.status = 'ESCALATED'
            elif decision == 'CLEARED':
                alert.status = 'CLEARED'
            alert.assigned_to = investigator_name

        db.session.commit()
        flash(f"Investigation decision '{decision}' recorded successfully.", "success")
    else:
        flash("Invalid decision code selected.", "danger")

    return redirect(url_for('investigations.view_investigation', txn_id=txn_id))

@investigations_bp.route('/investigation/<txn_id>/export-sar')
@login_required
def export_sar(txn_id):
    txn = Transaction.query.filter_by(transaction_id=txn_id).first_or_404()
    alert = Alert.query.filter_by(transaction_id=txn_id).first()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#DC2626'))
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1E293B'))
    normal_style = styles['Normal']

    story = []
    story.append(Paragraph("<b>AMLGUARD — SUSPICIOUS ACTIVITY REPORT (SAR)</b>", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | Reference ID: SAR-{txn_id}", normal_style))
    story.append(Spacer(1, 15))

    # Transaction Summary Table
    txn_data = [
        ["Field", "Details"],
        ["Transaction ID", txn.transaction_id],
        ["Sender Account", txn.sender_account],
        ["Receiver Account", txn.receiver_account],
        ["Amount Monitored", f"INR {txn.amount:,.2f}"],
        ["Transaction Type", txn.transaction_type],
        ["Risk Score / Tier", f"{txn.risk_score} / 100 ({txn.risk_tier})"],
        ["ML Prob / Anomaly", f"{txn.ml_prediction:.2f} / {txn.anomaly_score:.2f}"],
        ["Location", txn.location],
        ["Timestamp", str(txn.transaction_time)]
    ]
    t = Table(txn_data, colWidths=[180, 340])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Detection Reasons & Triggered Rules</b>", heading_style))
    story.append(Spacer(1, 5))
    reasons_text = alert.reasons if alert else "Suspicious score generated by multi-layer risk engine."
    story.append(Paragraph(reasons_text.replace('\n', '<br/>'), normal_style))

    doc.build(story)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=SAR_Report_{txn_id}.pdf'
    return response
