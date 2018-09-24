# -*- coding: utf-8 -*-
"""smol.link

Smol.link is a tiny url shortener written for personal and limited outside use.
"""

import base64
import logging
import os
import psycopg2
from flask import Flask, render_template, request, send_from_directory, abort, Response, redirect

APP = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


def get_db():
    """Connects to the configured database

    Returns:
        Psycopg2 database connection object
    """
    try:
        conn = psycopg2.connect("dbname=smol host=localhost user=smol password=smol")
    except psycopg2.Error:
        return abort(Response("500: We screwed up"))

    logging.debug("Connection to db established: %s", conn)
    return conn


def close_db(database):
    """Commits changes and closes a database connection"""
    database.commit()
    logging.debug("Connection to db closed: %s", database)
    database.close()


def b64_encode(data):
    """Encodes string to UTF-8 and converts to Base64

    Args:
        data (str): String to encode

    Returns:
        (str): A base64 encoded string
    """
    return base64.urlsafe_b64encode(data.encode())


def b64_decode(data):
    """Decodes string from Base64

    Args:
        data (str): String to decode

    Returns:
        (str): A decoded string
    """
    return base64.urlsafe_b64decode(data)


@APP.route('/', methods=['get', 'post'])
def index():
    """Handles the serving of the index page as well as shortening links in the form

    Returns:
        200: Renders the index page, if a form with a link was submitted, it returns
        the index page populated by the shortened link
    """
    if request.form:
        logging.debug("Link requested: %s", request.form['link'])
        link = b64_encode(request.form['link']).decode()

        db = get_db()
        cur = db.cursor()

        cur.execute("INSERT INTO links (original) VALUES (%s) RETURNING id", (link, ))
        link = request.url + str(b64_encode(str(cur.fetchone()[0])), 'UTF-8')

        cur.close()
        close_db(db)

        return render_template('index.html', link=link)

    return render_template('index.html')


@APP.route('/<link_id>')
def short(link_id):
    """Redirects a successful database match to its stored link

    Args:
        link_id (str): Base64 encoded string to match against in the database

    Returns:
        200: Redirection to the related link

        302: Renders the index page with an error
    """
    logging.debug("Link id: %s", link_id)

    link = b64_decode(link_id).decode()

    logging.debug("Link decoded: %s", link)

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT original FROM links WHERE id = (%s)", (link, ))
    original = str(b64_decode(cur.fetchone()[0]).decode())

    cur.close()
    close_db(db)

    logging.debug("Outgoing link: %s", original)

    return redirect(original)


@APP.route('/favicon.ico')
def favicon():
    """Returns the favicon for the site

    Returns:
        favicon.ico
    """
    return send_from_directory(os.path.join(APP.root_path, 'static'), 'favicon.ico')
