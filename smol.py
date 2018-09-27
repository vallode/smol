# -*- coding: utf-8 -*-
"""smol.link

Smol.link is a tiny url shortener written for personal and limited outside use.
"""

import base64
import logging
import os
import psycopg2
import requests
import config
from flask import Flask, render_template, request, send_from_directory, abort, Response, redirect

APP = Flask(__name__)
APP.config.from_object(config.DevelopmentConfig)

logging.basicConfig(level=APP.config['LOGGING'])


def get_db():
    """Connects to the configured database

    Returns:
        Psycopg2 database connection object
    """
    try:
        conn = psycopg2.connect("dbname=smol host=localhost user=smol password=smol")
    except psycopg2.Error:
        return abort(500, "Something on our servers went wrong")

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


def validate_link(link):
    """Checks to ensure link is valid

    First checks for 'smol.link' existing in link, to avoid recursive links.
    Attempts to ping the link, if the request is successful passes on. The
    request is on a short timeout to avoid waiting for non-existent sites.

    Args:
        link (str): User specified string to be shortened

    Returns:
        True: If the link is valid and does not lead to the website itself

        False: If link fails a single check
    """
    if link == "":
        logging.debug("Link empty, failing")
        return False

    if "smol.link" in link:
        logging.debug("Smol.link appears in link, rejecting")
        return False

    try:
        logging.debug("Requesting link")
        ping = requests.get(link, timeout=2)
    except:
        logging.debug("Link does not exist")
        return False

    if ping.status_code != 200:
        logging.debug("Link did not respond with 200")
        return False

    logging.debug("Link successfully passed tests")
    return True


@APP.route('/', methods=['get', 'post'])
def index():
    """Handles the serving of the index page as well as shortening links in the form

    Returns:
        200: Renders the index page, if a form with a link was submitted, it returns
        the index page populated by the shortened link
    """
    if request.form:
        logging.debug("Link requested: %s", request.form['link'])
        logging.debug("Checking link")

        if not validate_link(request.form['link']):
            return render_template('index.html')

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

    try:
        link = b64_decode(link_id).decode()
    except UnicodeDecodeError:
        return abort(400, "Please check your link")

    logging.debug("Link decoded: %s", link)

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("SELECT original FROM links WHERE id = (%s)", (link, ))
    except psycopg2.DatabaseError:
        return abort(404, "Link does not exist")

    original = str(b64_decode(cur.fetchone()[0]).decode())

    cur.close()
    close_db(db)

    logging.debug("Outgoing link: %s", original)

    return redirect(original)


@APP.errorhandler(500)
def error500(error):
    """Handles serving 500 error pages"""
    logging.critical("500 error")
    return render_template("error.html", message=error.description), 500


@APP.errorhandler(400)
def error500(error):
    """Handles serving 400 error pages"""
    return render_template("error.html", message=error.description), 400


@APP.errorhandler(404)
def error500(error):
    """Handles serving 404 error pages"""
    return render_template("error.html", message=error.description), 404
