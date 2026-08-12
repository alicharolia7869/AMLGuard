import os
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from generate_dataset import generate_aml_dataset
from preprocessing import preprocess_and_feature_engineering

def train_and_evaluate_models():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'raw', 'transactions_dataset.csv')
    model_dir = os.path.join(base_dir, 'models')
    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print("Generating new AML transaction dataset...")
        df = generate_aml_dataset(num_samples=2500, save_path=data_path)
    else:
        df = pd.read_csv(data_path)

    print(f"Loaded {len(df)} transactions. Preparing features...")
    y = df['is_suspicious'].values
    
    # Feature extraction & scaling
    X_scaled, scaler, cust_avg_map, feature_names = preprocess_and_feature_engineering(df, is_training=True)

    # Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, class_weight='balanced')
    rf_model.fit(X_train, y_train)

    # Predictions & Evaluation for RF
    y_pred_rf = rf_model.predict(X_test)
    y_prob_rf = rf_model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred_rf)
    prec = precision_score(y_test, y_pred_rf, zero_division=0)
    rec = recall_score(y_test, y_pred_rf, zero_division=0)
    f1 = f1_score(y_test, y_pred_rf, zero_division=0)
    auc = roc_auc_score(y_test, y_prob_rf)
    cm = confusion_matrix(y_test, y_pred_rf)

    print("\n--- RANDOM FOREST CLASSIFIER EVALUATION ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {auc:.4f}")
    print(f"Confusion Matrix:\n{cm}\n")

    print("Training Isolation Forest Anomaly Detector...")
    # Contamination approximate ~15%
    iso_model = IsolationForest(n_estimators=100, contamination=0.15, random_state=42)
    iso_model.fit(X_scaled)

    # Save artifacts
    joblib.dump(rf_model, os.path.join(model_dir, 'aml_model.pkl'))
    joblib.dump(iso_model, os.path.join(model_dir, 'anomaly_model.pkl'))
    joblib.dump(scaler, os.path.join(model_dir, 'scaler.pkl'))
    joblib.dump({'feature_names': feature_names, 'cust_avg_map': cust_avg_map}, os.path.join(model_dir, 'features.pkl'))

    print("Models and scalers saved successfully to models/ directory.")

    return {
        'accuracy': float(acc),
        'precision': float(prec),
        'recall': float(rec),
        'f1_score': float(f1),
        'roc_auc': float(auc)
    }

if __name__ == '__main__':
    train_and_evaluate_models()
