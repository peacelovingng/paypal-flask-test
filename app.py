import paypalrestsdk
import json
from paypalrestsdk import BillingPlan, BillingAgreement
from datetime import datetime, timedelta
from flask import Flask, Response, request, url_for

app = Flask(__name__)

paypalrestsdk.configure({
    "mode": 'sandbox',
    "client_id": '',
    "client_secret": ''
})

@app.route('/billing-plans')
def billing_plans():
    plans = paypalrestsdk.BillingPlan.all({"status":"ALL",
        "page_size": "10",
        "page": "0",
        "total_required": "yes",
        "sort_order": "DESC"})
    all_plans = plans.to_dict()
    return Response(json.dumps(all_plans), mimetype='application/json')

@app.route('/activate')
def activate_plan():
    billing_plan = BillingPlan.find('P-3NF352338H658800LZS4KMVY')
    if billing_plan.activate():
        return "Billing Plan [%s] activated successfully" % billing_plan.id
    else:
        return billing_plan.error

@app.route('/create')
def create_plan():
    return 'done'
    billing_plan_attributes = {
        "name": 'Haliya Publishing - Monthly',
        "description": 'Monthly Subscription',
        "merchant_preferences": {
            "auto_bill_amount": "yes",
            "cancel_url": "http://www.cancel.com",
            "initial_fail_amount_action": "continue",
            "max_fail_attempts": "1",
            "return_url": "http://127.0.0.1:5000/billing-plans",
            "setup_fee": {
                "currency": "USD",
                "value": "10"
            }
        },
        "payment_definitions": [
            {
                "amount": {
                    "currency": "USD",
                    "value": "10"
                },
                "cycles": 0, # Infinite
                "frequency": "DAY",
                "frequency_interval": "1",
                "name": "MONTHLY",
                "type": "REGULAR"
            }
        ],
        "type": "INFINITE"
    }
    billing_plan = BillingPlan(billing_plan_attributes)
    if billing_plan.create():
        return (
            "Billing Plan [%s] created successfully" % (billing_plan.id))

@app.route('/subscribe')
def subscribe():
    billing_agreement = BillingAgreement({
        "name": "Organization plan name",
        "description": "Agreement for <Monthly Plan>",
        "start_date": (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "plan": {
            "id": "P-3NF352338H658800LZS4KMVY"
        },
        "payer": {
            "payment_method": "paypal"
        },
        "shipping_address": {
            "line1": "StayBr111idge Suites",
            "line2": "Cro12ok Street",
            "city": "San Jose",
            "state": "CA",
            "postal_code": "95112",
            "country_code": "US"
        }
    })
    if billing_agreement.create():
        for link in billing_agreement.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return approval_url
    else:
        return billing_agreement.error

@app.route("/agreement-details")
def agreement_details():
    billing_agreement = BillingAgreement.find(request.args.get('id', ''))
    return Response(json.dumps(billing_agreement.to_dict()), mimetype='application/json')

@app.route('/execute')
def execute_agreement():
    payment_token = request.args.get('token', '')
    billing_agreement_response = BillingAgreement.execute(payment_token)
    return (url_for('agreement_details', id=billing_agreement_response.id))
    return 'execute'
