from flask import Blueprint, render_template, jsonify
from routes.auth import login_required
from database.models import db, Transaction, Customer

network_bp = Blueprint('network', __name__)

@network_bp.route('/network')
@login_required
def network_view():
    return render_template('network.html')

@network_bp.route('/api/network/data')
@login_required
def network_data():
    transactions = Transaction.query.order_by(Transaction.risk_score.desc()).limit(150).all()
    
    nodes_map = {}
    edges = []

    # Map account nodes and transaction edges
    for txn in transactions:
        sender = txn.sender_account
        receiver = txn.receiver_account

        # Account Nodes
        for acc in [sender, receiver]:
            if acc not in nodes_map:
                cust = Customer.query.filter_by(account_number=acc).first()
                risk = cust.risk_level if cust else 'LOW'
                
                # Check max risk of any txn associated with this node
                nodes_map[acc] = {
                    'id': acc,
                    'label': f"{acc}\n({cust.name if cust else 'Account'})",
                    'risk_level': risk,
                    'group': risk,
                    'val': 1
                }
            else:
                nodes_map[acc]['val'] += 1

        # Edge color by risk score
        if txn.risk_score >= 81:
            edge_color = '#EF4444' # Red
        elif txn.risk_score >= 61:
            edge_color = '#F97316' # Orange
        elif txn.risk_score >= 31:
            edge_color = '#FBBF24' # Yellow
        else:
            edge_color = '#10B981' # Green

        edges.append({
            'from': sender,
            'to': receiver,
            'label': f"₹{txn.amount:,.0f} ({txn.risk_score} Risk)",
            'arrows': 'to',
            'color': {'color': edge_color, 'highlight': '#FFFFFF'},
            'width': 2 if txn.risk_score >= 61 else 1,
            'txn_id': txn.transaction_id,
            'risk_score': txn.risk_score
        })

    nodes = list(nodes_map.values())

    return jsonify({
        'nodes': nodes,
        'edges': edges
    })
