from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, admin_required
from database.models import db, Rule

rules_bp = Blueprint('rules', __name__)

@rules_bp.route('/rules')
@login_required
def list_rules():
    # Fetch rules from DB or seed defaults
    rules = Rule.query.order_by(Rule.id.asc()).all()
    
    if not rules:
        # Seed default rules
        default_rules = [
            {'code': 'RULE_01', 'name': '10x Average Amount Spike', 'points': 20, 'desc': 'Transaction amount exceeds 10 times customer normal historical average.'},
            {'code': 'RULE_02', 'name': 'Smurfing / Structuring Detection', 'points': 20, 'desc': 'Amount is structured just below regulatory reporting thresholds (₹9,000–₹9,999).'},
            {'code': 'RULE_03', 'name': 'Unusual Night Off-Hours', 'points': 10, 'desc': 'Transaction initiated between 1:00 AM and 4:00 AM off-peak hours.'},
            {'code': 'RULE_04', 'name': 'New Beneficiary Large Wire', 'points': 15, 'desc': 'First-time transfer to new unverified beneficiary exceeding ₹50,000.'},
            {'code': 'RULE_05', 'name': 'High-Risk Geo Jurisdiction', 'points': 15, 'desc': 'Transaction involves high-risk or secrecy jurisdiction location (Panama, Cayman, Cyprus).'},
            {'code': 'RULE_06', 'name': 'Rapid Velocity Spike', 'points': 15, 'desc': 'Multiple rapid transactions detected from sender account within short time window.'}
        ]
        for r in default_rules:
            rule_obj = Rule(rule_code=r['code'], rule_name=r['name'], points=r['points'], description=r['desc'], is_active=True)
            db.session.add(rule_obj)
        db.session.commit()
        rules = Rule.query.order_by(Rule.id.asc()).all()

    return render_template('rules.html', rules=rules)

@rules_bp.route('/rules/<int:rule_id>/toggle', methods=['POST'])
@login_required
def toggle_rule(rule_id):
    rule = db.get_or_404(Rule, rule_id)
    rule.is_active = not rule.is_active
    db.session.commit()
    status_str = "Activated" if rule.is_active else "Deactivated"
    flash(f"Rule '{rule.rule_name}' has been {status_str}.", "info")
    return redirect(url_for('rules.list_rules'))

@rules_bp.route('/rules/add', methods=['POST'])
@login_required
def add_rule():
    rule_code = request.form.get('rule_code', '').strip().upper()
    rule_name = request.form.get('rule_name', '').strip()
    points = request.form.get('points', 15, type=int)
    description = request.form.get('description', '').strip()

    if not rule_code or not rule_name:
        flash("Rule code and name are required.", "danger")
        return redirect(url_for('rules.list_rules'))

    existing = Rule.query.filter_by(rule_code=rule_code).first()
    if existing:
        flash(f"Rule code '{rule_code}' already exists.", "danger")
        return redirect(url_for('rules.list_rules'))

    new_rule = Rule(rule_code=rule_code, rule_name=rule_name, points=points, description=description, is_active=True)
    db.session.add(new_rule)
    db.session.commit()

    flash(f"New rule '{rule_name}' added successfully!", "success")
    return redirect(url_for('rules.list_rules'))
