from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import sqlite3, json, os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'finanzas-kotly-secret-2024')

DB_PATH = os.environ.get('DATABASE_URL', 'finanzas.db')
USERNAME = 'kotly777'
PASSWORD = '@ndrade.8041'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) if '/' in DB_PATH else None
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS estado (
                id INTEGER PRIMARY KEY,
                saldos TEXT NOT NULL,
                pagos TEXT NOT NULL,
                usdt_amount REAL DEFAULT 274,
                trm_manual REAL DEFAULT 3475,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        if not conn.execute('SELECT id FROM estado WHERE id=1').fetchone():
            conn.execute('INSERT INTO estado (id,saldos,pagos) VALUES (1,?,?)', (
                json.dumps([
                    {"label":"Fisico","value":109500,"interes":0,"liquido":True},
                    {"label":"Nequi","value":321000,"interes":0,"liquido":True},
                    {"label":"Prestado mama","value":500000,"interes":10,"liquido":False},
                    {"label":"Prestado Carlos","value":500000,"interes":10,"liquido":False},
                ]),
                json.dumps([
                    {"label":"Cadena","value":100000,"fecha":""},
                    {"label":"Toga","value":35000,"fecha":""},
                ])
            ))
        conn.commit()

def login_required(f):
    @wraps(f)
    def d(*a,**k):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*a,**k)
    return d

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username')==USERNAME and request.form.get('password')==PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        error = 'Usuario o contrasena incorrectos.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    with get_db() as conn:
        row = conn.execute('SELECT * FROM estado WHERE id=1').fetchone()
    return render_template('index.html', data={
        'saldos':      json.loads(row['saldos']),
        'pagos':       json.loads(row['pagos']),
        'usdt_amount': row['usdt_amount'],
        'trm_manual':  row['trm_manual'],
        'updated_at':  row['updated_at'],
    })

@app.route('/api/save', methods=['POST'])
@login_required
def save():
    b = request.get_json()
    with get_db() as conn:
        conn.execute('''UPDATE estado SET saldos=?,pagos=?,usdt_amount=?,trm_manual=?,
            updated_at=CURRENT_TIMESTAMP WHERE id=1''',
            (json.dumps(b.get('saldos',[])), json.dumps(b.get('pagos',[])),
             b.get('usdt_amount',274), b.get('trm_manual',3475)))
        conn.commit()
    return jsonify({'ok':True})

@app.route('/api/load')
@login_required
def load():
    with get_db() as conn:
        row = conn.execute('SELECT * FROM estado WHERE id=1').fetchone()
    return jsonify({
        'saldos':json.loads(row['saldos']),'pagos':json.loads(row['pagos']),
        'usdt_amount':row['usdt_amount'],'trm_manual':row['trm_manual'],
        'updated_at':row['updated_at']
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=False)

init_db()
