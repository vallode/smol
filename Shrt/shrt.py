import os
import sqlite3
import base64
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask('Shrt')
app.config.from_object('Shrt')

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'shrt.db'),
    SECRET_KEY='poniesonrainbows',
))
app.config.from_envvar('SHRT_SETTINGS', silent=True)

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/shorten', methods=['POST'])
def shorten_link():
    db = get_db()
    db.execute('INSERT INTO links (originalURL) VALUES (?)',
                [base64.b64encode(request.form['original']) ])
    db.commit()
    cur = db.execute('SELECT id FROM links WHERE originalURL = (?)',
                    [base64.b64encode(request.form['original'])])
    link = cur.fetchone()
    return render_template('layout.html', link=link[0])

@app.route('/short/<int:short>', methods=['POST', 'GET'])
def reroute(short):
    db = get_db()
    cur = db.execute('SELECT originalURL FROM links WHERE id = (?)',
                    [short])
    link = cur.fetchone()
    link = base64.b64decode(link[0])
    return redirect(link)