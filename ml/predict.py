import os

try:
    import joblib
    import pandas as pd
    import numpy as np
    HAS_ML = True
except ImportError:
    HAS_ML = False

class AMLPredictor:
    def __init__(self, model_dir=None):
        if model_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'models')

        self.rf_path = os.path.join(model_dir, 'aml_model.pkl')
        self.iso_path = os.path.join(model_dir, 'anomaly_model.pkl')
        self.scaler_path = os.path.join(model_dir, 'scaler.pkl')
        self.features_path = os.path.join(model_dir, 'features.pkl')

        self.loaded = False
        if HAS_ML:
            self.load_models()

    def load_models(self):
        if not HAS_ML:
            self.loaded = False
            return

        if os.path.exists(self.rf_path) and os.path.exists(self.iso_path) and os.path.exists(self.scaler_path):
            try:
                self.rf_model = joblib.load(self.rf_path)
                self.iso_model = joblib.load(self.iso_path)
                self.scaler = joblib.load(self.scaler_path)
                feat_data = joblib.load(self.features_path)
                self.feature_names = feat_data.get('feature_names', [])
                self.cust_avg_map = feat_data.get('cust_avg_map', {})
                self.loaded = True
            except Exception as e:
                print(f"Error loading ML models: {e}")
                self.loaded = False

    def predict_single(self, txn_dict):
        """
        Takes a single transaction dictionary and returns ML prediction probability & Anomaly score.
        """
        if HAS_ML and not self.loaded:
            self.load_models()

        sender = txn_dict.get('sender_customer_id', 'UNKNOWN')
        cust_avg = getattr(self, 'cust_avg_map', {}).get(sender, 50000.0) if hasattr(self, 'cust_avg_map') else 50000.0
        
        amount = float(txn_dict.get('amount', 0))
        ratio = amount / cust_avg if cust_avg > 0 else 1.0
        
        hour = int(txn_dict.get('hour_of_day', 12))
        is_off_hours = 1 if 1 <= hour <= 4 else 0
        is_structuring = 1 if 9000 <= amount <= 9999 else 0
        is_new_ben = int(txn_dict.get('is_new_beneficiary', 0))
        is_high_geo = int(txn_dict.get('is_high_risk_country', 0))
        
        t_type = txn_dict.get('transaction_type', 'TRANSFER')
        type_wire = 1 if t_type == 'WIRE' else 0
        type_cash = 1 if t_type == 'CASH_DEPOSIT' else 0
        type_transfer = 1 if t_type == 'TRANSFER' else 0

        if HAS_ML and self.loaded and getattr(self, 'scaler', None) is not None:
            cols = getattr(self, 'feature_names', None) or [
                'amount', 'amount_to_avg_ratio', 'hour_of_day', 'is_off_hours',
                'is_structuring_range', 'is_new_beneficiary', 'is_high_risk_country',
                'type_WIRE', 'type_CASH_DEPOSIT', 'type_TRANSFER'
            ]

            feat_df = pd.DataFrame([{
                'amount': amount,
                'amount_to_avg_ratio': ratio,
                'hour_of_day': hour,
                'is_off_hours': is_off_hours,
                'is_structuring_range': is_structuring,
                'is_new_beneficiary': is_new_ben,
                'is_high_risk_country': is_high_geo,
                'type_WIRE': type_wire,
                'type_CASH_DEPOSIT': type_cash,
                'type_TRANSFER': type_transfer
            }], columns=cols)

            feat_scaled = self.scaler.transform(feat_df)
            ml_prob = float(self.rf_model.predict_proba(feat_scaled)[0, 1])
            
            raw_iso_score = float(self.iso_model.decision_function(feat_scaled)[0])
            anomaly_score = max(0.0, min(1.0, 0.5 - (raw_iso_score * 2.5)))
        else:
            # Fallback mathematical heuristic
            ml_prob = 0.85 if (ratio > 5 or is_structuring or is_high_geo) else 0.12
            anomaly_score = 0.75 if (is_off_hours or ratio > 8) else 0.18

        return {
            'ml_prediction': round(ml_prob, 4),
            'anomaly_score': round(anomaly_score, 4)
        }
