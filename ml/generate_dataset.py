import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_aml_dataset(num_samples=2500, save_path=None):
    random.seed(42)
    np.random.seed(42)

    # Base customer pools
    num_customers = 150
    customer_ids = [f"CUST-{1000+i}" for i in range(num_customers)]
    accounts = [f"ACC-{50000+i}" for i in range(num_customers)]
    customer_acc_map = dict(zip(customer_ids, accounts))
    acc_customer_map = dict(zip(accounts, customer_ids))

    # Customer profiles (avg transaction amount, normal hours)
    customer_profiles = {}
    for c_id in customer_ids:
        customer_profiles[c_id] = {
            'avg_amount': float(np.random.choice([5000, 12000, 25000, 50000, 100000], p=[0.4, 0.3, 0.15, 0.1, 0.05])),
            'country': np.random.choice(['India', 'UAE', 'Singapore', 'UK', 'USA'], p=[0.7, 0.1, 0.1, 0.05, 0.05]),
            'account_age': random.randint(3, 120)
        }

    txn_types = ['TRANSFER', 'WIRE', 'CASH_DEPOSIT', 'ATM']
    locations = ['Mumbai, IN', 'Delhi, IN', 'Bangalore, IN', 'Dubai, AE', 'Singapore, SG', 'London, UK', 'Panama City, PA', 'George Town, KY']
    
    records = []
    base_time = datetime(2026, 8, 1, 8, 0, 0)

    # 1. Generate normal transactions (~85%)
    normal_count = int(num_samples * 0.85)
    for i in range(normal_count):
        sender_cust = random.choice(customer_ids)
        sender_acc = customer_acc_map[sender_cust]
        receiver_acc = random.choice([acc for acc in accounts if acc != sender_acc])
        
        avg_amt = customer_profiles[sender_cust]['avg_amount']
        amount = round(float(np.random.normal(avg_amt, avg_amt * 0.3)), 2)
        amount = max(500.0, amount)
        
        # Normal daytime hours (6 AM to 10 PM)
        hour = random.randint(6, 22)
        minute = random.randint(0, 59)
        day_offset = random.randint(0, 10)
        txn_time = base_time + timedelta(days=day_offset, hours=hour, minutes=minute)
        
        records.append({
            'transaction_id': f"TXN-{10000 + len(records)}",
            'sender_account': sender_acc,
            'receiver_account': receiver_acc,
            'sender_customer_id': sender_cust,
            'amount': amount,
            'transaction_type': random.choice(['TRANSFER', 'CASH_DEPOSIT', 'TRANSFER']),
            'transaction_time': txn_time.strftime('%Y-%m-%d %H:%M:%S'),
            'hour_of_day': hour,
            'location': 'Mumbai, IN' if random.random() < 0.8 else random.choice(locations[:3]),
            'is_new_beneficiary': random.choice([0, 0, 0, 1]),
            'is_high_risk_country': 0,
            'is_suspicious': 0
        })

    # 2. Generate Suspicious Patterns (~15%)
    suspicious_count = num_samples - normal_count
    
    # Pattern A: Smurfing / Structuring (amounts just below 10,000 threshold)
    smurf_count = int(suspicious_count * 0.3)
    smurf_senders = random.sample(customer_ids, 5)
    for i in range(smurf_count):
        sender_cust = random.choice(smurf_senders)
        sender_acc = customer_acc_map[sender_cust]
        receiver_acc = random.choice([acc for acc in accounts if acc != sender_acc])
        
        amount = round(random.uniform(9100.0, 9950.0), 2)
        hour = random.randint(1, 23)
        minute = random.randint(0, 59)
        day_offset = random.randint(0, 10)
        txn_time = base_time + timedelta(days=day_offset, hours=hour, minutes=minute)
        
        records.append({
            'transaction_id': f"TXN-{10000 + len(records)}",
            'sender_account': sender_acc,
            'receiver_account': receiver_acc,
            'sender_customer_id': sender_cust,
            'amount': amount,
            'transaction_type': 'CASH_DEPOSIT' if random.random() < 0.5 else 'WIRE',
            'transaction_time': txn_time.strftime('%Y-%m-%d %H:%M:%S'),
            'hour_of_day': hour,
            'location': random.choice(['Mumbai, IN', 'Delhi, IN']),
            'is_new_beneficiary': 1,
            'is_high_risk_country': 0,
            'is_suspicious': 1
        })

    # Pattern B: Sudden Extreme Amount Spike (>10x avg)
    spike_count = int(suspicious_count * 0.25)
    for i in range(spike_count):
        sender_cust = random.choice(customer_ids)
        sender_acc = customer_acc_map[sender_cust]
        receiver_acc = random.choice([acc for acc in accounts if acc != sender_acc])
        
        avg_amt = customer_profiles[sender_cust]['avg_amount']
        amount = round(avg_amt * random.uniform(12.0, 30.0), 2)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        day_offset = random.randint(0, 10)
        txn_time = base_time + timedelta(days=day_offset, hours=hour, minutes=minute)
        
        records.append({
            'transaction_id': f"TXN-{10000 + len(records)}",
            'sender_account': sender_acc,
            'receiver_account': receiver_acc,
            'sender_customer_id': sender_cust,
            'amount': amount,
            'transaction_type': 'WIRE',
            'transaction_time': txn_time.strftime('%Y-%m-%d %H:%M:%S'),
            'hour_of_day': hour,
            'location': random.choice(locations),
            'is_new_beneficiary': 1,
            'is_high_risk_country': 1 if 'Panama' in random.choice(locations) else 0,
            'is_suspicious': 1
        })

    # Pattern C: Rapid Velocity (Burst of transactions in short window)
    velocity_count = int(suspicious_count * 0.25)
    burst_senders = random.sample(customer_ids, 3)
    for i in range(velocity_count):
        sender_cust = random.choice(burst_senders)
        sender_acc = customer_acc_map[sender_cust]
        receiver_acc = random.choice([acc for acc in accounts if acc != sender_acc])
        
        amount = round(random.uniform(45000.0, 180000.0), 2)
        # Off hours or rapid sequence
        hour = random.randint(1, 4)
        minute = random.randint(0, 59)
        day_offset = random.randint(0, 10)
        txn_time = base_time + timedelta(days=day_offset, hours=hour, minutes=minute)
        
        records.append({
            'transaction_id': f"TXN-{10000 + len(records)}",
            'sender_account': sender_acc,
            'receiver_account': receiver_acc,
            'sender_customer_id': sender_cust,
            'amount': amount,
            'transaction_type': 'WIRE',
            'transaction_time': txn_time.strftime('%Y-%m-%d %H:%M:%S'),
            'hour_of_day': hour,
            'location': random.choice(['Panama City, PA', 'George Town, KY', 'Dubai, AE']),
            'is_new_beneficiary': 1,
            'is_high_risk_country': 1,
            'is_suspicious': 1
        })

    # Pattern D: Layered Circular Ring / Multi-hop laundering loop
    ring_count = suspicious_count - (smurf_count + spike_count + velocity_count)
    ring_nodes = ['ACC-59901', 'ACC-59902', 'ACC-59903', 'ACC-59904']
    for i in range(ring_count):
        sender_acc = ring_nodes[i % len(ring_nodes)]
        receiver_acc = ring_nodes[(i + 1) % len(ring_nodes)]
        sender_cust = f"CUST-{9000 + (i % 4)}"
        
        amount = round(random.uniform(750000.0, 1200000.0), 2)
        hour = random.randint(1, 4)
        txn_time = base_time + timedelta(days=random.randint(0, 5), hours=hour, minutes=random.randint(0, 59))
        
        records.append({
            'transaction_id': f"TXN-{10000 + len(records)}",
            'sender_account': sender_acc,
            'receiver_account': receiver_acc,
            'sender_customer_id': sender_cust,
            'amount': amount,
            'transaction_type': 'WIRE',
            'transaction_time': txn_time.strftime('%Y-%m-%d %H:%M:%S'),
            'hour_of_day': hour,
            'location': 'George Town, KY',
            'is_new_beneficiary': 1,
            'is_high_risk_country': 1,
            'is_suspicious': 1
        })

    df = pd.DataFrame(records)
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"Generated {len(df)} transactions and saved to {save_path}")

    return df

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_csv = os.path.join(base_dir, 'data', 'raw', 'transactions_dataset.csv')
    generate_aml_dataset(num_samples=2500, save_path=output_csv)
