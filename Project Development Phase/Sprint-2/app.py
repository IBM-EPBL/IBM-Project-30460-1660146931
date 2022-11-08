from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import re


app = Flask(__name__)
app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=31321;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=scg10921;PWD=hBxJTYvcqDKSpHib;",'','')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'Name' in request.form and 'Password' in request.form and 'Email' in request.form :
        username = request.form['Name']
        password = request.form['Password']
        email = request.form['Email']
        stmt = ibm_db.prepare(conn,'SELECT * FROM users WHERE name = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            prep_stmt = ibm_db.prepare(conn,"INSERT INTO users(name , email,password) VALUES(?, ?, ?)")
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
    
        return render_template('register.html', msg = msg)
    return render_template('register.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'Name' in request.form and 'Password' in request.form:
        username = request.form['Name']
        password = request.form['Password']
        stmt = ibm_db.prepare(conn,'SELECT * FROM users WHERE name = ? AND password = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['loggedin'] = True
            session['name'] = account['NAME']
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username / password !'
            return render_template('login.html', a = msg)
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

    
@app.route('/add', methods =['GET','POST'])
def add():
    if request.method == "POST" and 'paymode'  in request.form and 'expensename'  in request.form and 'expensename'  in request.form and 'category' in request.form and 'amount'  in request.form:
        if 'id' in session:
            uid = session['id']
            paymode = request.form['paymode']
            expensename = request.form['expensename'] 
            expensedate = request.form['expensedate'] 
            category = request.form['category']
            amount = request.form['amount']
            stmt = ibm_db.prepare(conn,'SELECT * FROM users WHERE id = ?')
            ibm_db.bind_param(stmt,1,uid)
            ibm_db.execute(stmt)
            ibm_db.fetch_assoc(stmt)
            prep_stmt = ibm_db.prepare(conn,'INSERT INTO expense(uid, paymode, expensename, expensedate, category, amount) VALUES (?, ?, ?, ?, ? ,?)')
            ibm_db.bind_param(prep_stmt, 1, uid)
            ibm_db.bind_param(prep_stmt, 2, paymode)
            ibm_db.bind_param(prep_stmt, 3, expensename)
            ibm_db.bind_param(prep_stmt, 4, expensedate)
            ibm_db.bind_param(prep_stmt, 5, category)
            ibm_db.bind_param(prep_stmt, 6, amount)
            ibm_db.execute(prep_stmt)
        msg = 'Your expense has been sucessfully added'
        return render_template('add.html', a = msg )   
    return render_template('add.html')        


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('Name', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8080)
