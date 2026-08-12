from flask import Blueprint, render_template, request
from routes.auth import login_required
from database.models import db, Customer, Transaction

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers')
@login_required
def list_customers():
    risk_level = request.args.get('risk_level', '')
    search_q = request.args.get('q', '').strip()

    query = Customer.query

    if risk_level:
        query = query.filter_by(risk_level=risk_level)

    if search_q:
        query = query.filter(
            (Customer.name.ilike(f"%{search_q}%")) |
            (Customer.customer_id.ilike(f"%{search_q}%")) |
            (Customer.account_number.ilike(f"%{search_q}%"))
        )

    customers = query.order_by(Customer.risk_level.desc(), Customer.name.asc()).all()

    # Calculate live transaction metrics for customers
    customer_data = []
    for c in customers:
        txns = Transaction.query.filter(
            (Transaction.sender_account == c.account_number) |
            (Transaction.receiver_account == c.account_number)
        ).all()
        
        txn_count = len(txns)
        flagged_count = sum(1 for t in txns if t.risk_score >= 61)
        total_vol = sum(t.amount for t in txns)

        customer_data.append({
            'customer': c,
            'txn_count': txn_count,
            'flagged_count': flagged_count,
            'total_vol': total_vol
        })

    return render_template('customers.html',
                           customer_data=customer_data,
                           risk_level=risk_level,
                           search_q=search_q)
