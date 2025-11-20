from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

def load_data():
    if 'transactions' not in session:
        session['transactions'] = []
        session['budget'] = 1000.0
    return session['transactions'], session.get('budget', 1000.0)

def save_transaction(transaction):
    transactions, budget = load_data()
    transactions.append(transaction)
    session['transactions'] = transactions
    session.modified = True

def calculate_balance():
    transactions, budget = load_data()
    balance = budget
    for trans in transactions:
        if trans['type'] == 'income':
            balance += trans['amount']
        else:
            balance -= trans['amount']
    return balance

def get_pet_mood():
    transactions, budget = load_data()
    balance = calculate_balance()
    
    if not transactions:
        return 'happy', 'Your pet is waiting for you to start budgeting!'
    
    total_spent = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    
    savings_rate = 0
    if total_income > 0:
        savings_rate = ((total_income - total_spent) / total_income) * 100
    
    if balance < 0:
        return 'sad', 'Oh no! You\'re in debt. Your pet is worried!'
    elif savings_rate > 50:
        return 'excited', 'Wow! You\'re saving so much! Your pet is thrilled!'
    elif savings_rate > 20:
        return 'happy', 'Great job! Your pet is happy with your savings!'
    elif total_spent > total_income:
        return 'concerned', 'Your pet is a bit concerned about your spending...'
    else:
        return 'neutral', 'Your pet is watching your budget.'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    transactions, budget = load_data()
    balance = calculate_balance()
    mood, message = get_pet_mood()
    
    return jsonify({
        'transactions': transactions,
        'balance': balance,
        'budget': budget,
        'pet': {
            'mood': mood,
            'message': message
        }
    })

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json or {}
    
    transaction = {
        'id': len(session.get('transactions', [])) + 1,
        'type': data.get('type', 'expense'),
        'amount': float(data.get('amount', 0)),
        'category': data.get('category', ''),
        'description': data.get('description', ''),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    save_transaction(transaction)
    
    transactions, budget = load_data()
    balance = calculate_balance()
    mood, message = get_pet_mood()
    
    return jsonify({
        'success': True,
        'transactions': transactions,
        'balance': balance,
        'budget': budget,
        'pet': {
            'mood': mood,
            'message': message
        }
    })

@app.route('/api/budget', methods=['POST'])
def update_budget():
    data = request.json or {}
    session['budget'] = float(data.get('budget', 1000))
    session.modified = True
    
    transactions, budget = load_data()
    balance = calculate_balance()
    mood, message = get_pet_mood()
    
    return jsonify({
        'success': True,
        'transactions': transactions,
        'budget': budget,
        'balance': balance,
        'pet': {
            'mood': mood,
            'message': message
        }
    })

@app.route('/api/reset', methods=['POST'])
def reset_data():
    session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    is_dev = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=is_dev)
