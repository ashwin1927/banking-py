from flask import *
import pickle
import os

app = Flask(__name__)
app.secret_key = 'ashwin'
accounts_file = 'accounts.dat'

def load_accounts():
    if os.path.exists(accounts_file):
        with open(accounts_file, 'rb') as file:
            return pickle.load(file)
    return {}

def save_accounts(accounts):
    with open(accounts_file, 'wb') as file:
        pickle.dump(accounts, file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        owner = request.form['owner']
        password = request.form['password']
        initial_deposit = float(request.form['initial_deposit'])

        accounts = load_accounts()

        if owner in accounts:
            flash('Account already exists.')
        else:
            accounts[owner] = {'password': password, 'balance': initial_deposit}
            save_accounts(accounts)
            flash(f'Account created for {owner} with initial deposit of ${initial_deposit}')

        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        owner = request.form['owner']
        password = request.form['password']
        amount = float(request.form['amount'])

        accounts = load_accounts()

        if owner in accounts:
            if accounts[owner]['password'] == password:
                if amount > 0:
                    accounts[owner]['balance'] += amount
                    save_accounts(accounts)
                    flash(f'Deposit successful! New balance: ${accounts[owner]["balance"]}')
                else:
                    flash('Deposit amount must be positive.')
            else:
                flash('Incorrect password. Access denied.')
        else:
            flash('Account not found.')

        return redirect(url_for('index'))

    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        owner = request.form['owner']
        password = request.form['password']
        amount = float(request.form['amount'])

        accounts = load_accounts()

        if owner in accounts:
            if accounts[owner]['password'] == password:
                if amount > 0:
                    if amount <= accounts[owner]['balance']:
                        accounts[owner]['balance'] -= amount
                        save_accounts(accounts)
                        flash(f'Withdrawal successful! New balance: ${accounts[owner]["balance"]}')
                    else:
                        flash('Insufficient funds.')
                else:
                    flash('Withdrawal amount must be positive.')
            else:
                flash('Incorrect password. Access denied.')
        else:
            flash('Account not found.')

        return redirect(url_for('index'))

    return render_template('withdraw.html')

@app.route('/balance', methods=['GET', 'POST'])
def check_balance():
    if request.method == 'POST':
        owner = request.form['owner']

        accounts = load_accounts()

        if owner in accounts:
            balance = accounts[owner]['balance']
            return render_template('balance.html', owner=owner, balance=balance)
        else:
            flash('Account not found.')

        return redirect(url_for('index'))

    return render_template('balance.html', owner=None, balance=None)


app.run(debug=True)