import os
import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

from routes.auth import login_required
from database.models import db, Transaction, Alert, Customer
from engine.risk_engine import RiskEngine

transactions_bp = Blueprint('transactions', __name__)
risk_engine = RiskEngine()

@transactions_bp.route('/transactions')
@login_required
def list_transactions():
    page = request.args.get('page', 1, type=int)
    search_q = request.args.get('q', '').strip()
    risk_filter = request.args.get('risk', '')
    type_filter = request.args.get('type', '')
    min_amount = request.args.get('min_amount', type=float)
    sort_by = request.args.get('sort', 'risk_desc')

    query = Transaction.query

    if search_q:
        query = query.filter(
            (Transaction.transaction_id.ilike(f"%{search_q}%")) |
            (Transaction.sender_account.ilike(f"%{search_q}%")) |
            (Transaction.receiver_account.ilike(f"%{search_q}%"))
        )

    if risk_filter:
        query = query.filter(Transaction.risk_tier == risk_filter)

    if type_filter:
        query = query.filter(Transaction.transaction_type == type_filter)

    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)

    if sort_by == 'risk_desc':
        query = query.order_by(Transaction.risk_score.desc())
    elif sort_by == 'risk_asc':
        query = query.order_by(Transaction.risk_score.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Transaction.amount.desc())
    elif sort_by == 'date_desc':
        query = query.order_by(Transaction.transaction_time.desc())
    else:
        query = query.order_by(Transaction.transaction_time.desc())

    pagination = query.paginate(page=page, per_page=15, error_out=False)
    transactions = pagination.items

    return render_template('transactions.html',
                           transactions=transactions,
                           pagination=pagination,
                           search_q=search_q,
                           risk_filter=risk_filter,
                           type_filter=type_filter,
                           min_amount=min_amount,
                           sort_by=sort_by)

@transactions_bp.route('/transactions/upload', methods=['POST'])
@login_required
def upload_csv():
    if 'csv_file' not in request.files:
        flash("No file selected for upload.", "danger")
        return redirect(url_for('transactions.list_transactions'))

    file = request.files['csv_file']
    if file.filename == '':
        flash("No CSV file selected.", "danger")
        return redirect(url_for('transactions.list_transactions'))

    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        try:
            df = pd.read_csv(file_path)
            processed_count = 0
            alert_count = 0

            for idx, row in df.iterrows():
                val_id = row.get('transaction_id')
                if pd.isna(val_id) or not str(val_id).strip():
                    txn_id = f"TXN-{10000 + Transaction.query.count() + idx}"
                else:
                    txn_id = str(val_id).strip()
                
                # Check if already exists
                existing = Transaction.query.filter_by(transaction_id=txn_id).first()
                if existing:
                    continue

                sender_val = row.get('sender_account')
                sender = str(sender_val).strip() if pd.notna(sender_val) else 'ACC-50001'
                
                rec_val = row.get('receiver_account')
                receiver = str(rec_val).strip() if pd.notna(rec_val) else 'ACC-50002'
                
                amt_val = row.get('amount')
                try:
                    amount = float(amt_val) if pd.notna(amt_val) else 10000.0
                except (ValueError, TypeError):
                    amount = 10000.0

                type_val = row.get('transaction_type')
                t_type = str(type_val).strip() if pd.notna(type_val) else 'TRANSFER'
                
                loc_val = row.get('location')
                location = str(loc_val).strip() if pd.notna(loc_val) else 'Mumbai, IN'
                
                hour_val = row.get('hour_of_day')
                try:
                    hour_of_day = int(hour_val) if pd.notna(hour_val) else 14
                except (ValueError, TypeError):
                    hour_of_day = 14

                new_ben_val = row.get('is_new_beneficiary')
                try:
                    is_new_ben = int(new_ben_val) if pd.notna(new_ben_val) else 0
                except (ValueError, TypeError):
                    is_new_ben = 0

                high_geo_val = row.get('is_high_risk_country')
                try:
                    is_high_geo = int(high_geo_val) if pd.notna(high_geo_val) else 0
                except (ValueError, TypeError):
                    is_high_geo = 0

                sender_cust_val = row.get('sender_customer_id')
                sender_cust_id = str(sender_cust_val).strip() if pd.notna(sender_cust_val) else 'CUST-1001'

                # Risk engine evaluation
                txn_dict = {
                    'amount': amount,
                    'transaction_type': t_type,
                    'hour_of_day': hour_of_day,
                    'is_new_beneficiary': is_new_ben,
                    'is_high_risk_country': is_high_geo,
                    'location': location,
                    'sender_customer_id': sender_cust_id
                }

                eval_res = risk_engine.compute_risk(txn_dict)

                txn = Transaction(
                    transaction_id=txn_id,
                    sender_account=sender,
                    receiver_account=receiver,
                    amount=amount,
                    transaction_type=t_type,
                    transaction_time=datetime.now(),
                    location=location,
                    risk_score=eval_res['risk_score'],
                    ml_prediction=eval_res['ml_prediction'],
                    anomaly_score=eval_res['anomaly_score'],
                    rule_score=eval_res['rule_score'],
                    risk_tier=eval_res['risk_tier']
                )
                db.session.add(txn)
                processed_count += 1

                # Generate alert if high or critical risk
                if eval_res['risk_score'] >= 61:
                    alert = Alert(
                        transaction_id=txn_id,
                        alert_type='SUSPICIOUS_BEHAVIOR',
                        severity=eval_res['risk_tier'],
                        reasons="\n".join(eval_res['reasons']),
                        status='PENDING'
                    )
                    db.session.add(alert)
                    alert_count += 1

            db.session.commit()
            flash(f"Successfully processed {processed_count} transactions. Generated {alert_count} suspicious alerts!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error parsing CSV file: {str(e)}", "danger")

    return redirect(url_for('transactions.list_transactions'))
