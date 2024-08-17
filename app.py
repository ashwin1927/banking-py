from flask import *
import pickle
import os

app = Flask(__name__)
app.secret_key = 'ashwin'
accounts_file = 'accounts.bin'

admin_credentials = {'admin': 'admin123'}

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

# Client Side Routes
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

@app.route('/delete', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        owner = request.form['owner']
        password = request.form['password']

        accounts = load_accounts()

        if owner in accounts:
            if accounts[owner]['password'] == password:
                del accounts[owner]
                save_accounts(accounts)
                flash('Account deleted successfully.')
                return redirect(url_for('index'))
            else:
                flash('Incorrect password. Access denied.')
        else:
            flash('Account not found.')

    return render_template('delete.html')

# Admin Side Routes
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in admin_credentials and admin_credentials[username] == password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.')

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    accounts = load_accounts()
    return render_template('admin_dashboard.html', accounts=accounts)

@app.route('/admin/delete/<owner>', methods=['POST'])
def admin_delete_account(owner):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    accounts = load_accounts()
    if owner in accounts:
        del accounts[owner]
        save_accounts(accounts)
        flash(f'Account {owner} has been deleted.')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit/<owner>', methods=['GET', 'POST'])
def admin_edit_account(owner):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    accounts = load_accounts()

    if request.method == 'POST':
        new_balance = float(request.form['new_balance'])

        if owner in accounts:
            accounts[owner]['balance'] = new_balance
            save_accounts(accounts)
            flash(f'Account {owner} updated successfully.')

        return redirect(url_for('admin_dashboard'))

    if owner in accounts:
        account_info = accounts[owner]
        return render_template('admin_edit.html', owner=owner, account=account_info)
    else:
        flash('Account not found.')
        return redirect(url_for('admin_dashboard'))
    
@app.route('/client')
def client_dashboard():
    return render_template('client_dashboard.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
