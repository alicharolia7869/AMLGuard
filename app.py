import os
import random
from datetime import datetime, timedelta
# pyrefly: ignore [missing-import]
from flask import Flask, redirect, url_for

from config import Config
from database.models import db, User, Customer, Transaction, Alert, Rule
from engine.risk_engine import RiskEngine

# Import Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.transactions import transactions_bp
from routes.alerts import alerts_bp
from routes.customers import customers_bp
from routes.investigations import investigations_bp
from routes.network import network_bp
from routes.analytics import analytics_bp
from routes.rules import rules_bp
from routes.simulator import simulator_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure Upload & Model Directories Exist
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['MODEL_DIR'], exist_ok=True)
    except Exception as e:
        print(f"Directory creation note: {e}")

    # Initialize DB
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(investigations_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(rules_bp)
    app.register_blueprint(simulator_bp)

    @app.route('/')
    def root():
        # pyrefly: ignore [missing-import]
        from flask import session
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Seed Database on Startup
    with app.app_context():
        db.create_all()
        seed_initial_data()

    return app

def seed_initial_data():
    # 1. Seed Users
    if User.query.count() == 0:
        print("Seeding default administrative and investigator users...")
        admin = User(name='Admin Officer', email='admin@amlguard.io', role='admin')
        admin.set_password('admin123')
        
        investigator = User(name='Senior Investigator', email='investigator@amlguard.io', role='investigator')
        investigator.set_password('investigator123')
        
        db.session.add(admin)
        db.session.add(investigator)
        db.session.commit()

    # 2. Seed ML Models check
    model_path = Config.CLASSIFIER_MODEL_PATH
    if not os.path.exists(model_path):
        print("ML Model binaries not found. Training ML pipeline...")
        from ml.train_model import train_and_evaluate_models
        train_and_evaluate_models()

    # 3. Seed Customers & Transactions if database empty
    if Transaction.query.count() == 0:
        print("Seeding synthetic customer entities and transaction ledger...")
        risk_engine = RiskEngine()

        # Seed Customers
        customers_list = [
            {'id': 'CUST-1001', 'name': 'Apex Trading Corp', 'acc': 'ACC-50001', 'risk': 'HIGH', 'inc': 500000.0, 'country': 'Panama'},
            {'id': 'CUST-1002', 'name': 'Rajesh Sharma', 'acc': 'ACC-50002', 'risk': 'LOW', 'inc': 75000.0, 'country': 'India'},
            {'id': 'CUST-1003', 'name': 'Vanguard Shell Global', 'acc': 'ACC-50003', 'risk': 'CRITICAL', 'inc': 1200000.0, 'country': 'Cayman Islands'},
            {'id': 'CUST-1004', 'name': 'Priya Patel', 'acc': 'ACC-50004', 'risk': 'LOW', 'inc': 60000.0, 'country': 'India'},
            {'id': 'CUST-1005', 'name': 'Cyprus Horizon Ltd', 'acc': 'ACC-50005', 'risk': 'HIGH', 'inc': 850000.0, 'country': 'Cyprus'},
            {'id': 'CUST-1006', 'name': 'Amit Verma', 'acc': 'ACC-50006', 'risk': 'MEDIUM', 'inc': 110000.0, 'country': 'India'},
        ]

        for c_data in customers_list:
            c = Customer(
                customer_id=c_data['id'],
                name=c_data['name'],
                account_number=c_data['acc'],
                account_type='Business' if 'Corp' in c_data['name'] or 'Ltd' in c_data['name'] else 'Savings',
                account_age_months=random.randint(6, 60),
                avg_monthly_income=c_data['inc'],
                risk_level=c_data['risk'],
                country=c_data['country']
            )
            db.session.add(c)
        db.session.commit()

        # Seed Transactions
        seed_txns = [
            {'id': 'TXN-10452', 'sender': 'ACC-50003', 'receiver': 'ACC-50001', 'amount': 850000.0, 'type': 'WIRE', 'hour': 2, 'loc': 'George Town, KY', 'new_ben': 1, 'high_risk': 1},
            {'id': 'TXN-10453', 'sender': 'ACC-50001', 'receiver': 'ACC-50005', 'amount': 9500.0, 'type': 'CASH_DEPOSIT', 'hour': 14, 'loc': 'Panama City, PA', 'new_ben': 0, 'high_risk': 1},
            {'id': 'TXN-10454', 'sender': 'ACC-50001', 'receiver': 'ACC-50005', 'amount': 9800.0, 'type': 'CASH_DEPOSIT', 'hour': 15, 'loc': 'Panama City, PA', 'new_ben': 0, 'high_risk': 1},
            {'id': 'TXN-10455', 'sender': 'ACC-50002', 'receiver': 'ACC-50004', 'amount': 12500.0, 'type': 'TRANSFER', 'hour': 11, 'loc': 'Mumbai, IN', 'new_ben': 0, 'high_risk': 0},
            {'id': 'TXN-10456', 'sender': 'ACC-50005', 'receiver': 'ACC-50003', 'amount': 1450000.0, 'type': 'WIRE', 'hour': 3, 'loc': 'Nicosia, CY', 'new_ben': 1, 'high_risk': 1},
            {'id': 'TXN-10457', 'sender': 'ACC-50004', 'receiver': 'ACC-50006', 'amount': 5500.0, 'type': 'TRANSFER', 'hour': 16, 'loc': 'Delhi, IN', 'new_ben': 0, 'high_risk': 0},
            {'id': 'TXN-10458', 'sender': 'ACC-50006', 'receiver': 'ACC-50002', 'amount': 18000.0, 'type': 'TRANSFER', 'hour': 10, 'loc': 'Bangalore, IN', 'new_ben': 0, 'high_risk': 0},
            {'id': 'TXN-10459', 'sender': 'ACC-50003', 'receiver': 'ACC-50005', 'amount': 9600.0, 'type': 'CASH_DEPOSIT', 'hour': 1, 'loc': 'George Town, KY', 'new_ben': 1, 'high_risk': 1},
        ]

        base_dt = datetime.now()
        for idx, t_data in enumerate(seed_txns):
            txn_dict = {
                'amount': t_data['amount'],
                'transaction_type': t_data['type'],
                'hour_of_day': t_data['hour'],
                'is_new_beneficiary': t_data['new_ben'],
                'is_high_risk_country': t_data['high_risk'],
                'location': t_data['loc'],
                'sender_customer_id': 'CUST-1003' if t_data['sender'] == 'ACC-50003' else 'CUST-1001'
            }

            eval_res = risk_engine.compute_risk(txn_dict, cust_avg=100000.0)

            txn = Transaction(
                transaction_id=t_data['id'],
                sender_account=t_data['sender'],
                receiver_account=t_data['receiver'],
                amount=t_data['amount'],
                transaction_type=t_data['type'],
                transaction_time=base_dt - timedelta(hours=idx * 3),
                location=t_data['loc'],
                risk_score=eval_res['risk_score'],
                ml_prediction=eval_res['ml_prediction'],
                anomaly_score=eval_res['anomaly_score'],
                rule_score=eval_res['rule_score'],
                risk_tier=eval_res['risk_tier']
            )
            db.session.add(txn)

            if eval_res['risk_score'] >= 61:
                alert = Alert(
                    transaction_id=t_data['id'],
                    alert_type='SUSPICIOUS_PATTERN',
                    severity=eval_res['risk_tier'],
                    reasons="\n".join(eval_res['reasons']),
                    status='PENDING'
                )
                db.session.add(alert)

        db.session.commit()
        print("Database seeded with sample transactions and alerts!")

app = create_app()

if __name__ == '__main__':
    print("Launching AMLGuard Web Server on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)

