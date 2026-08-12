from flask import Blueprint, render_template, request, jsonify
from routes.auth import login_required
from engine.risk_engine import RiskEngine

simulator_bp = Blueprint('simulator', __name__)
risk_engine = RiskEngine()

@simulator_bp.route('/simulator', methods=['GET', 'POST'])
@login_required
def simulator():
    sim_result = None
    
    if request.method == 'POST':
        sender_acc = request.form.get('sender_account', 'ACC-50001')
        receiver_acc = request.form.get('receiver_account', 'ACC-50002')
        amount = request.form.get('amount', 50000.0, type=float)
        t_type = request.form.get('transaction_type', 'WIRE')
        hour = request.form.get('hour_of_day', 2, type=int)
        is_new_ben = request.form.get('is_new_beneficiary', 0, type=int)
        is_high_geo = request.form.get('is_high_risk_country', 0, type=int)
        location = request.form.get('location', 'Panama City, PA')
        cust_avg = request.form.get('cust_avg', 50000.0, type=float)

        txn_dict = {
            'amount': amount,
            'transaction_type': t_type,
            'hour_of_day': hour,
            'is_new_beneficiary': is_new_ben,
            'is_high_risk_country': is_high_geo,
            'location': location,
            'sender_customer_id': 'CUST-SIMULATED'
        }

        sim_result = risk_engine.compute_risk(txn_dict, cust_avg=cust_avg)
        sim_result['inputs'] = {
            'sender_account': sender_acc,
            'receiver_account': receiver_acc,
            'amount': amount,
            'transaction_type': t_type,
            'hour_of_day': hour,
            'is_new_beneficiary': is_new_ben,
            'is_high_risk_country': is_high_geo,
            'location': location,
            'cust_avg': cust_avg
        }

    return render_template('simulator.html', sim_result=sim_result)

@simulator_bp.route('/api/simulator/evaluate', methods=['POST'])
@login_required
def evaluate_api():
    data = request.get_json() or {}
    amount = float(data.get('amount', 50000.0))
    t_type = str(data.get('transaction_type', 'WIRE'))
    hour = int(data.get('hour_of_day', 2))
    is_new_ben = int(data.get('is_new_beneficiary', 0))
    is_high_geo = int(data.get('is_high_risk_country', 0))
    location = str(data.get('location', 'Panama City, PA'))
    cust_avg = float(data.get('cust_avg', 50000.0))

    txn_dict = {
        'amount': amount,
        'transaction_type': t_type,
        'hour_of_day': hour,
        'is_new_beneficiary': is_new_ben,
        'is_high_risk_country': is_high_geo,
        'location': location,
        'sender_customer_id': 'CUST-SIMULATED'
    }

    result = risk_engine.compute_risk(txn_dict, cust_avg=cust_avg)
    return jsonify(result)
