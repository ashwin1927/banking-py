from flask import *
import pickle
import os
import datetime

app = Flask(__name__)
app.secret_key = 'ashwin'
accounts_file = 'accounts.dat'
log_file = 'change_logs.txt'
admin_credentials = {'admin': 'admin123'}

# Function to handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Load accounts from file
def load_accounts():
    if os.path.exists(accounts_file):
        with open(accounts_file, 'rb') as file:
            return pickle.load(file)
    return {}

# Save accounts to file
def save_accounts(accounts):
    with open(accounts_file, 'wb') as file:
        pickle.dump(accounts, file)

# Log changes to accounts in user-specific log files
def log_change(action, owner, amount=None):
    # Ensure the logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    user_log_file = os.path.join('logs', f'{owner}_log.csv')
    
    # If the log file doesn't exist, create it and write the headers
    if not os.path.exists(user_log_file):
        with open(user_log_file, 'w') as file:
            file.write('Timestamp,Action,Amount\n')
    
    # Log the action
    with open(user_log_file, 'a') as file:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if amount is not None:
            log_entry = f"{timestamp},{action},${amount}\n"
        else:
            log_entry = f"{timestamp},{action},\n"
        file.write(log_entry)

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
            log_change('Created Account', owner, initial_deposit)
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
                    log_change('Deposit', owner, amount)
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
                        log_change('Withdrawal', owner, amount)
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
        password1 = request.form['password1']

        accounts = load_accounts()

        if owner in accounts:
            if accounts[owner]['password'] == password and accounts[owner]['password'] == password1:
                del accounts[owner]
                save_accounts(accounts)
                log_change('Deleted Account', owner)
                flash('Account deleted successfully.')
                return redirect(url_for('index'))
            else:
                flash('Incorrect password. Access denied.')
        else:
            flash('Account not found.')

    return render_template('delete.html')

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
        log_change('Admin Deleted Account', owner)
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
            old_balance = accounts[owner]['balance']
            accounts[owner]['balance'] = new_balance
            save_accounts(accounts)
            log_change('Admin Edited Balance', owner, new_balance - old_balance)
            flash(f'Account {owner} updated successfully.')

        return redirect(url_for('admin_dashboard'))

    if owner in accounts:
        account_info = accounts[owner]
        return render_template('admin_edit.html', owner=owner, account=account_info)
    else:
        flash('Account not found.')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/logs')
def view_logs():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    logs = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            for line in file:
                parts = line.strip().split(' - ')
                logs.append({
                    'timestamp': parts[0],
                    'action': ' - '.join(parts[1:])
                })
    return render_template('logs.html', logs=logs)

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

# Route to download user bank statements
@app.route('/download_statement/<owner>', methods=['GET'])
def download_statement(owner):
    user_log_file = os.path.join('logs', f'{owner}_log.csv')
    
    # Check if the user log file exists
    if os.path.exists(user_log_file):
        return send_file(user_log_file, as_attachment=True, download_name=f'{owner}_statement.csv', mimetype='text/csv')
    else:
        flash('No transaction history found for this account.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
