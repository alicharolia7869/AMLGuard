class RuleEngine:
    def __init__(self):
        # Default AML Rules
        self.rules = [
            {
                'code': 'RULE_01',
                'name': '10x Average Amount Spike',
                'points': 20,
                'check': lambda txn, cust_avg: (txn.get('amount', 0) > cust_avg * 10) if cust_avg > 0 else False,
                'description': 'Transaction amount exceeds 10 times customer normal historical average.'
            },
            {
                'code': 'RULE_02',
                'name': 'Smurfing / Structuring Detection',
                'points': 20,
                'check': lambda txn, cust_avg: (9000 <= txn.get('amount', 0) <= 9999),
                'description': 'Amount is structured just below regulatory reporting thresholds (₹9,000–₹9,999).'
            },
            {
                'code': 'RULE_03',
                'name': 'Unusual Night Off-Hours',
                'points': 10,
                'check': lambda txn, cust_avg: (1 <= txn.get('hour_of_day', 12) <= 4),
                'description': 'Transaction initiated between 1:00 AM and 4:00 AM off-peak hours.'
            },
            {
                'code': 'RULE_04',
                'name': 'New Beneficiary Large Wire',
                'points': 15,
                'check': lambda txn, cust_avg: (txn.get('is_new_beneficiary', 0) == 1 and txn.get('amount', 0) >= 50000),
                'description': 'First-time transfer to new unverified beneficiary exceeding ₹50,000.'
            },
            {
                'code': 'RULE_05',
                'name': 'High-Risk Geo Jurisdiction',
                'points': 15,
                'check': lambda txn, cust_avg: (txn.get('is_high_risk_country', 0) == 1 or any(loc in str(txn.get('location', '')) for loc in ['Panama', 'Cayman', 'Seychelles', 'Offshore'])),
                'description': 'Transaction involves high-risk or secrecy jurisdiction location.'
            },
            {
                'code': 'RULE_06',
                'name': 'Rapid Velocity Spike',
                'points': 15,
                'check': lambda txn, cust_avg: txn.get('recent_velocity_count', 0) >= 4,
                'description': 'Multiple rapid transactions detected from sender account within short time window.'
            }
        ]

    def evaluate(self, txn_dict, cust_avg=50000.0):
        triggered_rules = []
        total_rule_points = 0
        reasons = []

        for rule in self.rules:
            try:
                if rule['check'](txn_dict, cust_avg):
                    triggered_rules.append(rule['code'])
                    total_rule_points += rule['points']
                    reasons.append(f"⚠ {rule['name']}: {rule['description']}")
            except Exception as e:
                continue

        return {
            'triggered_rules': triggered_rules,
            'rule_score': total_rule_points,
            'reasons': reasons
        }
