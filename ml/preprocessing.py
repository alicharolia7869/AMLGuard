import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    'amount',
    'amount_to_avg_ratio',
    'hour_of_day',
    'is_off_hours',
    'is_structuring_range',
    'is_new_beneficiary',
    'is_high_risk_country',
    'type_WIRE',
    'type_CASH_DEPOSIT',
    'type_TRANSFER'
]

def preprocess_and_feature_engineering(df, customer_avg_map=None, scaler=None, is_training=True):
    df_feat = df.copy()

    # Calculate or retrieve customer historical averages
    if customer_avg_map is None:
        customer_avg_map = df_feat.groupby('sender_customer_id')['amount'].mean().to_dict()

    df_feat['cust_avg_amount'] = df_feat['sender_customer_id'].map(customer_avg_map).fillna(df_feat['amount'])
    
    # Avoid zero division
    df_feat['cust_avg_amount'] = df_feat['cust_avg_amount'].replace(0, 10000.0)
    df_feat['amount_to_avg_ratio'] = df_feat['amount'] / df_feat['cust_avg_amount']

    # Hour feature & off-hours indicator (1 AM to 4 AM)
    if 'hour_of_day' not in df_feat.columns:
        if 'transaction_time' in df_feat.columns:
            df_feat['hour_of_day'] = pd.to_datetime(df_feat['transaction_time']).dt.hour
        else:
            df_feat['hour_of_day'] = 12

    df_feat['is_off_hours'] = df_feat['hour_of_day'].apply(lambda h: 1 if 1 <= h <= 4 else 0)

    # Structuring / Smurfing indicator (9000 <= amount <= 9999)
    df_feat['is_structuring_range'] = df_feat['amount'].apply(lambda amt: 1 if 9000 <= amt <= 9999 else 0)

    # One-hot encode transaction type
    for t_type in ['WIRE', 'CASH_DEPOSIT', 'TRANSFER']:
        col_name = f'type_{t_type}'
        if 'transaction_type' in df_feat.columns:
            df_feat[col_name] = (df_feat['transaction_type'] == t_type).astype(int)
        else:
            df_feat[col_name] = 0

    # Ensure binary columns exist
    if 'is_new_beneficiary' not in df_feat.columns:
        df_feat['is_new_beneficiary'] = 0
    if 'is_high_risk_country' not in df_feat.columns:
        df_feat['is_high_risk_country'] = 0

    # Extract feature matrix X
    X = df_feat[FEATURE_COLUMNS].fillna(0)

    if is_training:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        return X_scaled, scaler, customer_avg_map, FEATURE_COLUMNS
    else:
        if scaler is not None:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X.values
        return X_scaled, FEATURE_COLUMNS
