#!/usr/bin/env python

"""
Web service for SPLURGE recommendation engine
"""
import sys
import os

# TODO: perhaps should be using
# Request.environ to access env variables

sys.path.append(os.environ['SPLURGE_ROOT_APP_PATH'] + 'bin/')
import splurge
RECOMMENDER = splurge.Splurge(
    os.path.join(os.environ['SPLURGE_ROOT_APP_PATH'], 'data/'),
    os.path.join(os.environ['SPLURGE_ROOT_APP_PATH'], 'logs/'),
    'splurge', 'splurge_user', os.environ['SPLURGE_DB_PASSWORD'], '127.0.0.1', '5432',
)

from flask import Flask, jsonify

APP = Flask(__name__)
#APP.config.from_pyfile('splurge_production.conf')
APP.config.from_pyfile('splurge.conf')

APP.debug = True

@APP.route("/splurge_service/")
def hello():
    "Basic facts about the service"
    out = """<html>
    <head><title>SPLURGE Help</title></head><body><h1>Welcome to Splurge!</h1>
    <h3>SPLURGE is the Scholars Portal Library Usage-based Recommendation Engine</h3>
    <p><b>URL format:</b> /splurge/&lt;isbn&gt;/&lt;institution&gt/&lt;start_year&gt/&lt;end_year&gt;</p>
    <p>institution start_year and end_year are optional</p>

    Example tool:
    http://127.0.0.1:3000/static/index.html

    <p>Available institutions:</p>
    <ul>"""

    for inst in RECOMMENDER.get_institutions():
        out = out + '<li>{0}: {1}</li>'.format(inst[0], inst[1])

    out = out + """</ul></body></html>"""
    return out

@APP.route("/splurge_service_getinstitutions/", )
def splurge_service_getinstitutions():
    "Lists the institutions"
    return jsonify(institutions=RECOMMENDER.get_institutions())

@APP.route("/splurge_service/<isbn>/", defaults={
    'institution_names': None, 'start_year': None, 'end_year': None
})
@APP.route(
    "/splurge_service/<isbn>/<institution_names>/"
    "<start_year>/<end_year>/",
)
def splurge_service(isbn=None, institution_names=None,
    start_year=None, end_year=None
):
    "Main recommendation service"
    institutions = []
    if institution_names:
        for name in institution_names.split(","):
            institutions.append(RECOMMENDER.get_inst_id(name.strip()))

    filtr = splurge.create_transaction_filter(institutions)
    if isbn == None or isbn == 'random':
        isbn = RECOMMENDER.random_isbn(filtr)
    records = RECOMMENDER.recommend(isbn, filtr)
    return jsonify(isbn=isbn, institution_names=institution_names,
        institution_ids=institutions, start_year=start_year, end_year=end_year,
        results=records
    )

if __name__ == "__main__":
    APP.run('0.0.0.0', APP.config['SERVER_PORT'])
