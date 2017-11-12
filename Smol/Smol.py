import os
import sqlite3
import base64
from flask import Flask, request, session, g, redirect, \
    url_for, abort, \
    render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'smol.db'),
    SECRET_KEY='rainbows',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('SMOL_SETTINGS', silent=True)


# DB setup


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


# URL check


def checkURL(url):
    if url.startswith('http://') == 0 and url.startswith('https://') == 0:
        url = 'http://' + url

    return url


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('SMOL initialized the database.')


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# Routes


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('base.html')


@app.route('/shorten', methods=['POST'])
def shorten_link():
    url = checkURL(request.form['original'])
    urlEncoded = str(base64.b64encode(bytes(str(url), 'UTF-8')), 'UTF-8')
    db = get_db()

    db.execute('INSERT INTO links (originalURL) VALUES (?)', [urlEncoded])
    db.commit()
    cur = db.execute('SELECT last_insert_rowid()')

    curId = (cur.fetchone()[0])
    idEncoded = str(base64.urlsafe_b64encode(bytes(str(curId), 'UTF-8')), 'UTF-8')

    db.execute('UPDATE links SET encodedURL = (?) WHERE id = (?)', [idEncoded, curId])

    return render_template('base.html', link=idEncoded)


@app.route('/s/<path:url>', methods=['POST', 'GET'])
def reroute(url):
    db = get_db()
    idDecoded = str(base64.urlsafe_b64decode(url), 'UTF-8')

    cur = db.execute('SELECT originalURL FROM links WHERE id = (?)', [idDecoded])

    curId = (cur.fetchone()[0])

    link = str(base64.b64decode(bytes(curId, 'UTF-8')), 'UTF-8')

    return redirect(link)