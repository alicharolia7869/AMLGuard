from ml.predict import AMLPredictor
from engine.rule_engine import RuleEngine

class RiskEngine:
    def __init__(self, model_dir=None):
        self.predictor = AMLPredictor(model_dir=model_dir)
        self.rule_engine = RuleEngine()

    def compute_risk(self, txn_dict, cust_avg=50000.0):
        """
        Combines:
        - Random Forest ML Prediction Probability (Max 40 pts)
        - Isolation Forest Anomaly Score (Max 25 pts)
        - Rule Engine Violations (Max 20 pts)
        - Behavioral Ratio Deviation (Max 15 pts)
        Total Max: 100 Risk Score
        """
        ml_res = self.predictor.predict_single(txn_dict)
        ml_prob = ml_res['ml_prediction']
        anomaly_score = ml_res['anomaly_score']

        rule_res = self.rule_engine.evaluate(txn_dict, cust_avg=cust_avg)
        rule_score = rule_res['rule_score']
        reasons = rule_res['reasons']

        # 1. ML Classifier Score (0 - 40 points)
        ml_pts = ml_prob * 40.0

        # 2. Anomaly Score (0 - 25 points)
        anomaly_pts = anomaly_score * 25.0

        # 3. Rule Violations Score (0 - 20 points)
        rule_pts = min(20.0, float(rule_score))

        # 4. Behavioral Ratio Deviation (0 - 15 points)
        amount = float(txn_dict.get('amount', 0))
        ratio = amount / cust_avg if cust_avg > 0 else 1.0
        
        if ratio >= 10.0:
            behavior_pts = 15.0
        elif ratio >= 5.0:
            behavior_pts = 10.0
        elif ratio >= 2.5:
            behavior_pts = 5.0
        else:
            behavior_pts = 0.0

        # Final Risk Score (0 - 100)
        final_score = int(round(ml_pts + anomaly_pts + rule_pts + behavior_pts))
        final_score = max(0, min(100, final_score))

        # Categorize Risk Tier
        if final_score >= 81:
            tier = 'CRITICAL'
        elif final_score >= 61:
            tier = 'HIGH'
        elif final_score >= 31:
            tier = 'MEDIUM'
        else:
            tier = 'LOW'

        # Default reasons if no rule triggered but ML score high
        if not reasons:
            if ml_prob >= 0.7:
                reasons.append("⚠ High ML Anomaly Pattern: Model identified suspicious feature co-occurrence.")
            elif ratio >= 3.0:
                reasons.append("⚠ Transaction amount significantly above customer historical baseline.")
            else:
                reasons.append("✔ Normal transaction behavior observed.")

        return {
            'risk_score': final_score,
            'risk_tier': tier,
            'ml_prediction': round(ml_prob, 4),
            'anomaly_score': round(anomaly_score, 4),
            'rule_score': int(rule_score),
            'breakdown': {
                'ml_points': round(ml_pts, 1),
                'anomaly_points': round(anomaly_pts, 1),
                'rule_points': round(rule_pts, 1),
                'behavior_points': round(behavior_pts, 1)
            },
            'triggered_rules': rule_res['triggered_rules'],
            'reasons': reasons
        }
