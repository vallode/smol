import os
import sqlite3
import base64
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'smol.db'),
    SECRET_KEY='rainbows',
))
app.config.from_envvar('SMOL_SETTINGS', silent=True)

#DB setup

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
    print('SMOL initialized the database.')

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Routes

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/shorten', methods=['POST'])
def shorten_link():
    urlEncoded = base64.b64encode(bytes(str(request.form['original']), 'UTF-8'))
    db = get_db()

    db.execute('INSERT INTO links (originalURL) VALUES (?)' ,
                [ urlEncoded ])
    db.commit()

    cur = db.execute('SELECT id FROM links WHERE originalURL = (?)',
                    [ urlEncoded ])
    urlId = cur.fetchone()[0]

    db.execute('UPDATE links SET encodedURL = (?) WHERE originalURL = (?)' ,
                [ base64.urlsafe_b64encode(bytes(str(urlId), 'UTF-8')) , urlEncoded ])

    encodedLink = str(base64.urlsafe_b64encode(bytes(str(urlId), 'UTF-8')), 'UTF-8')

    return render_template('layout.html', link=encodedLink)

@app.route('/s/<url>', methods=['POST', 'GET'])
def reroute(url):
    db = get_db()
    decodedLink = str(base64.urlsafe_b64decode(url), 'UTF-8')

    cur = db.execute('SELECT originalURL FROM links WHERE id = (?)',
                    [ decodedLink ])

    urlId = str(cur.fetchone()[0], 'UTF-8')

    link = base64.b64decode(bytes(str(urlId), 'UTF-8'))

    return redirect(url_for(link))