from flask import render_template, request, redirect, url_for, session
from app import app
import csv
import os
from datetime import datetime
import uuid

# Directory to store individual CSV files
DATA_DIR = "expense_data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_csv():
    """Get the CSV file path for the current user session."""
    user_id = session.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
    return os.path.join(DATA_DIR, f"{user_id}_expenses.csv")

def init_csv(file_path):
    """Ensure the CSV file exists and has a header."""
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Description", "Amount"])

@app.route('/', methods=['GET', 'POST'])
def index():
    csv_file = get_user_csv()
    init_csv(csv_file)

    if request.method == 'POST':
        budget = request.form['budget']
        session['budget'] = float(budget)
        return redirect(url_for('index'))

    expenses = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            expenses.append(row)

    total_spending = sum(float(expense["Amount"]) for expense in expenses)
    budget = session.get('budget', 0)
    allowed_spending = budget - total_spending

    return render_template('index.html', expenses=expenses, total_spending=total_spending, budget=budget, allowed_spending=allowed_spending)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    csv_file = get_user_csv()
    init_csv(csv_file)

    if request.method == 'POST':
        date = datetime.now().strftime("%Y-%m-%d")
        category = request.form['category']
        description = request.form['description']
        amount = request.form['amount']

        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, category, description, amount])

        return redirect(url_for('index'))

    return render_template('add_expense.html')
