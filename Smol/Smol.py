import os
import sqlite3
import base64
import validators
from flask import Flask, request, session, g, redirect, \
    url_for, abort, \
    render_template, flash


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('SMOL_SETTINGS', silent=True)

DATABASE = os.path.join(app.root_path, 'smol.db')


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


@app.teardown_appcontext
def close_db(exception):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def init_db_command():
    init_db()
    print('Initialized the database.')


def encode(u):
    return str(base64.b64encode(bytes(str(u), 'UTF-8')), 'UTF-8')


def decode(u):
    return str(base64.b64decode(bytes(str(u), 'UTF-8')), 'UTF-8')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('base.html')

    if request.method == 'POST':

        if not validators.url(request.form['original']):
            return render_template('base.html', error='Invalid link, please provide a valid URL')

        if 'www.smol.link' in request.form['original']:
            return render_template('base.html', error='We do not shorten our own links :)')

        with get_db() as conn:
            cursor = conn.cursor()
            query = cursor.execute('INSERT INTO links (originalURL) VALUES (?)',
                                   [encode(request.form['original'])])
        id_encoded = encode(query.lastrowid)

        return render_template('base.html', link=id_encoded)

    return render_template('base.html')


@app.route('/<link>', methods=['POST', 'GET'])
def reroute(link):
    with get_db() as conn:
        cursor = conn.cursor()

        try:
            query = cursor.execute('SELECT originalURL FROM links WHERE id = (?)',
                                   [decode(link)])
            link = decode(query.fetchone()[0])
            return redirect(link)

        except:
            return render_template('base.html')
