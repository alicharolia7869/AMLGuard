# AMLGuard — AI-Powered Anti-Money Laundering & Suspicious Transaction Detection Platform

![AMLGuard Banner](https://img.shields.io/badge/AMLGuard-AI--Security-06B6D4?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Random%20Forest%20%2B%20Isolation%20Forest-F7931E?style=for-the-badge&logo=scikit-learn)
![SQLite/MySQL](https://img.shields.io/badge/Database-SQLite%2FMySQL-4479A1?style=for-the-badge&logo=sqlite)

---

## 🚀 Overview

**AMLGuard** is an end-to-end, enterprise-grade AI platform designed for compliance officers, fraud analysts, and financial crime investigators. It continuously ingests financial transaction streams, cleanses data, applies hybrid **Machine Learning + Custom Rule Engines**, generates normalized **0–100 risk scores**, provides explainable risk breakdowns (SHAP-like), maps multi-hop account network topologies, and generates regulatory-compliant **Suspicious Activity Reports (SAR)**.

---

## 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │ Transaction Data │
                    │ CSV / Database   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Data Preprocessor│
                    │ Cleaning + FE    │
                    └────────┬─────────┘
                             ↓
              ┌──────────────┴──────────────┐
              ↓                             ↓
       ┌──────────────┐              ┌──────────────┐
       │ Rule Engine  │              │ ML Detection │
       │              │              │              │
       │ AML Rules    │              │ RandomForest │
       │ Thresholds   │              │ Isolation    │
       └──────┬───────┘              │ Forest       │
              │                      └──────┬───────┘
              └──────────────┬──────────────┘
                             ↓
                    ┌──────────────────┐
                    │ Risk Score Engine│
                    │    0 → 100       │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Alert Stream     │
                    └────────┬─────────┘
                             ↓
              ┌──────────────┴──────────────┐
              ↓                             ↓
      ┌───────────────┐             ┌───────────────┐
      │ AML Dashboard │             │ Investigation │
      │               │             │ Cockpit & SAR │
      └───────────────┘             └───────────────┘
```

---

## 🧠 Risk Scoring Model

The risk engine computes a normalized score between **0 and 100** by combining four distinct risk factors:

| Risk Factor | Max Points | Description |
| :--- | :---: | :--- |
| **Random Forest ML Probability** | 40 | Supervised classifier prediction probability |
| **Isolation Forest Anomaly Score** | 25 | Unsupervised anomaly severity |
| **AML Rule Violations** | 20 | Heuristic rules (Smurfing, off-hours, velocity, geo) |
| **Behavioral Ratio Deviation** | 15 | Ratio of transfer amount to historical average |

### Risk Tiers
- 🟢 **LOW**: `0 – 30`
- 🟡 **MEDIUM**: `31 – 60`
- 🟠 **HIGH**: `61 – 80`
- 🔴 **CRITICAL**: `81 – 100`

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed

### 2. Installation & Setup
```bash
# Clone repository
git clone https://github.com/alicharolia7869/AMLGuard.git
cd AMLGuard

# Install dependencies
pip install -r requirements.txt
```

### 3. Run ML Pipeline & Train Models
```powershell
# In Windows PowerShell:
& "C:\Users\ALI SHAFIQUE\venv\Scripts\python.exe" ml/train_model.py

# Or with virtual environment activated:
python ml/train_model.py
```

### 4. Launch Web Platform
```powershell
# In Windows PowerShell:
& "C:\Users\ALI SHAFIQUE\venv\Scripts\python.exe" app.py

# Or with virtual environment activated:
python app.py
```
Open **http://127.0.0.1:5000** in your web browser.

---

## 🔑 Demo Login Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin@amlguard.io` | `admin123` |
| **Investigator** | `investigator@amlguard.io` | `investigator123` |

---

## 📂 Project Directory Structure

```text
AMLGuard/
├── app.py                     # Main Flask application entrypoint
├── config.py                  # Application configuration settings
├── requirements.txt           # Python dependency list
├── README.md                  # Project documentation
│
├── data/                      # Dataset directories
│   ├── raw/                   # Raw transactions CSV
│   └── uploads/               # User CSV upload staging
│
├── database/                  # Database models & SQL schema
│   ├── schema.sql             # MySQL & SQLite schema definition
│   └── models.py              # SQLAlchemy ORM models
│
├── ml/                        # Machine Learning Pipeline
│   ├── generate_dataset.py    # Synthetic AML transaction dataset generator
│   ├── preprocessing.py       # Data cleaning & feature extraction
│   ├── train_model.py         # Model training & metrics evaluator
│   └── predict.py             # Inference engine
│
├── engine/                    # Risk Engine Core
│   ├── rule_engine.py         # Configurable AML rules
│   └── risk_engine.py         # 0-100 Risk Scoring engine
│
├── models/                    # Binary model artifacts (.pkl)
│   ├── aml_model.pkl          # Random Forest Classifier
│   ├── anomaly_model.pkl      # Isolation Forest
│   └── scaler.pkl             # StandardScaler
│
├── routes/                    # Flask Blueprints
│   ├── auth.py                # Authentication & Session Management
│   ├── dashboard.py           # Dashboard statistics & recent alerts
│   ├── transactions.py        # Transaction table, search, CSV upload
│   ├── alerts.py              # Alert queue & severity filters
│   ├── customers.py           # Customer entity profiles
│   ├── investigations.py      # Investigation cockpit & SAR PDF exporter
│   ├── network.py             # Interactive account relationship graph
│   └── analytics.py           # Plotly analytics API
│
├── templates/                 # Jinja2 Dark Theme UI Templates
└── static/                    # Dark Financial Security CSS & JS
```

---

## 📄 License
This project is licensed under the MIT License.
