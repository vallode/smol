import os
import sqlite3
import base64
import validators
from flask import Flask, request, session, g, redirect, \
    url_for, abort, \
    render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'smol.db'),
))
app.config.from_envvar('SMOL_SETTINGS', silent=True)


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


def encode(u):
    return str(base64.b64encode(bytes(str(u), 'UTF-8')), 'UTF-8')


def decode(u):
    return str(base64.b64decode(bytes(str(u), 'UTF-8')), 'UTF-8')


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('SMOL initialized the database.')


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/shorten', methods=['POST', 'GET'])
def shorten_link():
    if request.method == 'GET':
        return index()

    if not validators.url(request.form['original']):
        return render_template('base.html', error='Invalid link, please provide a valid URL')

    url = encode(request.form['original'])
    db = get_db()

    db.execute('INSERT INTO links (originalURL) VALUES (?)', [url])
    db.commit()
    cur = db.execute('SELECT last_insert_rowid()')

    cur_id = (cur.fetchone()[0])
    id_encoded = encode(cur_id)

    db.execute('UPDATE links SET encodedURL = (?) WHERE id = (?)', [id_encoded, cur_id])

    return render_template('base.html', link=id_encoded)


@app.route('/<link>', methods=['POST', 'GET'])
def reroute(link):
    db = get_db()
    link_id = decode(link)

    cur = db.execute('SELECT originalURL FROM links WHERE id = (?)', [link_id])

    URL = decode(cur.fetchone()[0])

    return redirect(URL)
