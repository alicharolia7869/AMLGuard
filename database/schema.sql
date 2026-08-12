-- AMLGuard Database Schema Definition
-- Compatible with MySQL and SQLite

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'investigator', -- 'admin', 'investigator'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    account_number VARCHAR(30) UNIQUE NOT NULL,
    account_type VARCHAR(20) DEFAULT 'Savings',
    account_age_months INTEGER DEFAULT 12,
    avg_monthly_income DECIMAL(15,2) DEFAULT 50000.00,
    risk_level VARCHAR(20) DEFAULT 'LOW', -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    country VARCHAR(50) DEFAULT 'India',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    sender_account VARCHAR(30) NOT NULL,
    receiver_account VARCHAR(30) NOT NULL,
    sender_name VARCHAR(100),
    receiver_name VARCHAR(100),
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(30) DEFAULT 'TRANSFER', -- 'TRANSFER', 'WIRE', 'CASH_DEPOSIT', 'ATM'
    transaction_time DATETIME NOT NULL,
    location VARCHAR(100) DEFAULT 'Mumbai, IN',
    status VARCHAR(30) DEFAULT 'COMPLETED',
    risk_score INTEGER DEFAULT 0,
    ml_prediction FLOAT DEFAULT 0.0,
    anomaly_score FLOAT DEFAULT 0.0,
    rule_score INTEGER DEFAULT 0,
    risk_tier VARCHAR(20) DEFAULT 'LOW', -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id VARCHAR(50) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    reasons TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'PENDING', -- 'PENDING', 'UNDER_REVIEW', 'ESCALATED', 'CLEARED'
    assigned_to VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS investigations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id VARCHAR(50) NOT NULL,
    investigator VARCHAR(100) NOT NULL,
    decision VARCHAR(50) NOT NULL, -- 'UNDER_REVIEW', 'ESCALATED_SAR', 'CLEARED', 'REJECTED'
    comments TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code VARCHAR(30) UNIQUE NOT NULL,
    rule_name VARCHAR(100) NOT NULL,
    description TEXT,
    points INTEGER DEFAULT 15,
    is_active BOOLEAN DEFAULT 1
);
